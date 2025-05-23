import json
import os
import sys
import django
import re
from decimal import Decimal
from django.db import connection
from django.core.exceptions import ValidationError

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import TipoPercepcionIb

def reset_tipo_percepcion_ib():
    """Elimina los datos existentes y resetea la secuencia de IDs"""
    TipoPercepcionIb.objects.all().delete()
    print("Tabla TipoPercepcionIb limpiada.")
    
    if 'sqlite' in connection.settings_dict['ENGINE']:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tipo_percepcion_ib';")
        print("Secuencia de ID reseteada para SQLite.")

def validar_decimal(valor, campo, max_enteros, max_decimales=2):
    """Valida campos decimales según las reglas del modelo"""
    if valor is None:
        return None
        
    valor_str = str(valor)
    patron = rf'^(0|[1-9]\d{{0,{max_enteros-1}}})(\.\d{{1,{max_decimales}}})?$'
    
    if not re.match(patron, valor_str):
        raise ValidationError(
            f"{campo}: El valor debe ser positivo, con hasta {max_enteros} " +
            f"dígitos enteros y hasta {max_decimales} decimales o cero."
        )
    return Decimal(valor_str)

def cargar_tipo_percepcion_ib_desde_json(ruta_json):
    """Carga los tipos de percepción IB desde JSON"""
    try:
        with open(ruta_json, 'r', encoding='utf-8') as file:
            percepciones = json.load(file)
            
        for item in percepciones:
            try:
                # Validar campos decimales según las reglas del modelo
                alicuota = validar_decimal(item.get("alicuota"), "Alicuota", 4)
                monto = validar_decimal(item.get("monto"), "Monto", 13)
                minimo = validar_decimal(item.get("minimo"), "Mínimo", 13)
                
                TipoPercepcionIb.objects.create(
                    id_tipo_percepcion_ib=item["id_tipo_percepcion_ib"],
                    estatus_tipo_percepcion_ib=bool(item["estatus_tipo_percepcion_ib"]),
                    descripcion_tipo_percepcion_ib=item["descripcion_tipo_percepcion_ib"],
                    alicuota=alicuota,
                    monto=monto,
                    minimo=minimo,
                    neto_total=bool(item.get("neto_total", False))
                )
                
            except ValidationError as e:
                print(f"Error de validación en registro {item['id_tipo_percepcion_ib']}: {e}")
            except KeyError as e:
                print(f"Campo faltante en registro {item['id_tipo_percepcion_ib']}: {e}")
                
        print(f"Se migraron {len(percepciones)} percepciones IB correctamente.")
        
    except FileNotFoundError:
        print(f"Error: Archivo {ruta_json} no encontrado.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON tiene formato incorrecto.")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'tipo_percepcion_ib.json')
    reset_tipo_percepcion_ib()
    cargar_tipo_percepcion_ib_desde_json(ruta_json)