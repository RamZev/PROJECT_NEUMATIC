# neumatic\apps\informes\views\list_views_generics.py

import uuid
from django.views.generic import FormView
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string

#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from utils.utils import serializar_datos

# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class InformeFormView(FormView):
	"""
	Clase base para informes.
	Se encarga de:
	  - Validar el formulario.
	  - Ejecutar la consulta mediante obtener_queryset().
	  - Obtener el contexto final para el reporte mediante obtener_contexto_reporte().
	  - Procesar la salida según el parámetro 'tipo_salida'.
	Las vistas hijas deberán implementar, al menos, obtener_queryset()
	y, en caso de necesitar transformación de datos, obtener_contexto_reporte().
	"""
	
	def get(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		if request.GET and any(value for key, value in request.GET.items() if value):
			if form.is_valid():
				tipo_salida = request.GET.get("tipo_salida")
				#-- Se ejecuta la consulta a la Base de Datos.
				queryset = self.obtener_queryset(form.cleaned_data)
				#-- Obtiene el contexto del reporte; por defecto, puede ser simplemente el queryset.
				contexto_reporte = self.obtener_contexto_reporte(queryset, form.cleaned_data)
				#-- Procesa la salida.
				return self.procesar_reporte(contexto_reporte, tipo_salida)
			else:
				return self.form_invalid(form)
		
		context_data = self.get_context_data(form=form)
		return self.render_to_response(context_data)
	
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		#-- Sólo asignar data si la querystring contiene datos.
		if len(self.request.GET) > 0:
			kwargs['data'] = self.request.GET
		return kwargs	
	
	def form_invalid(self, form):
		context = self.get_context_data(form=form)
		context["data_has_errors"] = True
		if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
			#-- Renderizar el modal con los errores de validación y enviado en la respuesta JSON.
			html = render_to_string("informes/modal_errors.html", context, request=self.request)
			return JsonResponse({"success": False, "html": html})
		else:
			return super().render_to_response(context)
	
	def procesar_reporte(self, contexto_reporte, tipo_salida):
		"""
		Una vez validado el formulario, genera un token, guarda el contexto en la sesión y
		devuelve un JSON con la URL de salida (para pantalla o PDF).
		"""
		#-- Limpiar posibles reportes previos en la sesión.
		for key in list(self.request.session.keys()):
			if key.startswith("reporte_"):  #-- Opcional: prefijo para identificar tokens de reportes.
				del self.request.session[key]
		
		token = f"reporte_{uuid.uuid4()}"  #-- Agregar prefijo para fácil identificación.
		self.request.session[token] = serializar_datos(contexto_reporte)
		
		if tipo_salida == "pantalla":
			url = reverse(self.config.url_pantalla) + f"?token={token}"
		elif tipo_salida == "pdf_preliminar":
			url = reverse(self.config.url_pdf) + f"?token={token}"
		else:
			url = reverse(self.config.url_pantalla) + f"?token={token}"
		
		if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
			return JsonResponse({"success": True, "url": url})
		else:
			return HttpResponseRedirect(url)
	
	def obtener_queryset(self, cleaned_data):
		"""
		Debe devolver el queryset filtrado según los datos del formulario.
		DEBE implementarse en la vista hija.
		"""
		raise NotImplementedError("Debe implementarse el método obtener_queryset.")
		
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Retorna el contexto que se pasará al template para renderizar el reporte.
		Por defecto, se retorna un contexto con los datos tal cual:
		  {
			 "objetos": queryset
		  }
		Si el listado requiere agrupar, subtotalizar o totalizar, la vista hija
		debe sobreescribir este método.
		"""
		return {"objetos": queryset}
