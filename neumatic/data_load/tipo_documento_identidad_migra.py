import json
import os
import sys
import django
from django.db import connection

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import TipoDocumentoIdentidad  

def reset_tipo_documento_identidad():
    """Elimina los datos existentes en la tabla TipoDocumentoIdentidad y resetea su ID en SQLite."""
    # Eliminar los datos existentes en la tabla
    TipoDocumentoIdentidad.objects.all().delete()
    print("Tabla TipoDocumentoIdentidad limpiada.")

    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tipo_documento_identidad';") 
        
    print("Secuencia de ID reseteada.")

def cargar_tipo_documento_identidad_desde_json(ruta_json):
    """Carga los tipos de documento de identidad desde un archivo JSON y los guarda en la base de datos."""
    # Abrir y cargar el archivo JSON
    with open(ruta_json, 'r', encoding='utf-8') as file:
        tipos_documento_identidad = json.load(file)

    # Recorrer los elementos del JSON y migrar cada uno
    for item in tipos_documento_identidad:
        nombre_documento_identidad = item["nombre_documento_identidad"]
        tipo_documento_identidad = item["tipo_documento_identidad"]
        codigo_afip = item["codigo_afip"]
        ws_afip = item["ws_afip"]


        # Crear o actualizar el registro en la base de datos
        TipoDocumentoIdentidad.objects.create(
            estatus_tipo_documento_identidad=True,
            nombre_documento_identidad=nombre_documento_identidad,
            tipo_documento_identidad=tipo_documento_identidad,
            codigo_afip=codigo_afip,
            ws_afip=ws_afip
        )

    print(f"Se han migrado {len(tipos_documento_identidad)} tipos de documento de identidad de forma exitosa.")

if __name__ == '__main__':
    # Ruta al archivo tipo_documento_identidad.json
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'tipo_documento_identidad.json')

    # Resetear la tabla TipoDocumentoIdentidad antes de la migración
    reset_tipo_documento_identidad()

    # Ejecutar la migración
    cargar_tipo_documento_identidad_desde_json(ruta_json)
