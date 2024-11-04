# neumatic\apps\maestros\views\operario_views.py
from django.urls import reverse_lazy
from ..views.cruds_views_generics import *
from ..models.producto_models import Producto
from ..forms.producto_forms import ProductoForm
from ..models.base_models import (ProductoDeposito, ProductoStock, 
								  ProductoMinimo, ProductoCai)


class ConfigViews():
	# Modelo
	model = Producto
	
	# Formulario asociado al modelo
	form_class = ProductoForm
	
	# Aplicación asociada al modelo
	app_label = model._meta.app_label
	
	#-- Deshabilitado por redundancia:
	# # Título del listado del modelo
	# master_title = model._meta.verbose_name_plural
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	model_string = model.__name__.lower()  #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	
	#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
	# model_string = "tipo_retencion_ib"
	
	# Permisos
	permission_add = f"{app_label}.add_{model.__name__.lower()}"
	permission_change = f"{app_label}.change_{model.__name__.lower()}"
	permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	create_view_name = f"{model_string}_create"
	update_view_name = f"{model_string}_update"
	delete_view_name = f"{model_string}_delete"
	
	# Plantilla para crear o actualizar el modelo
	template_form = f"{app_label}/{model_string}_form.html"
	
	# Plantilla para confirmar eliminación de un registro
	template_delete = "base_confirm_delete.html"
	
	# Plantilla de la lista del CRUD
	template_list = f'{app_label}/maestro_list.html'
	
	# Contexto de los datos de la lista
	context_object_name	= 'objetos'
	
	# Vista del home del proyecto
	home_view_name = "home"
	
	# Nombre de la url 
	success_url = reverse_lazy(list_view_name)


class DataViewList():
	search_fields = ['nombre_producto', 
					 'medida', 
					 'id_cai__cai', 
	]
	
	ordering = ['nombre_producto']
	
	paginate_by = 8
	
	table_headers = {
		'nombre_producto': (6, 'Nombre producto'),
		'medida': (2, 'Medida'),
		'id_cai': (2, 'CAI'),
		
		'acciones': (2, 'Acciones'),
	}
	
	table_data = [
		{'field_name': 'nombre_producto', 'date_format': None},
		{'field_name': 'medida', 'date_format': None},
		{'field_name': 'id_cai', 'date_format': None},
	]


# ProductoListView - Inicio
class ProductoListView(MaestroListView):
	model = ConfigViews.model
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	search_fields = DataViewList.search_fields
	ordering = DataViewList.ordering
	
	extra_context = {
		"master_title": ConfigViews.model._meta.verbose_name_plural,
		"home_view_name": ConfigViews.home_view_name,
		"list_view_name": ConfigViews.list_view_name,
		"create_view_name": ConfigViews.create_view_name,
		"update_view_name": ConfigViews.update_view_name,
		"delete_view_name": ConfigViews.delete_view_name,
		"table_headers": DataViewList.table_headers,
		"table_data": DataViewList.table_data,
	}


# ProductoCreateView - Inicio
class ProductoCreateView(MaestroCreateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	# (revisar de donde lo copiaste que tienes asignado permission_change en vez de permission_add)
	permission_required = ConfigViews.permission_add
	
	extra_context = {
		"accion": f"Crear {ConfigViews.model._meta.verbose_name}",
		"list_view_name" : ConfigViews.list_view_name
	}
	
	def form_valid(self, form):
		response = super().form_valid(form)
		
		producto = self.object
		if producto.tipo_producto == 'p':
			#-- Obtener todos los depósitos.
			depositos = ProductoDeposito.objects.all()
			
			#-- Registrar en ProductoStock para cada depósito.
			for deposito in depositos:
				ProductoStock.objects.create(
					id_producto=producto,
					id_deposito=deposito,
					stock=0,
					minimo=0,
					fecha_producto_stock=timezone.now()
				)
			
			#-- Registrar en ProductoMinimo si el CAI existe y no está ya en ProductoMinimo.
			if producto.id_cai:
				for deposito in depositos:
					#-- Registrar solo si el CAI no existe ya en ProductoMinimo.
					if not ProductoMinimo.objects.filter(id_cai=producto.id_cai, id_deposito=deposito).exists():
						ProductoMinimo.objects.create(
							id_deposito=deposito,
							id_cai=producto.id_cai,
							minimo=producto.minimo
						)
			
		return response


# ProductoUpdateView
class ProductoUpdateView(MaestroUpdateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_change
	
	def form_valid(self, form):
		producto = form.save(commit=False)
		old_cai = Producto.objects.get(pk=producto.pk).id_cai
		new_cai = producto.id_cai
		
		response = super().form_valid(form)
		
		depositos = ProductoDeposito.objects.all()
		
		#-- Manejar cambios en el CAI.
		if new_cai:
			if old_cai != new_cai:
				#-- Solo elimina el CAI anterior en ProductoMinimo si no existen otros productos asociados a ese CAI.
				if not Producto.objects.filter(id_cai=old_cai).exclude(pk=producto.pk).exists():
					ProductoMinimo.objects.filter(id_cai=old_cai).delete()
				for deposito in depositos:
					if not ProductoMinimo.objects.filter(id_cai=new_cai, id_deposito=deposito).exists():
						ProductoMinimo.objects.create(
							id_deposito=deposito,
							id_cai=new_cai,
							minimo=producto.minimo
						)
		else:
			#-- Si el nuevo CAI es None.
			#-- Solo elimina el CAI anterior en ProductoMinimo si no existen otros productos asociados a ese CAI.
			if old_cai and not Producto.objects.filter(id_cai=old_cai).exclude(pk=producto.pk).exists():
				ProductoMinimo.objects.filter(id_cai=old_cai).delete()
				
		return response
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Obtener el producto actual.
		producto = self.object
		
		#-- Consultar registros de ProductoStock y ProductoMinimo relacionados al producto.
		context['producto_stock_list'] = ProductoStock.objects.filter(id_producto=producto).order_by('id_deposito__nombre_producto_deposito')
		context['producto_minimo_list'] = ProductoMinimo.objects.filter(id_cai=producto.id_cai).order_by('id_deposito__nombre_producto_deposito')
		
		#-- Agregar datos adicionales al contexto.
		context.update({
			"accion": f"Editar {ConfigViews.model._meta.verbose_name}",
			"list_view_name": ConfigViews.list_view_name,
		})
		
		return context

# ProductoDeleteView
class ProductoDeleteView (MaestroDeleteView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	template_name = ConfigViews.template_delete
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_delete
	
	extra_context = {
		"accion": f"Eliminar {ConfigViews.model._meta.verbose_name}",
		"list_view_name" : ConfigViews.list_view_name,
		"mensaje": "Estás seguro de eliminar el Registro"
	}
	
	def delete(self, request, *args, **kwargs):
		producto = self.get_object()
		
		#-- Almacena el CAI antes de eliminar el producto.
		cai = producto.id_cai
		
		#-- Eliminar el producto.
		response = super().delete(request, *args, **kwargs)
		
		#-- Eliminar registros en ProductoStock relacionados al producto eliminado.
		ProductoStock.objects.filter(id_producto=producto).delete()
		
		#-- Si el CAI existe, verifica que no haya otros productos con el mismo CAI.
		if cai and not Producto.objects.filter(id_cai=cai).exists():
			#-- Eliminar registros en ProductoMinimo asociados al CAI.
			ProductoMinimo.objects.filter(id_cai=cai).delete()
		
		return response	
