# neumatic\apps\informes\views\list_views_generics_prop.py

import uuid
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.views.generic import FormView, TemplateView

#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


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
				queryset = self.obtener_queryset(form.cleaned_data)
				contexto_reporte = self.obtener_contexto_reporte(queryset, form.cleaned_data)
				return self.procesar_reporte(contexto_reporte, form.cleaned_data)
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
		#-- Obtener el contexto de get_context_data.
		context = self.get_context_data(form=form)
		#-- Agrega la bandera de errores.
		context["data_has_errors"] = True
		#-- Renderiza la respuesta con el contexto actualizado.
		return super().render_to_response(context)
	
	def procesar_reporte(self, contexto_reporte, cleaned_data):
		"""
		Una vez validado el formulario, genera un token, guarda el contexto en la sesión y
		devuelve un JSON con la URL de salida (para pantalla o PDF).
		"""
		
		tipo_salida = cleaned_data.get("tipo_salida", "pantalla").lower()
		token = str(uuid.uuid4())
		self.request.session[token] = contexto_reporte
		
		print(f"{tipo_salida = }")
		print(f"{token = }")
		print(f"{self.request.session.items() = }")
		print(f"X-Requested-With: {self.request.headers.get('X-Requested-With')}")

		
		if tipo_salida == "pantalla":
			url = reverse("ventacompro_vista_pantalla") + f"?token={token}"
		elif tipo_salida == "pdf_preliminar":
			url = reverse("ventacompro_vista_pdf") + f"?token={token}&format=pdf"
		else:
			url = reverse("ventacompro_vista_pantalla") + f"?token={token}"
		
		print(f"{url = }")
		
		if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
			return JsonResponse({"success": True, "url": url})
		else:
			print("Llega hasta acá")
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


@method_decorator(login_required, name='dispatch')
class InformeTemplateView(TemplateView):
	pass