# neumatic\apps\maestros\services.py
from django.db import transaction
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import ProductoEstado, MedidasEstados


def actualizar_estados_productos():
	"""
	Actualiza el estado de los productos basado en stock y rangos de MedidasEstados.
	"""
	#-- Obtener los estados una vez para eficiencia.
	estados = ProductoEstado.objects.filter(
		nombre_producto_estado__in=['FALTANTES', 'DISPONIBLES', 'POCAS']
	)
	
	estado_faltantes = estados.filter(nombre_producto_estado='FALTANTES').first()
	estado_disponibles = estados.filter(nombre_producto_estado='DISPONIBLES').first()
	estado_pocas = estados.filter(nombre_producto_estado='POCAS').first()
	
	if not all([estado_faltantes, estado_disponibles, estado_pocas]):
		estados_faltantes = []
		if not estado_faltantes: estados_faltantes.append('FALTANTES')
		if not estado_disponibles: estados_faltantes.append('DISPONIBLES')
		if not estado_pocas: estados_faltantes.append('POCAS')
		raise ValueError(f"No se encontraron los estados: {', '.join(estados_faltantes)}")
	
	#-- Obtener productos a actualizar con prefetch_related para optimización.
	productos = Producto.objects.filter(
		tipo_producto='P'
	).select_related('id_cai').prefetch_related('productostock_set')
	
	productos_actualizados = 0
	actualizaciones = []
	
	with transaction.atomic():
		for producto in productos:
			#-- Calcular stock total.
			stock_total = sum(stock.stock for stock in producto.productostock_set.all())
			
			#-- Obtener medidas_estados relacionadas.
			medidas_estados = MedidasEstados.objects.filter(id_cai=producto.id_cai).first()
			
			if medidas_estados:
				stock_desde = medidas_estados.stock_desde or 0
				stock_hasta = medidas_estados.stock_hasta or 999999
				
				#-- Determinar el estado basado en el stock.
				if stock_total < stock_desde:
					nuevo_estado = estado_faltantes
				elif stock_total > stock_hasta:
					nuevo_estado = estado_disponibles
				else:
					nuevo_estado = estado_pocas
			else:
				#-- Si no hay medidas_estados, usar estado por defecto.
				if stock_total > 0:
					nuevo_estado = estado_disponibles
				else:
					nuevo_estado = estado_faltantes
			
			#-- Actualizar solo si cambió el estado.
			if producto.id_producto_estado != nuevo_estado:
				producto.id_producto_estado = nuevo_estado
				actualizaciones.append(producto)
				productos_actualizados += 1
		
		#-- Bulk update para mejor performance si hay muchas actualizaciones.
		if actualizaciones:
			Producto.objects.bulk_update(actualizaciones, ['id_producto_estado'])
	
	return {
		'total_productos': productos.count(),
		'productos_actualizados': productos_actualizados,
		'message': f"Se actualizaron {productos_actualizados} de {productos.count()} productos"
	}