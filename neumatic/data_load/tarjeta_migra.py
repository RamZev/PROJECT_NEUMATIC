# neumatic\data_load\tarjeta_migra.py
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

from apps.maestros.models.base_models import Tarjeta

def reset_tarjeta():
    """Elimina los datos existentes en la tabla Tarjeta y resetea su ID en SQLite."""
    Tarjeta.objects.all().delete()
    print("Tabla Tarjeta limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tarjeta';")
    
    print("Secuencia de ID reseteada.")

def cargar_tarjetas_desde_json(ruta_json):
    """Carga las tarjetas desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        tarjetas = json.load(file)

    for item in tarjetas:
        Tarjeta.objects.create(
            estatus_tarjeta=bool(item.get("estatus_tarjeta", True)),
            nombre_tarjeta=item["nombre_tarjeta"],
            imputacion=item["imputacion"] if item["imputacion"] else None,
            banco_acreditacion=item["banco_acreditacion"] if item["banco_acreditacion"] else None,
            propia=bool(item.get("propia", False))
        )

    print(f"Se han migrado {len(tarjetas)} tarjetas.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'tarjeta.json')

    reset_tarjeta()
    cargar_tarjetas_desde_json(ruta_json)