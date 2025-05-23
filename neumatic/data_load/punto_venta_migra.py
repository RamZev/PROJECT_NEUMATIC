import json
import os
import sys
import django
import re
from django.db import connection
from django.core.exceptions import ValidationError

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import PuntoVenta

def reset_punto_venta():
    """Elimina los datos existentes en la tabla PuntoVenta y resetea su ID en SQLite."""
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys=OFF;")
        
    PuntoVenta.objects.all().delete()
    print("Tabla PuntoVenta limpiada.")

    if 'sqlite' in connection.settings_dict['ENGINE']:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='punto_venta';")
        print("Secuencia de ID reseteada para SQLite.")
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys=ON;")

def validar_punto_venta(numero):
    """Valida y formatea el número de punto de venta según las reglas del modelo."""
    try:
        # Convertir a entero y luego a string con ceros a la izquierda
        return str(int(numero)).zfill(5)
    except (ValueError, TypeError):
        raise ValidationError("El punto de venta debe ser un número entero positivo")

def cargar_punto_venta_desde_json(ruta_json):
    """Carga los puntos de venta desde un archivo JSON con validación."""
    try:
        with open(ruta_json, 'r', encoding='utf-8') as file:
            puntos_venta = json.load(file)

        registros_procesados = 0
        errores = 0

        for item in puntos_venta:
            try:
                # Validar y formatear el punto de venta
                punto_venta_formateado = validar_punto_venta(item["punto_venta"])
                
                # Crear el registro manteniendo el ID explícito
                PuntoVenta.objects.create(
                    id_punto_venta=item["id_punto_venta"],
                    estatus_punto_venta=bool(item["estatus_punto_venta"]),
                    id_sucursal_id=item["id_sucursal_id"],
                    punto_venta=punto_venta_formateado,
                    descripcion_punto_venta=item["descripcion_punto_venta"]
                )
                registros_procesados += 1

            except ValidationError as e:
                print(f"Error de validación en registro {item['id_punto_venta']}: {e}")
                errores += 1
            except KeyError as e:
                print(f"Campo faltante en registro {item['id_punto_venta']}: {e}")
                errores += 1
            except Exception as e:
                print(f"Error inesperado en registro {item['id_punto_venta']}: {e}")
                errores += 1

        print(f"\nResumen de migración:")
        print(f"Registros procesados: {registros_procesados}")
        print(f"Errores: {errores}")
        print(f"Total en JSON: {len(puntos_venta)}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_json}")
    except json.JSONDecodeError:
        print("Error: El archivo JSON está mal formado")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'punto_venta.json')
    
    # Paso 1: Resetear la tabla
    reset_punto_venta()
    
    # Paso 2: Cargar los datos
    cargar_punto_venta_desde_json(ruta_json)