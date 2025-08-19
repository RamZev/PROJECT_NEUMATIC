# neumatic\data_load\concepto_banco_migra.py
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

from apps.maestros.models.base_models import ConceptoBanco

def reset_concepto_banco():
    """Elimina los datos existentes en la tabla ConceptoBanco y resetea su ID en SQLite."""
    ConceptoBanco.objects.all().delete()
    print("Tabla ConceptoBanco limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='concepto_banco';")
    
    print("Secuencia de ID reseteada.")

def cargar_conceptos_desde_json(ruta_json):
    """Carga los conceptos bancarios desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        conceptos = json.load(file)

    for item in conceptos:
        try:
            ConceptoBanco.objects.create(
                estatus_concepto_banco=bool(item.get("estatus_concepto_banco", True)),
                nombre_concepto_banco=item["nombre_concepto_banco"],
                factor=int(item["factor"])
            )
        except ValidationError as e:
            print(f"Error validando concepto {item.get('nombre_concepto_banco')}: {e}")
        except Exception as e:
            print(f"Error creando concepto {item.get('nombre_concepto_banco')}: {e}")

    print(f"Se han migrado {ConceptoBanco.objects.count()} conceptos bancarios.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'concepto_banco.json')

    reset_concepto_banco()
    cargar_conceptos_desde_json(ruta_json)