# neumatic\data_load\vincular_factura_caja.py
import os
import sys
import django
import time
import logging
from django.db import transaction

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.ventas.models.caja_models import CajaDetalle, Caja
from apps.ventas.models.factura_models import Factura

# Configuración de logging
logging.basicConfig(
    filename='vincular_factura_caja.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def vincular_facturas_con_cajas():
    """Actualiza el campo id_caja en Factura usando datos de CajaDetalle"""
    try:
        start_time = time.time()
        print("Iniciando vinculación de Facturas con Cajas desde CajaDetalle...")

        # Obtener registros relevantes: solo con idventas > 0
        caja_detalles = CajaDetalle.objects.filter(idventas__gt=0).only('pk', 'idventas', 'id_caja_id')
        total_registros = caja_detalles.count()
        print(f"Registros de CajaDetalle con idventas > 0: {total_registros}")

        if total_registros == 0:
            print("No hay registros con idventas > 0. Nada que procesar.")
            return

        # Contadores
        actualizados = 0
        no_encontrados = 0
        errores = 0
        batch_size = 2000
        facturas_a_actualizar = []

        for idx, detalle in enumerate(caja_detalles, 1):
            try:
                id_venta = detalle.idventas
                id_caja_db = detalle.id_caja_id

                if not id_caja_db:
                    mensaje = f"id_caja_detalle={detalle.pk}, idventa={id_venta}, id_caja=None"
                    print(f"Caja nula: {mensaje}")
                    logger.warning(mensaje)
                    continue

                # ✅ INSTANCIAR EXPLÍCITAMENTE EL OBJETO CAJA
                try:
                    caja_instancia = Caja.objects.get(pk=id_caja_db)
                except Caja.DoesNotExist:
                    mensaje = f"id_caja_detalle={detalle.pk}, idventa={id_venta}, id_caja={id_caja_db} | Caja no existe"
                    print(f"Error: {mensaje}")
                    logger.error(mensaje)
                    errores += 1
                    continue

                # ✅ CORREGIDO: usar 'id_factura' en lugar de 'id_venta'
                try:
                    factura = Factura.objects.get(id_factura=id_venta)
                except Factura.DoesNotExist:
                    no_encontrados += 1
                    mensaje = f"id_caja_detalle={detalle.pk}, idventa={id_venta}, id_caja={id_caja_db}"
                    print(f"Factura no encontrada: {mensaje}")
                    logger.warning(mensaje)
                    continue

                # Asignar la instancia de caja
                factura.id_caja = caja_instancia
                facturas_a_actualizar.append(factura)

                # Guardar por lotes
                if len(facturas_a_actualizar) >= batch_size:
                    with transaction.atomic():
                        Factura.objects.bulk_update(facturas_a_actualizar, ['id_caja'])
                        actualizados += len(facturas_a_actualizar)
                        print(f"Lote guardado: {len(facturas_a_actualizar)} facturas actualizadas")
                        facturas_a_actualizar = []

                if idx % 2000 == 0:
                    print(f"Procesados: {idx}/{total_registros}")

            except Exception as e:
                errores += 1
                mensaje_error = f"id_caja_detalle={detalle.pk}, idventa={detalle.idventas}, id_caja={detalle.id_caja_id} | Error: {str(e)}"
                print(f"Error: {mensaje_error}")
                logger.error(mensaje_error)
                continue

        # Guardar último lote
        if facturas_a_actualizar:
            with transaction.atomic():
                Factura.objects.bulk_update(facturas_a_actualizar, ['id_caja'])
                actualizados += len(facturas_a_actualizar)
                print(f"Último lote guardado: {len(facturas_a_actualizar)} facturas actualizadas")

        # Resumen final
        elapsed_time = time.time() - start_time
        print("\n=== RESUMEN FINAL ===")
        print(f"Total CajaDetalle procesados (idventas > 0): {total_registros}")
        print(f"Facturas actualizadas: {actualizados}")
        print(f"Facturas no encontradas: {no_encontrados}")
        print(f"Errores: {errores}")
        print(f"Tiempo total: {elapsed_time:.2f} segundos")

        logger.info("=== RESUMEN FINAL ===")
        logger.info(f"Facturas actualizadas: {actualizados}")
        logger.info(f"Facturas no encontradas: {no_encontrados}")
        logger.info(f"Errores: {errores}")

    except Exception as e:
        mensaje_fatal = f"ERROR FATAL: {str(e)}"
        print(mensaje_fatal)
        logger.critical(mensaje_fatal)
        raise

if __name__ == '__main__':
    vincular_facturas_con_cajas()