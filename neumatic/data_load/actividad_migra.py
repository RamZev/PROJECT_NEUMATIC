# neumatic\data_load\caja_migra.py
import os
import sys
import django
import time
import logging
from dbfread import DBF
from django.db import connection
from django.db import transaction
from datetime import date, datetime

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.sucursal_models import Sucursal
from apps.usuarios.models import User
from apps.ventas.models.caja_models import Caja

# Configuración de logging
logging.basicConfig(
    filename='caja_migra.log',
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

def safe_datetime(value, default=None):
    """Conversión segura para fechas/horas de DBF"""
    try:
        if value and isinstance(value, datetime):
            return value
        elif value and str(value).strip():
            if isinstance(value, str):
                for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S'):
                    try:
                        return datetime.strptime(value, fmt)
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
            return value in ['T', 'TRUE', '1', 'S', 'SI', 'Y', 'YES']
        return default
    except (ValueError, TypeError):
        return default

def reset_caja():
    """Elimina los datos existentes de manera controlada"""
    try:
        print("DEBUG: Iniciando reset_caja()")
        with transaction.atomic():
            count = Caja.objects.count()
            print(f"DEBUG: Registros existentes en Caja: {count}")
            Caja.objects.all().delete()
            logger.info(f"Eliminados {count} registros existentes de Caja")
            print(f"DEBUG: Eliminados {count} registros existentes")
            
            if 'sqlite' in connection.settings_dict['ENGINE']:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='caja';")
                    print("DEBUG: Reset sequence SQLite")
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                with connection.cursor() as cursor:
                    cursor.execute("ALTER SEQUENCE caja_id_caja_seq RESTART WITH 1;")
                    print("DEBUG: Reset sequence PostgreSQL")
        print("DEBUG: reset_caja() completado")
    except Exception as e:
        logger.error(f"Error en reset_caja: {e}")
        print(f"DEBUG: ERROR en reset_caja: {e}")
        raise

def cargar_datos_caja():
    """Migración optimizada de caja.DBF a modelo Caja"""
    try:
        print("DEBUG: Iniciando cargar_datos_caja()")
        start_time = time.time()
        reset_caja()

        # Precargar relaciones para optimización
        print("DEBUG: Cargando cache de sucursales...")
        sucursales = list(Sucursal.objects.all())
        sucursales_cache = {s.id_sucursal: s for s in sucursales}
        print(f"DEBUG: Sucursales en cache: {len(sucursales_cache)}")
        
        print("DEBUG: Cargando cache de usuarios...")
        usuarios = list(User.objects.all())
        usuarios_cache = {u.pk: u for u in usuarios}
        print(f"DEBUG: Usuarios en cache: {len(usuarios_cache)}")

        dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'caja.DBF')
        print(f"DEBUG: Ruta del archivo DBF: {dbf_path}")
        logger.info(f"Buscando archivo en: {dbf_path}")
        
        # Verificar si el archivo existe
        if not os.path.exists(dbf_path):
            print(f"ERROR: No se encuentra el archivo {dbf_path}")
            logger.error(f"No se encuentra el archivo {dbf_path}")
            return
        else:
            print("DEBUG: Archivo DBF encontrado")
        
        print("DEBUG: Abriendo archivo DBF...")
        table = DBF(dbf_path, encoding='latin-1')
        total_records = len(table)
        print(f"DEBUG: Total de registros en DBF: {total_records}")
        logger.info(f"Archivo encontrado. Total de registros en DBF: {total_records}")
        
        if total_records == 0:
            print("DEBUG: EL ARCHIVO DBF ESTÁ VACÍO")
            return
        
        # Mostrar estructura completa del primer registro
        print("\nDEBUG: === ESTRUCTURA DEL PRIMER REGISTRO ===")
        for i, record in enumerate(table):
            if i == 0:
                print(f"DEBUG: Primer registro completo: {dict(record)}")
                print(f"DEBUG: Campos disponibles: {list(record.keys())}")
                print(f"DEBUG: Valores del primer registro:")
                for key, value in record.items():
                    print(f"DEBUG:   {key}: {value} (tipo: {type(value)})")
                break
        
        # Reiniciar el iterador
        table = DBF(dbf_path, encoding='latin-1')
        
        # Procesamiento por lotes
        batch_size = 1000
        cajas_batch = []
        registros_procesados = 0
        total_regs = 0
        errores = 0

        print(f"DEBUG: Iniciando procesamiento de {total_records} registros...")
        
        for idx, record in enumerate(table, 1):
            try:
                if idx <= 3:  # Debug solo primeros 3 registros
                    print(f"\nDEBUG: Procesando registro {idx}")
                    print(f"DEBUG: Record keys: {list(record.keys())}")
                
                # BUSQUEDA EXHAUSTIVA DEL CAMPO NUMERO
                numero_caja = None
                posibles_campos = ['numero', 'NUMERO', 'Numero', 'caja', 'CAJA', 'Caja', 'nro', 'NRO']
                
                for campo in posibles_campos:
                    valor = record.get(campo)
                    if valor is not None:
                        numero_caja = safe_int(valor)
                        if numero_caja:
                            if idx <= 3:
                                print(f"DEBUG: Campo '{campo}' encontrado: {valor} -> {numero_caja}")
                            break
                
                if not numero_caja:
                    if idx <= 3:
                        print(f"DEBUG: No se encontró número de caja válido. Campos disponibles: {list(record.keys())}")
                        for key, value in record.items():
                            print(f"DEBUG:   {key}: {value}")
                    logger.warning(f"Registro {idx} sin número de caja válido")
                    continue

                if idx <= 3:
                    print(f"DEBUG: Número de caja válido: {numero_caja}")

                # Obtener sucursal
                sucursal_id = None
                posibles_sucursal = ['sucursal', 'SUCURSAL', 'Sucursal', 'suc', 'SUC']
                for campo in posibles_sucursal:
                    valor = record.get(campo)
                    if valor is not None:
                        sucursal_id = safe_int(valor)
                        if sucursal_id:
                            break
                
                id_sucursal_instancia = None
                if sucursal_id and sucursal_id in sucursales_cache:
                    id_sucursal_instancia = sucursales_cache[sucursal_id]
                    if idx <= 3:
                        print(f"DEBUG: Sucursal encontrada: {sucursal_id}")
                else:
                    if idx <= 3:
                        print(f"DEBUG: Sucursal no encontrada o inválida: {sucursal_id}")

                # Buscar usuario para cierre
                usuario_cierre_nombre = None
                posibles_usuario = ['usuario', 'USUARIO', 'Usuario', 'user', 'USER']
                for campo in posibles_usuario:
                    valor = record.get(campo)
                    if valor is not None and str(valor).strip():
                        usuario_cierre_nombre = str(valor).strip()
                        break
                
                id_usercierre_instancia = None
                if usuario_cierre_nombre:
                    for user in usuarios_cache.values():
                        if user.username and usuario_cierre_nombre.lower() in user.username.lower():
                            id_usercierre_instancia = user
                            if idx <= 3:
                                print(f"DEBUG: Usuario encontrado: {usuario_cierre_nombre}")
                            break
                    if not id_usercierre_instancia and idx <= 3:
                        print(f"DEBUG: Usuario no encontrado: '{usuario_cierre_nombre}'")

                # EXTRAER TODOS LOS CAMPOS CON DEBUG
                if idx <= 3:
                    print("DEBUG: Extrayendo campos:")
                
                fecha_caja = safe_date(record.get('fecha') or record.get('FECHA'))
                saldoanterior = safe_float(record.get('saldoanterior') or record.get('SALDOANTERIOR'))
                ingresos = safe_float(record.get('ingresos') or record.get('INGRESOS'))
                egresos = safe_float(record.get('egresos') or record.get('EGRESOS'))
                saldo = safe_float(record.get('saldo') or record.get('SALDO'))
                caja_cerrada = safe_bool(record.get('cerrada') or record.get('CERRADA'))
                recuento = safe_float(record.get('recuento') or record.get('RECUENTO'))
                diferencia = safe_float(record.get('diferencia') or record.get('DIFERENCIA'))
                hora_cierre = safe_datetime(record.get('horaciente') or record.get('HORACIENTE'))
                observacion_caja = (record.get('observa') or record.get('OBSERVA') or '')[:50]
                
                if idx <= 3:
                    print(f"DEBUG: fecha_caja: {fecha_caja}")
                    print(f"DEBUG: saldoanterior: {saldoanterior}")
                    print(f"DEBUG: ingresos: {ingresos}")
                    print(f"DEBUG: egresos: {egresos}")
                    print(f"DEBUG: saldo: {saldo}")
                    print(f"DEBUG: caja_cerrada: {caja_cerrada}")
                    print(f"DEBUG: recuento: {recuento}")
                    print(f"DEBUG: diferencia: {diferencia}")
                    print(f"DEBUG: hora_cierre: {hora_cierre}")
                    print(f"DEBUG: observacion_caja: {observacion_caja}")

                # Crear instancia de Caja
                caja = Caja(
                    numero_caja=numero_caja,
                    fecha_caja=fecha_caja,
                    saldoanterior=saldoanterior,
                    ingresos=ingresos,
                    egresos=egresos,
                    saldo=saldo,
                    caja_cerrada=caja_cerrada,
                    recuento=recuento,
                    diferencia=diferencia,
                    id_sucursal=id_sucursal_instancia,
                    hora_cierre=hora_cierre,
                    observacion_caja=observacion_caja,
                    id_usercierre=id_usercierre_instancia
                )
                
                cajas_batch.append(caja)
                registros_procesados += 1

                if idx <= 3:
                    print(f"DEBUG: Registro {idx} agregado al lote")

                # Guardar por lotes
                if len(cajas_batch) >= batch_size:
                    print(f"DEBUG: Guardando lote de {len(cajas_batch)} registros...")
                    Caja.objects.bulk_create(cajas_batch)
                    logger.info(f"Lote guardado: {len(cajas_batch)} registros")
                    total_regs += len(cajas_batch)
                    print(f"DEBUG: Lote guardado: {len(cajas_batch)} registros - Acumulado: {total_regs} registros")
                    cajas_batch = []

            except Exception as e:
                errores += 1
                logger.error(f"Error en registro {idx} (Número: {record.get('numero')}): {str(e)}")
                print(f"DEBUG: ERROR en registro {idx}: {str(e)}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                continue

        # Guardar últimos registros
        if cajas_batch:
            print(f"DEBUG: Guardando último lote de {len(cajas_batch)} registros...")
            Caja.objects.bulk_create(cajas_batch)
            logger.info(f"Último lote guardado: {len(cajas_batch)} registros")
            total_regs += len(cajas_batch)
            print(f"DEBUG: Último lote guardado: {len(cajas_batch)} registros")

        # Resultados finales
        elapsed_time = time.time() - start_time
        logger.info(f"Migración completada. Registros: {registros_procesados}, Errores: {errores}")
        logger.info(f"Tiempo total: {elapsed_time:.2f} segundos")

        print(f"\nDEBUG: === RESUMEN FINAL ===")
        print(f"Total registros en DBF: {total_records}")
        print(f"Registros procesados: {registros_procesados}")
        print(f"Errores encontrados: {errores}")
        print(f"Tiempo total: {elapsed_time:.2f} segundos")

    except Exception as e:
        logger.error(f"Error fatal en cargar_datos_caja: {str(e)}")
        print(f"DEBUG: ERROR FATAL: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback completo: {traceback.format_exc()}")
        raise

if __name__ == '__main__':
    print("DEBUG: Script iniciado")
    cargar_datos_caja()
    print("DEBUG: Script finalizado")