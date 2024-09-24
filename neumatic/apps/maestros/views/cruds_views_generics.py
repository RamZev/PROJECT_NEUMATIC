# D:\HL_PROJECT\PERSONALSYS\apps\maestros\views\cruds_views_generics.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.http import JsonResponse

#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

#-- Recursos necesarios para los permisos de usuarios sobre modelos.
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

from django.utils import timezone


# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class MaestroListView(ListView):
	cadena_filtro = ""
	paginate_by = 8
	
	#app_label = ''
	search_fields = []
	ordering = []
	
	table_headers = {}
	table_data = []
	pagination_options = [8, 20, 30, 40, 50]
	
	def get_queryset(self):
		#-- Acá ya determina el Modelo con el que se trabaja.
		#-- Obtiene todos los registros sin filtro.
		#-- Con lo cual no es necesario un filter.all().
		#-- luego cambiar a que por defecto no haya registros.
		queryset = super().get_queryset()
		
		#-- Obtener el valor de paginate_by de la URL, si está presente.
		paginate_by_param = self.request.GET.get('paginate_by')
		if paginate_by_param is not None:
			try:
				#-- Intentar convertir a entero, usar valor predeterminado si falla.
				paginate_by_value = int(paginate_by_param)
				self.paginate_by = paginate_by_value
			except ValueError:
				pass
		
		#-- Obtener la cadena de filtro.
		query = self.request.GET.get('busqueda', None)
		
		# #-- Obtener el modelo dinámicamente.
		# Model = apps.get_model(app_label=self.app_label, model_name=self.model.__name__)
		
		#-- Crear la cadena de filtro en base a la lista search_fields-
		cadena_filtro = ""
		for field in self.search_fields:
			expression = f"Q({field}__icontains='{query}')"
			cadena_filtro += expression + " | "
		
		#-- Eliminar el último " | " en la cadena de filtro.
		cadena_filtro = "(" + cadena_filtro[:-3] + ")"
		
		#-- Ejecutar la consulta.
		if query and cadena_filtro:
			#queryset = Model.objects.filter(eval(cadena_filtro))
			queryset = queryset.filter(eval(cadena_filtro))
		# else:
		# 	# Sin filtro, obtener todos los registros
		# 	queryset = Model.objects.all()
		
		# Ordenar el queryset según la lista ordering
		queryset = queryset.order_by(*self.ordering)
		
		############################################
		# text = self.request.GET.get('buscar', None)
		# if text and self.cadena_filtro:
		# 	queryset = queryset.filter(eval(self.cadena_filtro))
		############################################
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		#context["buscar"] = self.request.GET.get('buscar', '')
		context["busqueda"] = self.request.GET.get('busqueda', '')
		
		# #-- Encabezado de la Tabla.
		# context['table_headers'] = self.table_headers
		# 
		# #-- Columnas de la Tabla.
		# context['table_data'] = self.table_data
		
		#-- Agregar valores de paginación y valor seleccionado.
		context['pagination_options'] = self.pagination_options
		context['selected_pagination'] = int(self.paginate_by)
		# Para pasar la fecha a la lista del maestro		
		context['fecha'] = timezone.now()

		return context
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el valor de paginate_by de la URL, si está presente.
		paginate_by_param = self.request.GET.get('paginate_by')
		if paginate_by_param is not None:
			try:
				#-- Intentar convertir a entero, usar valor predeterminado si falla.
				paginate_by_value = int(paginate_by_param)
				self.paginate_by = paginate_by_value
			except ValueError:
				pass
			
		#-- Mantener el valor de paginate_by en el formulario de paginación.
		self.request.GET = self.request.GET.copy()
		self.request.GET['paginate_by'] = str(self.paginate_by)
		#print("Mantener el valor de paginate_by: ", self.paginate_by)

		return super().get(request, *args, **kwargs)
	
	def get_paginate_by(self, queryset):
		#-- Utilizar el valor actualizado de paginate_by.
		return self.paginate_by


@method_decorator(login_required, name='dispatch')
class MaestroCreateView(PermissionRequiredMixin, CreateView):
	list_view_name = None
	
#	fields_to_validate = []
	
# 	def form_valid(self, form):
# 		#-- Validar los campos de fields_to_validate.
# 		for field, error_message in self.fields_to_validate:
# 			if not form.cleaned_data.get(field):
# 				form.add_error(field, error_message)
# 		
# 		#-- Verificar si hay errores de validación.
# 		if form.errors:
# 			print("Hay errores en el formulario!")
# 			return self.form_invalid(form)
# 
# 		#-- Llama al método save del formulario para guardar los datos.
# 		return super().form_valid(form)
# 
# 	
# 	def form_invalid(self, form):
# 		"""
# 		Si el formulario no es válido, renderiza el formulario con los errores.
# 		"""
# 		return self.render_to_response(self.get_context_data(form=form))
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = self.form_class()
		return context
	
	#-- Método que agrega mensaje cuando no tiene permiso de crear.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)	


@method_decorator(login_required, name='dispatch')
class MaestroUpdateView(PermissionRequiredMixin, UpdateView):
	# -- Nombre del argumento de clave primaria pasado en el url. Por defecto es pk.
	# pk_url_kwarg = "id"
	
	list_view_name = None
	
	#-- Método que agrega mensaje cuando no tiene permiso de modificar.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)


@method_decorator(login_required, name='dispatch')
class MaestroDeleteView(PermissionRequiredMixin, DeleteView):
	# -- Nombre del argumento de clave primaria pasado en el url. Por defecto es pk.
	# pk_url_kwarg = "id"
	
	list_view_name = None
	
	#-- Método que agrega mensaje cuando no tiene permiso de modificar.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)
# ------------------------------------------------------------------------------------


@method_decorator(login_required, name='dispatch')
class GenericDetailView(DetailView):
    def get_data(self, obj):
        """
        Este método debe ser sobreescrito en la clase hija 
        para proporcionar los datos específicos.
        """
        return {}

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        data = self.get_data(obj)
        return JsonResponse(data)
# ------------------------------------------------------------------------------------
