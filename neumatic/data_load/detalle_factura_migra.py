# neumatic\data_load\detalle_factura_migra.py
import os
import sys
import django
import time
import logging
from dbfread import DBF
from django.db import connection
from decimal import Decimal
from django.db import transaction

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.ventas.models.factura_models import Factura, DetalleFactura
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import Operario

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migracion_detalle_factura.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_decimal(value, default=Decimal('0.00')):
    """Conversión segura a Decimal"""
    try:
        return Decimal(str(value)) if value is not None else default
    except:
        return default

def safe_int(value, default=0):
    """Conversión segura a entero con múltiples formatos"""
    try:
        if value is None:
            return default
            
        # Manejar casos donde el valor podría ser string con decimales ("180646.00")
        if isinstance(value, str):
            value = value.split('.')[0]  # Eliminar parte decimal si existe
            
        return int(float(value)) if str(value).strip() else default
    except:
        return default

def reset_detalle_factura():
    """Elimina los datos existentes en la tabla DetalleFactura"""
    try:
        with transaction.atomic():
            count = DetalleFactura.objects.count()
            DetalleFactura.objects.all().delete()
            logger.info(f"Eliminados {count} registros existentes")
            
            if 'sqlite' in connection.settings_dict['ENGINE']:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='detalle_factura';")
    except Exception as e:
        logger.error(f"Error al resetear tabla: {e}")
        raise

def cargar_datos_detalle_factura():
    """Proceso de migración optimizado con bulk_create"""
    start_time = time.time()
    reset_detalle_factura()

    # Configuración para mejor rendimiento en SQLite
    if 'sqlite' in connection.settings_dict['ENGINE']:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA synchronous = OFF;")
            cursor.execute("PRAGMA journal_mode = MEMORY;")
            cursor.execute("PRAGMA cache_size = 10000;")

    # Ruta del archivo DBF
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'detven.DBF')
    
    if not os.path.exists(dbf_path):
        logger.error(f"Archivo DBF no encontrado en: {dbf_path}")
        return

    try:
        table = DBF(dbf_path, encoding='latin-1')
    except UnicodeDecodeError:
        table = DBF(dbf_path, encoding='utf-8')

    logger.info(f"Iniciando migración. Total registros: {len(table)}")

    # Precargar productos asegurando el tipo de dato correcto
    logger.info("Cargando cache de productos...")
    productos_cache = {}
    
    for p in Producto.objects.all():
        try:
            key = int(float(str(p.codigo_producto).split('.')[0]))
            productos_cache[key] = p
        except Exception as e:
            logger.error(f"Error procesando código de producto {p.codigo_producto}: {e}")
            continue
    
    logger.info(f"Total productos cargados: {len(productos_cache)}")
    
    # Cargar otros caches
    facturas_cache = {f.pk: f for f in Factura.objects.all()}
    operarios_cache = {o.pk: o for o in Operario.objects.all()}

    # Configuración de procesamiento por lotes
    batch_size = 2000  # Tamaño óptimo para SQLite
    detalles_batch = []
    registros_procesados = 0
    productos_no_encontrados = set()

    for idx, record in enumerate(table, 1):
        try:
            codigo_origen = safe_int(record.get('ID'))
            if not codigo_origen:
                logger.warning(f"Registro {idx} sin ID válido")
                continue

            # Buscar factura
            id_factura_instancia = facturas_cache.get(codigo_origen)
            if not id_factura_instancia:
                logger.warning(f"Factura no encontrada ID: {codigo_origen}")
                continue

            # Obtener código de producto con conversión robusta
            codigo_producto_raw = record.get('CODIGO')
            codigo_producto = safe_int(codigo_producto_raw)
            
            # Buscar producto
            id_producto_instancia = productos_cache.get(codigo_producto)
            
            if not id_producto_instancia:
                productos_no_encontrados.add((codigo_producto, codigo_producto_raw))
                continue

            # Crear instancia (sin guardar aún)
            detalle = DetalleFactura(
                id_factura=id_factura_instancia,
                id_producto=id_producto_instancia,
                codigo=codigo_producto,
                producto_venta=id_producto_instancia.nombre_producto,  # Campo añadido
                cantidad=safe_decimal(record.get('CANTIDAD')),
                costo=safe_decimal(record.get('COSTO')),
                precio=safe_decimal(record.get('PRECIO')),
                precio_lista=id_producto_instancia.precio,  # Campo añadido
                descuento=safe_decimal(record.get('DESCUENTO')),
                gravado=safe_decimal(record.get('GRAVADO')),
                alic_iva=safe_decimal(record.get('ALICIVA')),
                iva=safe_decimal(record.get('IVA')),
                total=safe_decimal(record.get('TOTAL')),
                reventa=str(record.get('REVENTA', '')).strip()[:1],
                stock=safe_decimal(record.get('STOCK')),
                act_stock=bool(safe_int(record.get('ACTSTOCK', 0))),
                id_operario=operarios_cache.get(safe_int(record.get('OPERARIO')))
            )
            
            detalles_batch.append(detalle)
            registros_procesados += 1

            # Guardar por lotes
            if len(detalles_batch) >= batch_size:
                with transaction.atomic():
                    DetalleFactura.objects.bulk_create(detalles_batch)
                logger.info(f"Lote guardado: {len(detalles_batch)} registros")
                detalles_batch = []

            if registros_procesados % 10000 == 0:
                logger.info(f"Progreso: {registros_procesados} registros procesados")

        except Exception as e:
            logger.error(f"Error en registro {idx}: {str(e)}")
            continue

    # Guardar los últimos registros si los hay
    if detalles_batch:
        with transaction.atomic():
            DetalleFactura.objects.bulk_create(detalles_batch)
        logger.info(f"Último lote guardado: {len(detalles_batch)} registros")

    # Reporte final
    logger.info("\n=== REPORTE FINAL ===")
    logger.info(f"Total registros procesados: {registros_procesados}")
    
    if productos_no_encontrados:
        logger.warning(f"\nProductos no encontrados ({len(productos_no_encontrados)}):")
        for codigo, codigo_raw in sorted(productos_no_encontrados)[:100]:  # Mostrar solo los primeros 100
            logger.warning(f" - Código convertido: {codigo} | Valor original: {codigo_raw}")
            
            # Verificación adicional en BD para diagnóstico
            producto = Producto.objects.filter(
                codigo_producto=str(codigo)
            ).first()
            
            if producto:
                logger.error(f"   ¡INCONSISTENCIA! El producto existe en BD: ID {producto.id}, Código: {producto.codigo_producto}")

    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    logger.info(f"\nTiempo total: {int(mins)} minutos {int(secs)} segundos")

if __name__ == '__main__':
    cargar_datos_detalle_factura()