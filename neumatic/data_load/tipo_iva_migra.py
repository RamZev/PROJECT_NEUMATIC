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
    TipoIva.objects.all().delete()
    print("Tabla TipoIva limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tipo_iva';")
    
    print("Secuencia de ID reseteada.")

def cargar_tipo_iva_desde_json(ruta_json):
    """Carga los tipos de IVA desde un archivo JSON y los guarda en la base de datos."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        tipos_iva = json.load(file)

    for item in tipos_iva:
        TipoIva.objects.create(
            id_tipo_iva=item["id_tipo_iva"],
            estatus_tipo_iva=bool(item["estatus_tipo_iva"]),
            codigo_iva=item["codigo_iva"],
            nombre_iva=item["nombre_iva"],
            discrimina_iva=bool(item["discrimina_iva"]),
            codigo_afip_responsable=item["codigo_afip_responsable"]
        )

    print(f"Se han migrado {len(tipos_iva)} tipos de IVA con sus ID explícitos.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'tipo_iva.json')

    reset_tipo_iva()
    cargar_tipo_iva_desde_json(ruta_json)
