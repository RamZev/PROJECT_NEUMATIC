# neumatic\data_load\stockcliente_migra.py
import os
import sys
import django
import time
from dbfread import DBF
from django.db import transaction
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.producto_models import Producto
from apps.ventas.models.factura_models import Factura
from apps.ventas.models.venta_models import StockCliente

def reset_stockcliente():
    """Elimina los datos existentes en la tabla StockCliente y resetea su ID en SQLite."""
    StockCliente.objects.all().delete()
    print("Tabla StockCliente limpiada.")
    
    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='stock_cliente';")
    print("Secuencia de ID reseteada.")

def cargar_datos():
    """Migra datos desde stockcliente.DBF al modelo StockCliente"""
    reset_stockcliente()
    
    # Ruta del archivo DBF
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'stockcliente.DBF')
    
    # Abrir tabla y preparar datos
    table = DBF(dbf_path, encoding='latin-1')
    total_records = len(table)
    batch_size = 2000
    processed = 0
    missing_facturas = 0
    missing_productos = 0
    other_errors = 0
    
    print(f"Iniciando migración de {total_records} registros...")
    start_time = time.time()
    
    # Procesar por lotes
    batch = []
    for i, record in enumerate(table, 1):
        try:
            # Obtener instancias de modelos relacionados con validación explícita
            try:
                factura = Factura.objects.get(id_factura=record['id_factura'])
            except ObjectDoesNotExist:
                print(f"Registro {i}: Factura no encontrada (ID: {record['id_factura']})")
                missing_facturas += 1
                continue
                
            try:
                producto = Producto.objects.get(id_producto=record['id_producto'])
            except ObjectDoesNotExist:
                print(f"Registro {i}: Producto no encontrado (ID: {record['id_producto']})")
                missing_productos += 1
                continue
            
            # Crear objeto StockCliente
            stock_cliente = StockCliente(
                id_factura=factura,
                id_producto=producto,
                cantidad=record['cantidad'],
                retiro=record['retiro'],
                fecha_retiro=record['fecha_retiro'],
                numero=record['numero'],
                comentario=record['comentario']
            )
            batch.append(stock_cliente)
            
            # Procesar lote completo
            if len(batch) >= batch_size or i == total_records:
                with transaction.atomic():
                    StockCliente.objects.bulk_create(batch)
                processed += len(batch)
                batch = []
                elapsed = time.time() - start_time
                print(f"Procesados {processed}/{total_records} registros. Tiempo: {elapsed:.2f}s")
                
        except Exception as e:
            print(f"Error inesperado en registro {i}: {str(e)}")
            other_errors += 1
            continue
    
    # Estadísticas finales mejoradas
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"Migración completada. Total registros procesados: {processed}")
    print(f"Registros con Factura faltante: {missing_facturas}")
    print(f"Registros con Producto faltante: {missing_productos}")
    print(f"Otros errores: {other_errors}")
    print(f"Tiempo total: {total_time:.2f} segundos")
    print(f"Registros por segundo: {processed/total_time:.2f}")
    print("="*50)

if __name__ == '__main__':
    cargar_datos()

