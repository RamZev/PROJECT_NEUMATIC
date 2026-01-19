# services/numeracion_simple.py
import time
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def obtener_proximo_numero_seguro(pto_vta, cbte_tipo, afip_client):
    """
    Obtiene el próximo número de manera segura
    SOLUCIÓN SIMPLE: Lock vía cache + consulta AFIP
    """
    max_intentos = 3
    
    for intento in range(max_intentos):
        try:
            # 1. INTENTAR OBTENER LOCK (solución más simple)
            lock_key = f"lock_afip_{pto_vta}_{cbte_tipo}"
            
            # cache.add es atómico: solo un proceso puede establecerlo
            lock_obtenido = cache.add(lock_key, "locked", timeout=10)  # 10 segundos
            
            if not lock_obtenido:
                # Alguien más tiene el lock, esperar un poco
                time.sleep(0.1)
                continue
            
            try:
                # 2. TENEMOS EL LOCK → Consultar AFIP
                ultimo_afip = afip_client.obtener_ultimo_autorizado(pto_vta, cbte_tipo)
                
                # 3. Calcular próximo
                proximo = ultimo_afip + 1
                
                logger.info(f"Número obtenido: {pto_vta}-{proximo:08d}")
                return proximo
                
            finally:
                # 4. SIEMPRE liberar el lock
                cache.delete(lock_key)
                
        except Exception as e:
            logger.error(f"Intento {intento+1} falló: {e}")
            if intento < max_intentos - 1:
                time.sleep(0.5)
                continue
            raise
    
    raise Exception("No se pudo obtener número después de reintentos")