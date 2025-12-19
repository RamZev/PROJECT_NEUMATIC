# neumatic\data_load\cajadetalle_migra.py
import os
import sys
import django
import time
import logging
from dbfread import DBF
from django.db import connection
from django.db import transaction
from datetime import date, datetime
from decimal import Decimal
from django.utils import timezone

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.ventas.models.caja_models import Caja, CajaDetalle
from apps.maestros.models.base_models import FormaPago

# Configuración de logging
logging.basicConfig(
    filename='cajadetalle_migra.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_int(value, default=0):
    """Conversión segura a entero"""
    try:
        return int(float(value)) if value is not None and str(value).strip() else default
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Conversión segura a float"""
    try:
        return float(value) if value is not None and str(value).strip() else default
    except (ValueError, TypeError):
        return default

def safe_decimal(value, default=0.0):
    """Conversión segura a Decimal"""
    try:
        if value is not None and str(value).strip():
            return Decimal(str(value))
        return Decimal(str(default))
    except (ValueError, TypeError):
        return Decimal(str(default))

def cargar_datos_cajadetalle():
    """Migración optimizada de cajadetalle.DBF a modelo CajaDetalle"""
    try:
        start_time = time.time()
        
        # NO resetear - solo agregar nuevos registros
        print("Iniciando migración de CajaDetalle (solo agregando nuevos)...")

        # Precargar caches para optimización
        print("Cargando cachés de relaciones...")
        
        # Cache de cajas por numero_caja
        cajas_cache = {}
        for caja in Caja.objects.all():
            if caja.numero_caja:
                cajas_cache[caja.numero_caja] = caja
        
        print(f"Cargadas {len(cajas_cache)} cajas en caché")
        
        # Cache de formas de pago
        formas_pago_cache = {fp.pk: fp for fp in FormaPago.objects.all()}
        print(f"Cargadas {len(formas_pago_cache)} formas de pago en caché")

        dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'cajadetalle.DBF')
        print(f"Procesando archivo: {dbf_path}")
        
        table = DBF(dbf_path, encoding='latin-1')
        total_records = len(table)
        print(f"Total de registros en DBF: {total_records}")
        
        # Procesamiento por lotes
        batch_size = 4000
        detalles_batch = []
        registros_procesados = 0
        total_regs = 0
        errores = 0
        cajas_no_encontradas = 0
        formas_pago_no_encontradas = 0
        duplicados = 0

        for idx, record in enumerate(table, 1):
            try:
                # ============================================
                # 1. OBTENER Y VALIDAR CAJA (RELACIÓN PRINCIPAL)
                # ============================================
                caja_numero = safe_int(record.get('CAJA'))
                
                if not caja_numero:
                    logger.warning(f"Registro {idx}: Campo CAJA vacío o inválido, omitiendo...")
                    continue
                
                # Buscar caja en el cache
                caja_obj = cajas_cache.get(caja_numero)
                
                if not caja_obj:
                    cajas_no_encontradas += 1
                    logger.warning(f"Registro {idx}: Caja número {caja_numero} no encontrada en sistema. Omitiendo...")
                    continue
                
                # ============================================
                # 2. OBTENER FORMA DE PAGO
                # ============================================
                forma_pago_id = safe_int(record.get('FORMAPAGO'))
                forma_pago_obj = None
                
                if forma_pago_id:
                    forma_pago_obj = formas_pago_cache.get(forma_pago_id)
                    if not forma_pago_obj:
                        formas_pago_no_encontradas += 1
                        logger.warning(f"Registro {idx}: Forma de pago ID {forma_pago_id} no encontrada. Usando NULL.")
                
                # ============================================
                # 3. PROCESAR VALORES NUMÉRICOS
                # ============================================
                # idventas (admite nulos)
                idventas_val = record.get('IDVENTAS')
                idventas_int = None
                if idventas_val is not None and str(idventas_val).strip() and safe_float(idventas_val) != 0:
                    idventas_int = safe_int(idventas_val)
                
                # idcompras (admite nulos)
                idcompras_val = record.get('IDCOMPRAS')
                idcompras_int = None
                if idcompras_val is not None and str(idcompras_val).strip() and safe_float(idcompras_val) != 0:
                    idcompras_int = safe_int(idcompras_val)
                
                # idbancos (admite nulos)
                idbancos_val = record.get('IDBANCOS')
                idbancos_int = None
                if idbancos_val is not None and str(idbancos_val).strip() and safe_float(idbancos_val) != 0:
                    idbancos_int = safe_int(idbancos_val)
                
                # importe (admite valores negativos)
                importe_val = record.get('IMPORTE')
                importe_decimal = safe_decimal(importe_val, 0.0)
                
                # ============================================
                # 4. DETERMINAR TIPO DE MOVIMIENTO
                # ============================================
                # Regla: Si importe >= 0 -> Ingreso (1), si es negativo -> Egreso (2)
                tipo_movimiento = 1 if importe_decimal >= Decimal('0') else 2
                
                # ============================================
                # 5. OBSERVACIÓN
                # ============================================
                observacion = record.get('OBSERVACION', '').strip()
                if observacion:
                    # Limitar a 50 caracteres como máximo
                    observacion = str(observacion)[:50]
                
                # ============================================
                # 6. VERIFICAR SI EL REGISTRO YA EXISTE
                # ============================================
                # Buscar por combinación única
                existe = CajaDetalle.objects.filter(
                    id_caja=caja_obj,
                    idventas=idventas_int,
                    idcompras=idcompras_int,
                    idbancos=idbancos_int,
                    id_forma_pago=forma_pago_obj,
                    importe=importe_decimal,
                    observacion=observacion
                ).exists()
                
                if existe:
                    duplicados += 1
                    if duplicados % 100 == 0:
                        logger.debug(f"Registro {idx}: Ya existe en sistema, omitiendo...")
                    continue
                
                # ============================================
                # 7. CREAR OBJETO CAJA DETALLE - SOLO LOS CAMPOS DEL MODELO
                # ============================================
                caja_detalle = CajaDetalle(
                    # Campos del modelo CajaDetalle
                    id_caja=caja_obj,
                    idventas=idventas_int,
                    idcompras=idcompras_int,
                    idbancos=idbancos_int,
                    id_forma_pago=forma_pago_obj,
                    importe=importe_decimal,
                    tipo_movimiento=tipo_movimiento,
                    observacion=observacion
                    
                    # NO INCLUIR: created_at, updated_at, is_active
                    # Estos campos son automáticos o no existen en tu modelo
                )
                
                detalles_batch.append(caja_detalle)
                registros_procesados += 1

                # Mostrar progreso cada 4000 registros
                if registros_procesados % 4000 == 0:
                    print(f"Procesados: {registros_procesados}/{total_records} registros")

                # Guardar por lotes
                if len(detalles_batch) >= batch_size:
                    with transaction.atomic():
                        CajaDetalle.objects.bulk_create(detalles_batch)
                        # logger.info(f"Lote guardado: {len(detalles_batch)} registros")
                        total_regs += len(detalles_batch)
                        print(f"Lote guardado: {len(detalles_batch)} registros - Acumulado: {total_regs} registros")
                        detalles_batch = []

            except Exception as e:
                errores += 1
                logger.error(f"Error en registro {idx} (Caja: {record.get('CAJA')}): {str(e)}")
                print(f"Error en registro {idx}: {str(e)}")
                continue

        # Guardar últimos registros
        if detalles_batch:
            with transaction.atomic():
                CajaDetalle.objects.bulk_create(detalles_batch)
                logger.info(f"Último lote guardado: {len(detalles_batch)} registros")
                total_regs += len(detalles_batch)
                print(f"Último lote guardado: {len(detalles_batch)} registros")

        # Resultados finales
        elapsed_time = time.time() - start_time
        logger.info(f"Migración completada. Registros: {registros_procesados}, Errores: {errores}")
        logger.info(f"Cajas no encontradas: {cajas_no_encontradas}")
        logger.info(f"Formas de pago no encontradas: {formas_pago_no_encontradas}")
        logger.info(f"Duplicados omitidos: {duplicados}")
        logger.info(f"Tiempo total: {elapsed_time:.2f} segundos")

        print(f"\nResumen de migración de CajaDetalle:")
        print(f"Total registros en DBF: {total_records}")
        print(f"Registros procesados exitosamente: {registros_procesados}")
        print(f"Cajas no encontradas (omitidas): {cajas_no_encontradas}")
        print(f"Formas de pago no encontradas: {formas_pago_no_encontradas}")
        print(f"Duplicados omitidos: {duplicados}")
        print(f"Errores encontrados: {errores}")
        print(f"Tiempo total: {elapsed_time:.2f} segundos")
        
        if cajas_no_encontradas > 0:
            print(f"\nADVERTENCIA: {cajas_no_encontradas} registros omitidos porque no se encontró la caja correspondiente.")
            print("Asegúrate de haber migrado las cajas primero o verifica los números de caja en el DBF.")

    except Exception as e:
        logger.error(f"Error fatal en cargar_datos_cajadetalle: {str(e)}")
        print(f"ERROR FATAL: {str(e)}")
        raise

if __name__ == '__main__':
    cargar_datos_cajadetalle()