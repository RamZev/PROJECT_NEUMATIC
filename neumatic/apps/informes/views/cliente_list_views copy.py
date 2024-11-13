# neumatic\apps\informes\views\cliente_list_views.py
from django.urls import reverse_lazy
from ..views.list_views_generics import *
from apps.maestros.models.cliente_models import Cliente
from apps.maestros.models.base_models import *
from django.utils import timezone


class ConfigViews():
	# Modelo
	model = Cliente
	
	# Aplicación asociada al modelo
	# app_label = model._meta.app_label
	# OJO OJO AQUÍ - El modelo pertenece a otra aplicación
	app_label = "informes"
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	model_string = model.__name__.lower()  #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	
	#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
	#model_string = "tipo_cambio"
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	
	# Plantilla de la lista del CRUD
	template_list = f'{app_label}/maestro_informe_list.html'
	
	# Contexto de los datos de la lista
	context_object_name	= 'objetos'
	
	# Vista del home del proyecto
	home_view_name = "home"
	
	# Nombre de la url 
	success_url = reverse_lazy(list_view_name)


class DataViewList():
	search_fields = ['nombre_cliente', 'cuit']
	
	ordering = ['nombre_cliente']
	
	paginate_by = 8
	  
	table_headers = {
		'estatus_cliente': (2, 'Estatus'),
		'nombre_cliente': (4, 'Nombre Cliente'),
		'tipo_persona': (2, 'Tipo'),
		'cuit': (2, 'CUIT'),
		#'acciones': (2, 'Acciones'),
	}
	
	table_data = [
		{'field_name': 'estatus_cliente', 'date_format': None},
		{'field_name': 'nombre_cliente', 'date_format': None},
		{'field_name': 'tipo_persona', 'date_format': None},
		{'field_name': 'cuit', 'date_format': None},
	]


# ClienteListView - Inicio
class ClienteInformeListView(InformeListView):
	model = ConfigViews.model
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	search_fields = DataViewList.search_fields
	ordering = DataViewList.ordering
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		"list_view_name": ConfigViews.list_view_name,
		"table_headers": DataViewList.table_headers,
		"table_data": DataViewList.table_data,
	}
