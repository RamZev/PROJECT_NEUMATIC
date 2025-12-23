# neumatic\data_load\cheque_recibo_migra.py
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

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.ventas.models.recibo_models import ChequeRecibo
from apps.ventas.models.factura_models import Factura
from apps.maestros.models.base_models import Banco

# Configuración de logging
logging.basicConfig(
    filename='cheque_recibo_migra.log',
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

def safe_small_int(value, default=None):
    """Conversión segura a SmallInteger"""
    try:
        if value is None or str(value).strip() == '':
            return default
        return int(float(value))
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

def safe_date(value, default=None):
    """Conversión segura para fechas de DBF"""
    try:
        if value and isinstance(value, (date, datetime)):
            return value
        elif value and str(value).strip():
            if isinstance(value, str):
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
            return default
        return default
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Conversión segura a booleano"""
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            value = value.upper().strip()
            return value in ['T', 'TRUE', '1', 'S', 'SI', 'Y', 'YES', 'V']
        return default
    except (ValueError, TypeError):
        return default

def reset_cheque_recibo():
    """Elimina los datos existentes de manera controlada"""
    try:
        print("<info>Iniciando reset de ChequeRecibo...</info>")
        with transaction.atomic():
            count = ChequeRecibo.objects.count()
            ChequeRecibo.objects.all().delete()
            logger.info(f"Eliminados {count} registros existentes de ChequeRecibo")
            print(f"<info>Eliminados {count} registros existentes de ChequeRecibo</info>")
            
            if 'sqlite' in connection.settings_dict['ENGINE']:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='cheque_recibo';")
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                with connection.cursor() as cursor:
                    cursor.execute("ALTER SEQUENCE cheque_recibo_id_cheque_recibo_seq RESTART WITH 1;")
        print("<info>Reset de ChequeRecibo completado</info>")
    except Exception as e:
        logger.error(f"Error en reset_cheque_recibo: {e}")
        print(f"<error>ERROR en reset_cheque_recibo: {e}</error>")
        raise

def cargar_datos_cheque_recibo():
    """Migración optimizada de cheques.DBF a modelo ChequeRecibo"""
    try:
        start_time = time.time()
        
        print("<info>Iniciando migración de ChequeRecibo...</info>")
        reset_cheque_recibo()

        # Precargar caches para optimización
        print("<info>Cargando cachés...</info>")
        
        # Cache de facturas por COMPRO + NUMERO_COMPROBANTE
        facturas_cache = {}
        for factura in Factura.objects.all():
            if factura.compro and factura.numero_comprobante:
                clave = f"{factura.compro.strip().upper()}_{factura.numero_comprobante}"
                facturas_cache[clave] = factura
        
        print(f"<info>Cargadas {len(facturas_cache)} facturas en caché</info>")
        
        # Cache de bancos por id_banco
        bancos_cache = {banco.id_banco: banco for banco in Banco.objects.all()}
        print(f"<info>Cargados {len(bancos_cache)} bancos en caché</info>")

        dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'cheques.DBF')
        print(f"<info>Procesando archivo: {dbf_path}</info>")
        
        table = DBF(dbf_path, encoding='latin-1')
        total_records = len(table)
        print(f"<info>Total de registros en DBF: {total_records}</info>")
        
        # Mostrar estructura del DBF (solo campos importantes)
        print("\n<info>=== CAMPOS IMPORTANTES DEL DBF ===</info>")
        campos_importantes = ['IDCHEQUE', 'CAJA', 'CODBCO', 'SUCURSAL', 'LOCALIDAD', 
                            'NUMERO', 'CUENTA', 'CUIT', 'FECHA', 'IMPORTE', 
                            'COMPROING', 'NROCOMPROING', 'ELECTRONIC']
        for field in table.fields:
            nombre_campo = field.name[:10] if len(field.name) > 10 else field.name
            if nombre_campo in [c[:10] for c in campos_importantes]:
                print(f"  <info>{nombre_campo:10} | Tipo: {field.type} | Tamaño: {field.length}</info>")

        # Procesamiento por lotes
        batch_size = 5000
        cheques_batch = []
        registros_procesados = 0
        registros_validos = 0
        total_regs = 0
        errores = 0
        facturas_no_encontradas = 0
        bancos_no_encontrados = 0

        for idx, record in enumerate(table, 1):
            try:
                # ============================================
                # 1. OBTENER FACTURA (COMPROING + NROCOMPROING)
                # ============================================
                # IMPORTANTE: Campos DBF pueden estar truncados a 10 caracteres
                comproing_raw = None
                nrocomproing_raw = None
                
                # Buscar campo COMPROING (puede estar truncado a 10 chars)
                for campo in ['COMPROING', 'COMPROIN', 'COMPROI', 'COMPRO']:
                    if campo in record:
                        comproing_raw = record.get(campo)
                        break
                
                # Buscar campo NROCOMPROING (puede estar truncado a 10 chars)
                for campo in ['NROCOMPROIN', 'NROCOMPROI', 'NROCOMPRO', 'NROCOMPR', 'NROCOMP']:
                    if campo in record:
                        nrocomproing_raw = record.get(campo)
                        break
                
                id_factura_instancia = None
                if comproing_raw and nrocomproing_raw:
                    comproing = str(comproing_raw).strip().upper()
                    nrocomproing = safe_int(nrocomproing_raw)
                    
                    if comproing and nrocomproing:
                        clave = f"{comproing}_{nrocomproing}"
                        id_factura_instancia = facturas_cache.get(clave)
                        
                        if not id_factura_instancia:
                            facturas_no_encontradas += 1
                            if facturas_no_encontradas <= 10:
                                print(f"  <warning>Factura no encontrada: {comproing} - {nrocomproing}</warning>")
                
                # ============================================
                # 2. OBTENER BANCO (CODBCO)
                # ============================================
                codbco_raw = record.get('CODBCO')
                id_banco_instancia = None
                
                if codbco_raw:
                    codbco = safe_int(codbco_raw)
                    if codbco:
                        id_banco_instancia = bancos_cache.get(codbco)
                        if not id_banco_instancia:
                            bancos_no_encontrados += 1
                            if bancos_no_encontrados <= 10:
                                print(f"  <warning>Banco no encontrado: CODBCO={codbco}</warning>")
                
                # ============================================
                # 3. OBTENER CAMPOS NUMÉRICOS
                # ============================================
                codigo_banco = safe_small_int(record.get('CODBCO'))
                sucursal = safe_small_int(record.get('SUCURSAL'))
                codigo_postal = safe_small_int(record.get('LOCALIDAD'))
                numero_cheque = safe_small_int(record.get('NUMERO'))
                cuenta_cheque = safe_small_int(record.get('CUENTA'))
                cuit_cheque = safe_small_int(record.get('CUIT'))
                
                # ============================================
                # 4. OBTENER FECHAS
                # ============================================
                fecha_cheque1 = safe_date(record.get('FECHA'))
                fecha_cheque2 = None  # Como especificado en las reglas
                
                # ============================================
                # 5. OBTENER IMPORTE
                # ============================================
                importe_raw = record.get('IMPORTE')
                importe_cheque = safe_decimal(importe_raw)
                
                # ============================================
                # 6. OBTENER ELECTRONICO (puede estar truncado)
                # ============================================
                electronico_raw = None
                # Buscar campo ELECTRONICO (puede estar truncado)
                for campo in ['ELECTRONIC', 'ELECTRONI', 'ELECTRON', 'ELECTRO', 'ELECTR']:
                    if campo in record:
                        electronico_raw = record.get(campo)
                        break
                
                electronico = safe_bool(electronico_raw)
                
                # ============================================
                # 7. VERIFICAR SI EL REGISTRO YA EXISTE
                # ============================================
                # Buscar por combinación única
                filtro = {
                    'numero_cheque_recibo': numero_cheque,
                    'cuenta_cheque_recibo': cuenta_cheque,
                    'cuit_cheque_recibo': cuit_cheque,
                    'importe_cheque': importe_cheque,
                }
                
                if id_factura_instancia:
                    filtro['id_factura'] = id_factura_instancia
                if id_banco_instancia:
                    filtro['id_banco'] = id_banco_instancia
                
                existe = ChequeRecibo.objects.filter(**filtro).exists()
                
                if existe:
                    continue
                
                # ============================================
                # 8. CREAR OBJETO CHEQUE RECIBO
                # ============================================
                cheque_recibo = ChequeRecibo(
                    id_factura=id_factura_instancia,
                    id_banco=id_banco_instancia,
                    codigo_banco=codigo_banco,
                    sucursal=sucursal,
                    codigo_postal=codigo_postal,
                    numero_cheque_recibo=numero_cheque,
                    cuenta_cheque_recibo=cuenta_cheque,
                    cuit_cheque_recibo=cuit_cheque,
                    fecha_cheque1=fecha_cheque1,
                    fecha_cheque2=fecha_cheque2,
                    importe_cheque=importe_cheque,
                    electronico=electronico
                )
                
                cheques_batch.append(cheque_recibo)
                registros_procesados += 1
                registros_validos += 1

                # Mostrar progreso cada 5000 registros VÁLIDOS
                if registros_validos % 5000 == 0:
                    print(f"<info>Registros válidos procesados: {registros_validos} (Total leídos: {idx}/{total_records})</info>")
                    
                    # Mostrar ejemplo del último registro procesado (solo primeros lotes)
                    if registros_validos <= 25000:
                        factura_info = f"{comproing_raw} {nrocomproing_raw}" if comproing_raw else "Sin factura"
                        print(f"  <info>Ejemplo: Factura: {factura_info} | Cheque: {numero_cheque} | Importe: {importe_cheque}</info>")

                # Guardar por lotes cuando batch_size se alcanza
                if len(cheques_batch) >= batch_size:
                    with transaction.atomic():
                        ChequeRecibo.objects.bulk_create(cheques_batch)
                        print(f"<success>✅ Lote guardado: {len(cheques_batch)} registros (Total válidos: {registros_validos})</success>")
                        total_regs += len(cheques_batch)
                        cheques_batch = []

            except Exception as e:
                errores += 1
                if errores <= 10:
                    print(f"<error>Error en registro {idx}: {str(e)}</error>")
                    # Debug adicional para primeros errores
                    if errores <= 5:
                        print(f"  <debug>COMPROING: {record.get('COMPROING')}</debug>")
                        print(f"  <debug>NROCOMPROING: {record.get('NROCOMPROING')}</debug>")
                        print(f"  <debug>CODBCO: {record.get('CODBCO')}</debug>")
                continue

        # Guardar últimos registros
        if cheques_batch:
            with transaction.atomic():
                ChequeRecibo.objects.bulk_create(cheques_batch)
                print(f"<success>✅ Último lote guardado: {len(cheques_batch)} registros</success>")
                total_regs += len(cheques_batch)

        # Resultados finales
        elapsed_time = time.time() - start_time
        
        print(f"\n<info>{'='*60}</info>")
        print("<info>RESUMEN FINAL</info>")
        print(f"<info>{'='*60}</info>")
        print(f"<info>Total registros en DBF: {total_records}</info>")
        print(f"<info>Registros leídos: {idx}</info>")
        print(f"\n<warning>Registros omitidos:</warning>")
        print(f"  <warning>- Facturas no encontradas: {facturas_no_encontradas}</warning>")
        print(f"  <warning>- Bancos no encontrados: {bancos_no_encontrados}</warning>")
        print(f"  <warning>- Duplicados: {idx - registros_validos - facturas_no_encontradas - bancos_no_encontrados}</warning>")
        print(f"\n<success>Registros procesados exitosamente: {registros_validos}</success>")
        print(f"<success>Registros guardados en BD: {total_regs}</success>")
        print(f"<error>Errores encontrados: {errores}</error>")
        print(f"\n<info>Tiempo total: {elapsed_time:.2f} segundos</info>")
        
        # Verificar conteo final
        try:
            total_final = ChequeRecibo.objects.count()
            print(f"\n<info>Total registros en tabla cheque_recibo: {total_final}</info>")
            
            if total_regs != total_final:
                print(f"<warning>⚠️  ADVERTENCIA: Total guardado ({total_regs}) no coincide con BD ({total_final})</warning>")
            
            # Mostrar estadísticas de los datos migrados
            if total_final > 0:
                print(f"\n<info>=== ESTADÍSTICAS DE DATOS MIGRADOS ===</info>")
                with_factura = ChequeRecibo.objects.filter(id_factura__isnull=False).count()
                with_banco = ChequeRecibo.objects.filter(id_banco__isnull=False).count()
                electronicos = ChequeRecibo.objects.filter(electronico=True).count()
                
                print(f"<info>Cheques con factura asociada: {with_factura} ({with_factura/total_final*100:.1f}%)</info>")
                print(f"<info>Cheques con banco asociado: {with_banco} ({with_banco/total_final*100:.1f}%)</info>")
                print(f"<info>Cheques electrónicos: {electronicos} ({electronicos/total_final*100:.1f}%)</info>")
                
        except Exception as e:
            print(f"\n<error>Nota: Error al verificar BD: {e}</error>")

    except Exception as e:
        logger.error(f"Error fatal en cargar_datos_cheque_recibo: {str(e)}")
        print(f"<error>ERROR FATAL: {str(e)}</error>")
        raise

if __name__ == '__main__':
    cargar_datos_cheque_recibo()