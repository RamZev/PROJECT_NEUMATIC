# neumatic\data_load\codigo_retencion_migra.py
import json
import os
import sys
import django
from django.db import connection

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import CodigoRetencion

def reset_codigo_retencion():
    """Elimina los datos existentes en la tabla CodigoRetencion y resetea su ID en SQLite."""
    CodigoRetencion.objects.all().delete()
    print("Tabla CodigoRetencion limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='codigo_retencion';")
    
    print("Secuencia de ID reseteada.")

def cargar_codigos_retencion_desde_json(ruta_json):
    """Carga los códigos de retención desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        codigos = json.load(file)

    for item in codigos:
        CodigoRetencion.objects.create(
            estatus_cod_retencion=bool(item.get("estatus_cod_retencion", True)),
            nombre_codigo_retencion=item["nombre_codigo_retencion"],
            imputacion=item["imputacion"] if item["imputacion"] is not None else 0
        )

    print(f"Se han migrado {len(codigos)} códigos de retención.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'codigo_retencion.json')

    reset_codigo_retencion()
    cargar_codigos_retencion_desde_json(ruta_json)