# neumatic\apps\maestros\signals\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import socket
from django.db import transaction

from ..models.producto_models import Producto
from ..models.base_models import (ProductoDeposito, 
								  ProductoStock, 
								  ProductoMinimo,
								  ProductoCai)

BATCH_SIZE = 1000  # Tamaño del lote para inserción masiva


@receiver(post_save, sender=ProductoDeposito)
def trasladar_productos_a_stock_y_minimo(sender, instance, created, **kwargs):
	if created:
		
		try:
			# Inicia una transacción para las operaciones en el signal
			with transaction.atomic():
				#-- Obtener el usuario autenticado.
				usuario_autenticado = instance.id_user
				nombre_usuario = usuario_autenticado.username if usuario_autenticado else 'Sistema'
				
				#-- Obtener el nombre de la estación y la fecha.
				estacion = socket.gethostname()
				fecha_actual = timezone.now().strftime("%Y-%m-%d %H:%M:%S")		
				
				
				# Paso 1: Obtener productos tipo "P" para ProductoStock
				productos_stock = Producto.objects.filter(tipo_producto="P")
				
				# Crear registros para ProductoStock
				producto_stock_instances = [
					ProductoStock(
						id_producto=producto,
						id_deposito=instance,
						stock=0,
						minimo=0,
						fecha_producto_stock=timezone.now(),
						id_user=usuario_autenticado,
						usuario=nombre_usuario,
						estacion=estacion,
						fcontrol=fecha_actual
					)
					for producto in productos_stock
				]
				
				# Guardar en ProductoStock en lotes
				ProductoStock.objects.bulk_create(producto_stock_instances, batch_size=BATCH_SIZE)
				
				# Paso 2: Obtener productos con id_cai único para ProductoMinimo
				productos_minimo = Producto.objects.exclude(id_cai=None).values("id_cai").distinct()
				
				# Crear registros para ProductoMinimo
				producto_minimo_instances = [
					ProductoMinimo(
						id_deposito=instance,
						id_cai=ProductoCai.objects.get(pk=producto["id_cai"]),
						minimo=0,
						id_user=usuario_autenticado,
						usuario=nombre_usuario,
						estacion=estacion,
						fcontrol=fecha_actual
					)
					for producto in productos_minimo
				]
				
				# Guardar en ProductoMinimo en lotes
				ProductoMinimo.objects.bulk_create(producto_minimo_instances, batch_size=BATCH_SIZE)
				
		except Exception as e:
			import logging
			logger = logging.getLogger(__name__)
			logger.error(f"Error en el signal trasladar_productos_a_stock_y_minimo: {str(e)}")
