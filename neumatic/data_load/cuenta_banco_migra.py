# neumatic\data_load\cuenta_banco_migra.py
import json
import os
import sys
import django
from django.db import connection
from decimal import Decimal

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import CuentaBanco, Banco, Moneda

def reset_cuenta_banco():
    """Elimina los datos existentes en la tabla CuentaBanco y resetea su ID en SQLite."""
    CuentaBanco.objects.all().delete()
    print("Tabla CuentaBanco limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cuenta_banco';")
    
    print("Secuencia de ID reseteada.")

def cargar_cuentas_desde_json(ruta_json):
    """Carga las cuentas bancarias desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        cuentas = json.load(file)

    cuentas_creadas = 0
    errores = 0

    for item in cuentas:
        try:
            # Obtener las instancias de los modelos relacionados
            banco = Banco.objects.filter(pk=item["id_banco_id"]).first()
            moneda = Moneda.objects.filter(pk=item["id_moneda_id"]).first()

            if not banco:
                print(f"Advertencia: No existe banco con ID {item['id_banco_id']}")
                errores += 1
                continue
                
            if not moneda:
                print(f"Advertencia: No existe moneda con ID {item['id_moneda_id']}")
                errores += 1
                continue

            CuentaBanco.objects.create(
                estatus_cuenta_banco=bool(item.get("estatus_cuenta_banco", True)),
                id_banco=banco,
                numero_cuenta=item["numero_cuenta"],
                tipo_cuenta=item["tipo_cuenta"],
                cbu=item["cbu"] if item["cbu"] else None,
                sucursal=item["sucursal"] if item["sucursal"] else None,
                codigo_postal=item["codigo_postal"] if item["codigo_postal"] else None,
                codigo_imputacion=item["codigo_imputacion"] if item["codigo_imputacion"] else None,
                tope_negociacion=Decimal(str(item.get("tope_negociacion", 0))),
                reporte_reques=item["reporte_reques"] if item["reporte_reques"] else None,
                id_moneda=moneda
            )
            cuentas_creadas += 1
            
        except Exception as e:
            print(f"Error creando cuenta: {str(e)}")
            errores += 1

    print(f"\nResumen:")
    print(f"Cuentas creadas: {cuentas_creadas}")
    print(f"Errores: {errores}")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'cuenta_banco.json')

    reset_cuenta_banco()
    cargar_cuentas_desde_json(ruta_json)