# neumatic\data_load\comprobante_venta_migra.py
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

from apps.maestros.models.base_models import ComprobanteVenta

def reset_comprobante_venta():
    """Elimina los datos existentes en la tabla ComprobanteVenta y resetea su ID en SQLite."""
    ComprobanteVenta.objects.all().delete()
    print("Tabla ComprobanteVenta limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='comprobante_venta';")
    
    print("Secuencia de ID reseteada.")

def cargar_comprobantes_desde_json(ruta_json):
    """Carga los comprobantes de venta desde un archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        comprobantes = json.load(file)

    for item in comprobantes:
        try:
            ComprobanteVenta.objects.create(
                usuario="admin",
                estatus_comprobante_venta=bool(item.get("estatus_comprobante_venta", True)),
                codigo_comprobante_venta=item.get("codigo_comprobante_venta", ""),
                nombre_comprobante_venta=item.get("nombre_comprobante_venta", ""),
                tipo_comprobante=item.get("tipo_comprobante"),
                compro_asociado=item.get("compro_asociado"),
                mult_venta=int(item.get("mult_venta", 0)),
                mult_saldo=int(item.get("mult_saldo", 0)),
                mult_stock=int(item.get("mult_stock", 0)),
                mult_comision=int(item.get("mult_comision", 0)),
                mult_caja=int(item.get("mult_caja", 0)),
                mult_estadistica=int(item.get("mult_estadistica", 0)),
                libro_iva=bool(item.get("libro_iva", False)),
                estadistica=bool(item.get("estadistica", False)),
                electronica=bool(item.get("electronica", False)),
                presupuesto=bool(item.get("presupuesto", False)),
                pendiente=bool(item.get("pendiente", False)),
                info_michelin_auto=bool(item.get("info_michelin_auto", False)),
                info_michelin_camion=bool(item.get("info_michelin_camion", False)),
                codigo_afip_a=item.get("codigo_afip_a", ""),
                codigo_afip_b=item.get("codigo_afip_b", ""),
                remito=bool(item.get("remito", False)),
                recibo=bool(item.get("recibo", False)),
                ncr_ndb=bool(item.get("ncr_ndb", False)),
                manual=bool(item.get("manual", False)),
                mipyme=bool(item.get("mipyme", False)),
                interno=bool(item.get("interno", False))
            )
        except ValidationError as e:
            print(f"Error validando comprobante {item.get('nombre_comprobante_venta', 'Desconocido')}: {e}")
        except Exception as e:
            print(f"Error creando comprobante {item.get('nombre_comprobante_venta', 'Desconocido')}: {e}")

    print(f"Se han migrado {ComprobanteVenta.objects.count()} comprobantes de venta.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'comprobante_venta.json')
    reset_comprobante_venta()
    cargar_comprobantes_desde_json(ruta_json)