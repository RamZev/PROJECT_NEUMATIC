import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF
from django.db import connection
from decimal import Decimal
from django.db import transaction

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.ventas.models.factura_models import Factura, DetalleFactura
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import Operario

def reset_detalle_factura():
    """Elimina los datos existentes en la tabla DetalleFactura y resetea su ID en SQLite."""
    DetalleFactura.objects.all().delete()  # Eliminar los datos existentes
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='detalle_factura';")
    print("Tabla DetalleFactura reiniciada.")

def cargar_datos_detalle_factura():
    """Lee los datos de la tabla origen y migra los datos al modelo DetalleFactura."""
    reset_detalle_factura()

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'detven.DBF')

    # Abrir la tabla de Visual FoxPro usando dbfread
    table = DBF(dbf_path, encoding='latin-1')

    total_registros = len(table)
    print(f"Total de registros a procesar: {total_registros}")

    # Código inicial para filtrar
    codigo_inicio = 1

    # Filtrar y ordenar los registros
    table = sorted(
        [record for record in table if int(record['ID']) >= codigo_inicio],
        key=lambda record: int(record['ID'])
    )

    print("Inicio del ciclo de migración.")

    registros_procesados = 0
    for idx, record in enumerate(table):
        try:
            # Obtener el código de la tabla origen
            codigo_origen = int(record.get('ID', 0))

            # Obtener instancias relacionadas
            id_factura_instancia = Factura.objects.filter(pk=codigo_origen).first()
            operario_id = record.get('OPERARIO', None)
            id_operario_instancia = Operario.objects.filter(pk=operario_id).first() if operario_id else None
            codigo_producto = record.get('CODIGO', None)
            id_producto_instancia = Producto.objects.filter(codigo_producto=codigo_producto).first() if codigo_producto else None

            if not id_factura_instancia:
                print(f"Advertencia: Factura con ID {codigo_origen} no encontrada. Registro omitido.")
                continue

            if not id_producto_instancia:
                print(f"Advertencia: Producto con código {codigo_producto} no encontrado. Registro omitido.")
                continue

            # Crear el registro de DetalleFactura
            DetalleFactura.objects.create(
                id_factura=id_factura_instancia,
                id_producto=id_producto_instancia,
                codigo=int(record.get('CODIGO', 0)),  # Convierte a entero
                cantidad=Decimal(record.get('CANTIDAD', 0) or 0),
                costo=Decimal(record.get('COSTO', 0) or 0),
                precio=Decimal(record.get('PRECIO', 0) or 0),
                descuento=Decimal(record.get('DESCUENTO', 0) or 0),
                gravado=Decimal(record.get('GRAVADO', 0) or 0),
                alic_iva=Decimal(record.get('ALICIVA', 0) or 0),
                iva=Decimal(record.get('IVA', 0) or 0),
                total=Decimal(record.get('TOTAL', 0) or 0),
                reventa=record.get('REVENTA', '').strip(),
                stock=Decimal(record.get('STOCK', 0) or 0),
                act_stock=bool(record.get('ACTSTOCK', False)),
                id_operario=id_operario_instancia
            )

            registros_procesados += 1

            # Mostrar progreso cada 100 registros
            if registros_procesados % 100 == 0:
                print(f"{registros_procesados} registros procesados.")

        except Exception as e:
            print(f"Error procesando el registro ID {record.get('ID', 'N/A')}: {e}")

    print(f"Total de registros procesados: {registros_procesados}")

if __name__ == '__main__':
    start_time = time.time()  # Empezar el control de tiempo
    cargar_datos_detalle_factura()
    end_time = time.time()  # Terminar el control de tiempo

    # Calcular el tiempo total en minutos y segundos
    elapsed_time = end_time - start_time
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    print("Migración de DetalleFactura completada.")
    print(f"Tiempo de procesamiento: {int(minutes)} minutos y {int(seconds)} segundos.")
