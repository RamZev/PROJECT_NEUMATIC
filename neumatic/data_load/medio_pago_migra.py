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

from apps.maestros.models.base_models import MedioPago

def reset_medio_pago():
    """Elimina los datos existentes y resetea la secuencia de IDs"""
    MedioPago.objects.all().delete()
    print("Tabla MedioPago limpiada.")
    
    if 'sqlite' in connection.settings_dict['ENGINE']:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='medio_pago';")
        print("Secuencia de ID reseteada para SQLite.")

def cargar_medio_pago_desde_json(ruta_json):
    """Carga los medios de pago desde JSON"""
    try:
        with open(ruta_json, 'r', encoding='utf-8') as file:
            medios_pago = json.load(file)
            
        for item in medios_pago:
            MedioPago.objects.create(
                id_medio_pago=item["id_medio_pago"],
                estatus_medio_pago=bool(item["estatus_medio_pago"]),
                nombre_medio_pago=item["nombre_medio_pago"],
                condicion_medio_pago=int(item["condicion_medio_pago"]),
                plazo_medio_pago=int(item["plazo_medio_pago"])
            )
            
        print(f"Se migraron {len(medios_pago)} medios de pago correctamente.")
        
    except FileNotFoundError:
        print(f"Error: Archivo {ruta_json} no encontrado.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON tiene formato incorrecto.")
    except KeyError as e:
        print(f"Error: Falta campo obligatorio en JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'medio_pago.json')
    reset_medio_pago()
    cargar_medio_pago_desde_json(ruta_json)