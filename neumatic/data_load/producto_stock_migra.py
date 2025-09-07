# neumatic\data_load\producto_stock_migra.py
import os
import sys
import django
import time
from dbfread import DBF
from django.db import connection
from datetime import date
from django.db import transaction

# Configuración del entorno Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

# Importación de los modelos
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import ProductoStock, ProductoDeposito

def reset_producto_stock():
    """Elimina todos los registros de ProductoStock y resetea la secuencia"""
    with transaction.atomic():
        # Eliminar todos los registros
        deleted_count = ProductoStock.objects.all().delete()[0]
        print(f"Eliminados {deleted_count} registros existentes de ProductoStock")
        
        # Resetear secuencia para SQLite
        if 'sqlite' in connection.settings_dict['ENGINE']:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='producto_stock';")
            print("Secuencia de ID reseteada para SQLite")

def migrar_producto_stock():
    """Migra datos desde el DBF a la tabla ProductoStock"""
    # Configuración de rutas y archivo
    tabla_origen = 'stock.DBF'
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', tabla_origen)
    
    try:
        # Leer y ordenar el archivo DBF
        table = sorted(DBF(dbf_path, encoding='latin-1'), 
                     key=lambda r: (r['CODIGO'] or 0, r['DEPOSITO'] or 0))
        total_registros = len(table)
        print(f"\n{tabla_origen}: Total de registros a procesar: {total_registros}")
        
        # Variables para el procesamiento
        batch_size = 2000
        bulk_data = []
        registros_creados = 0
        errores = 0
        inicio = time.time()

        # Procesar cada registro
        for idx, record in enumerate(table, 1):
            try:
                codigo = int(record.get('CODIGO', 0))
                deposito = int(record.get('DEPOSITO', 0))
                
                # Validar relaciones
                producto = Producto.objects.filter(id_producto=codigo).first()
                deposito_obj = ProductoDeposito.objects.filter(id_producto_deposito=deposito).first()
                
                if not producto or not deposito_obj:
                    print(f"Registro {idx} Código ({codigo}) o Depósito ({deposito}) no encontrados")
                    errores += 1
                    continue
                
                # Crear instancia para bulk_create
                bulk_data.append(ProductoStock(
                    id_producto=producto,
                    id_deposito=deposito_obj,
                    stock=record.get('STOCK', 0) or 0,
                    minimo=record.get('MINIMO', 0) or 0,
                    fecha_producto_stock=record.get('FECHA', date.today()) or date.today()
                ))
                
                # Insertar por lotes
                if len(bulk_data) >= batch_size:
                    with transaction.atomic():
                        ProductoStock.objects.bulk_create(bulk_data)
                    registros_creados += len(bulk_data)
                    bulk_data.clear()
                    print(f"Procesados {registros_creados} registros...")
                    
            except Exception as e:
                print(f"Registro {idx} Código {codigo} - : Error - {str(e)}")
                errores += 1
                continue
        
        # Insertar los registros restantes
        if bulk_data:
            with transaction.atomic():
                ProductoStock.objects.bulk_create(bulk_data)
            registros_creados += len(bulk_data)
        
        # Resultados finales
        tiempo_total = time.time() - inicio
        print(f"\nMigración completada en {tiempo_total:.2f} segundos")
        print(f"Total registros creados: {registros_creados}")
        print(f"Total errores: {errores}")
        print(f"Eficiencia: {(registros_creados/total_registros)*100:.2f}%")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {dbf_path}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == '__main__':
    # Paso 1: Resetear la tabla
    reset_producto_stock()
    
    # Paso 2: Migrar los datos
    migrar_producto_stock()