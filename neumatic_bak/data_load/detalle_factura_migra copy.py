import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF
from django.db import connection
from decimal import Decimal

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from neumatic.apps.ventas.models.factura_models import Factura, DetalleFactura
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import Operario

def reset_detalle_factura():
    """Elimina los datos existentes en la tabla DetalleFactura y resetea su ID en SQLite."""
    # DetalleFactura.objects.all().delete()
    with connection.cursor() as cursor:
        pass
        #cursor.execute("DELETE FROM sqlite_sequence WHERE name='detalle_factura';")
        #print("Eliminada la secuencia")

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
    codigo_inicio = 1498294
    
    # table = [record for record in table if int(record['ID']) >= codigo_inicio]
    table = sorted(
        [record for record in table if int(record['ID']) >= codigo_inicio],
        key=lambda record: int(record['ID'])
    )

    print("Inicio del ciclo for")

    for idx, record in enumerate(table):
        # Obtener el código de la tabla origen
        codigo_origen = int(record.get('ID', 0))
        
        # Obtener instancias relacionadas
        try:
            id_factura_instancia = Factura.objects.get(pk=codigo_origen)
        except (Factura.DoesNotExist, ValueError):
            id_factura_instancia = None
            
        # Obtener instancia predeterminada para id_operario
        operario_id = record.get('OPERARIO', None)
        try:
            id_operario_instancia = Operario.objects.get(pk=operario_id)
        except (Operario.DoesNotExist, ValueError):
            id_operario_instancia = None

        ##########################
        codigo_producto = record.get('CODIGO', None)

        if codigo_producto is not None:
            try:
                # Verificamos si el producto existe
                id_producto_instancia = Producto.objects.get(codigo_producto=codigo_producto)
            except Producto.DoesNotExist:
                # Si no se encuentra, lo registramos para depuración
                id_producto_instancia = None
                print(f"Producto con código {codigo_producto} no encontrado en la base de datos.")
        else:
            id_producto_instancia = None
            print(f"Código de producto inválido: {record['CODIGO']}")
        ##########################

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

        # Mostrar mensaje cada 1000 registros procesados
        if (idx + 1) % 1000 == 0:
            print(f"{idx + 1} registros procesados...")

    print("Todos los registros se han procesado correctamente.")

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
