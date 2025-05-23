import json
import os
import sys
import django
from django.db import connection
from datetime import datetime

# Añadir el directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.empresa_models import Empresa
from apps.maestros.models.base_models import Localidad, Provincia, TipoIva

def reset_empresa():
    """Elimina los datos existentes en la tabla Empresa y reinicia la secuencia (solo para SQLite)."""
    Empresa.objects.all().delete()
    print("Tabla Empresa limpiada.")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='empresa';")

    print("Secuencia de ID reseteada.")

def parse_date(valor):
    """Convierte string a fecha o retorna None si es vacío o nulo."""
    if not valor:
        return None
    return datetime.strptime(valor, "%Y-%m-%d").date()

def cargar_empresa_desde_json(ruta_json):
    """Carga los datos del archivo JSON e inserta los registros en la tabla Empresa."""
    with open(ruta_json, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        try:
            Empresa.objects.create(
                id_empresa=item["id_empresa"],
                estatus_empresa=bool(item["estatus_empresa"]),
                nombre_fiscal=item["nombre_fiscal"],
                nombre_comercial=item["nombre_comercial"],
                domicilio_empresa=item["domicilio_empresa"],
                codigo_postal=item["codigo_postal"],
                cuit=item["cuit"],
                ingresos_bruto=item["ingresos_bruto"],
                inicio_actividad=parse_date(item["inicio_actividad"]),
                cbu=item["cbu"],
                cbu_alias=item["cbu_alias"],
                cbu_vence=parse_date(item["cbu_vence"]),
                telefono=item["telefono"],
                email_empresa=item["email_empresa"],
                web_empresa=item.get("web_empresa", ""),
                logo_empresa=b"",  # Si necesitas cargar binario, hazlo aparte.
                ws_archivo_crt=item["ws_archivo_crt"],
                ws_archivo_key=item["ws_archivo_key"],
                ws_token=item.get("ws_token", ""),
                ws_sign=item.get("ws_sign", ""),
                ws_expiracion=parse_date(item.get("ws_expiracion")),
                ws_modo=item["ws_modo"],
                ws_vence=parse_date(item["ws_vence"]),
                interes=item["interes"],
                interes_dolar=item["interes_dolar"],
                cotizacion_dolar=item["cotizacion_dolar"],
                dias_vencimiento=item["dias_vencimiento"],
                descuento_maximo=item["descuento_maximo"],
                id_localidad=Localidad.objects.get(pk=item["id_localidad_id"]),
                id_provincia=Provincia.objects.get(pk=item["id_provincia_id"]),
                id_iva=TipoIva.objects.get(pk=item["id_iva_id"]) if item.get("id_iva_id") else None,
            )
        except Exception as e:
            print(f"Error al cargar empresa ID {item['id_empresa']}: {e}")

    print(f"Se han migrado {len(data)} empresas con IDs explícitos.")

if __name__ == '__main__':
    ruta_json = os.path.join(BASE_DIR, 'data_load', 'empresa.json')

    reset_empresa()
    cargar_empresa_desde_json(ruta_json)
