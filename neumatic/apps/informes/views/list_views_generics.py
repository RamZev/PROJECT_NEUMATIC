# neumatic\apps\informes\views\list_views_generics.py
from typing import Any
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
# from django.http import HttpRequest, HttpResponse, JsonResponse
from django.http import JsonResponse
from django.db import transaction
from django.db.models import ProtectedError


#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

#-- Recursos necesarios para los permisos de usuarios sobre modelos.
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render

from django.utils import timezone


# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class InformeListView(ListView):
	cadena_filtro = ""
	paginate_by = 8
	
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
		
		#-- Obtener la cadena de filtro (Propuesto y recomendado por ChatGPT).
		query = self.request.GET.get('busqueda', None)
		
		if query:
			#-- Generar filtros dinámicamente.
			search_conditions = Q()
			for field in self.search_fields:
				search_conditions |= Q(**{f"{field}__icontains": query})
			
			queryset = queryset.filter(search_conditions)
		
		return queryset.order_by(*self.ordering)
		
		''' Método original de Ricardo y Leoncio. (No seguro)
		#-- Crear la cadena de filtro en base a la lista search_fields-
		cadena_filtro = ""
		for field in self.search_fields:
			expression = f"Q({field}__icontains='{query}')"
			cadena_filtro += expression + " | "
		
		#-- Eliminar el último " | " en la cadena de filtro.
		cadena_filtro = "(" + cadena_filtro[:-3] + ")"
		
		#-- Ejecutar la consulta.
		if query and cadena_filtro:
			queryset = queryset.filter(eval(cadena_filtro))
		
		# Ordenar el queryset según la lista ordering
		queryset = queryset.order_by(*self.ordering)
		
		return queryset'''
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["busqueda"] = self.request.GET.get('busqueda', '')
		
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
		
		return super().get(request, *args, **kwargs)
	
	def get_paginate_by(self, queryset):
		#-- Utilizar el valor actualizado de paginate_by.
		return self.paginate_by

