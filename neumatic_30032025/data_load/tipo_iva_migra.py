# neumatic\data_load\tipo_iva_migra.py
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

from apps.maestros.models.base_models import TipoIva

def reset_tipo_iva():
    """Elimina los datos existentes en la tabla TipoIva y resetea su ID en SQLite."""
    # Eliminar los datos existentes en la tabla
    TipoIva.objects.all().delete()
    print("Tabla TipoIva limpiada.")

    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tipo_iva';")  # Ajustar el nombre si es necesario
    print("Secuencia de ID reseteada.")

def cargar_tipo_iva_desde_json(ruta_json):
    """Carga los tipos de IVA desde un archivo JSON y los guarda en la base de datos."""
    # Abrir y cargar el archivo JSON
    with open(ruta_json, 'r', encoding='utf-8') as file:
        tipos_iva = json.load(file)

    # Recorrer los elementos del JSON y migrar cada uno
    for item in tipos_iva:
        codigo = item["codigo"]
        nombre = item["descripcion"]

        # Convertir la descripción a un valor numérico y eliminar el símbolo de porcentaje
        nombre_iva = nombre.replace(",", ".").replace(" %", "")

        # Crear o actualizar el registro en la base de datos
        TipoIva.objects.create(
            codigo_iva=codigo,
            estatus_tipo_iva=True,
            nombre_iva=nombre_iva,
            discrimina_iva=False
        )

    print(f"Se han migrado {len(tipos_iva)} tipos de IVA de forma exitosa.")

if __name__ == '__main__':
    # Ruta al archivo tipo_iva.json
    ruta_json = os.path.join(os.path.dirname(__file__), 'tipo_iva.json')

    # Resetear la tabla TipoIva antes de la migración
    reset_tipo_iva()

    # Ejecutar la migración
    cargar_tipo_iva_desde_json(ruta_json)
