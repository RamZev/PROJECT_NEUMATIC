# neumatic\apps\ventas\views\compra_otros_views.py
from django.urls import reverse_lazy
from ..views.views_generics import *
from ..models.compra_models import Compra
from ..forms.compra_otros_forms import CompraOtrosForm
# from django.utils import timezone


class ConfigViews():
	# Modelo
	model = Compra
	
	# Formulario asociado al modelo
	form_class = CompraOtrosForm
	
	# Aplicación asociada al modelo
	app_label = model._meta.app_label
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	model_string = model.__name__.lower()  #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	
	#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
	#model_string = "tipo_cambio"
	
	# Permisos
	permission_add = f"{app_label}.add_{model.__name__.lower()}"
	permission_change = f"{app_label}.change_{model.__name__.lower()}"
	permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
	
	# Vistas del CRUD del modelo
	# list_view_name = f"{model_string}_list"
	# create_view_name = f"{model_string}_create"
	# update_view_name = f"{model_string}_update"
	# delete_view_name = f"{model_string}_delete"
	list_view_name = f"{model_string}_otros_list"
	create_view_name = f"{model_string}_otros_create"
	update_view_name = f"{model_string}_otros_update"
	delete_view_name = f"{model_string}_otros_delete"
	
	# Plantilla para crear o actualizar el modelo
	# template_form = f"{app_label}/{model_string}_form.html"
	template_form = f"{app_label}/{model_string}_otros_form.html"
	
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
	search_fields = ['numero_comprobante']
	
	ordering = ['numero_comprobante']
	
	paginate_by = 8
	  
	table_headers = {
		# 'estatus_cliente': (1, 'Estatus'),
		'id_comprobante_compra': (4, 'Comprobante'),
		'compro': (2, 'Compro'),
		'letra_comprobante': (2, 'Letra'),
		'numero_comprobante': (2, 'Número'),
		
		'acciones': (2, 'Acciones'),
	}
	
	table_data = [
		# {'field_name': 'estatus_cliente', 'date_format': None},
		{'field_name': 'id_comprobante_compra', 'date_format': None},
		{'field_name': 'compro', 'date_format': None},
		{'field_name': 'letra_comprobante', 'date_format': None},
		{'field_name': 'numero_comprobante', 'date_format': None},
	]


class CompraOtrosListView(MaestroListView):
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


class CompraOtrosCreateView(MaestroCreateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_add
	
	# def get_initial(self):
	# 	initial = super().get_initial()
	# 	#-- Asignar la sucursal del usuario autenticado como valor inicial.
	# 	initial['id_sucursal'] = self.request.user.id_sucursal
	# 	return initial


class CompraOtrosUpdateView(MaestroUpdateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_change


class CompraOtrosDeleteView (MaestroDeleteView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	template_name = ConfigViews.template_delete
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_delete
