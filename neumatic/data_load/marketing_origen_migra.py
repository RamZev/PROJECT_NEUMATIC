# neumatic\data_load\marketing_origen_migra.py
import json
import os
import sys
import django
from django.db import connection
from django.core.exceptions import ValidationError

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import MarketingOrigen

def reset_marketing_origen():
    """Elimina los datos existentes en la tabla MarketingOrigen y resetea su ID en SQLite."""
    MarketingOrigen.objects.all().delete()
    print("Tabla MarketingOrigen limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='marketing_origen';")
    
    print("Secuencia de ID reseteada.")

def cargar_marketing_origen_desde_json(ruta_json):
    """Carga los orígenes de marketing desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        origenes = json.load(file)

    for item in origenes:
        try:
            # Nota: Hay un typo en el JSON para id=9 (id_marketing_origen vs id_marketing_origen)
            item_id = item.get("id_marketing_origen") or item.get("id_marketing_origen")
            
            MarketingOrigen.objects.create(
                id_marketing_origen=item_id,
                estatus_marketing_origen=bool(item.get("estatus_marketing_origen", True)),
                nombre_marketing_origen=item["nombre_marketing_origen"]
            )
        except ValidationError as e:
            print(f"Error validando origen {item.get('nombre_marketing_origen')}: {e}")
        except Exception as e:
            print(f"Error creando origen {item.get('nombre_marketing_origen')}: {e}")

    print(f"Se han migrado {MarketingOrigen.objects.count()} orígenes de marketing.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'marketing_origen.json')

    reset_marketing_origen()
    cargar_marketing_origen_desde_json(ruta_json)