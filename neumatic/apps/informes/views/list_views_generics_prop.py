# neumatic\apps\informes\views\list_views_generics_prop.py

import asyncio
import uuid
from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string

from django.views.generic import FormView, TemplateView

#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class InformeFormView(FormView):
	"""
	Clase base asíncrona para informes.
	Se encarga de:
	  - Validar el formulario.
	  - Ejecutar la consulta mediante obtener_queryset().
	  - Obtener el contexto final para el reporte mediante obtener_contexto_reporte().
	  - Procesar la salida según el parámetro 'tipo_salida'.
	Las vistas hijas deberán implementar, al menos, obtener_queryset()
	y, en caso de necesitar transformación de datos, obtener_contexto_reporte().
	"""
	
	# http_method_names = ['get', 'post', 'head', 'options', 'trace']
	http_method_names = ['get', 'post']
	
	async def dispatch(self, request, *args, **kwargs):
		return await super().dispatch(request, *args, **kwargs)
	
	async def post(self, request, *args, **kwargs):
		return await self.get(request, *args, **kwargs)
	
	async def get(self, request, *args, **kwargs):
		self.object = None
		form = await sync_to_async(self.get_form)()
		
		if request.GET and any(value for key, value in request.GET.items() if value):
			if form.is_valid():
				#-- Se ejecuta la consulta en un hilo aparte.
				queryset = await sync_to_async(self.obtener_queryset)(form.cleaned_data)
				#-- Obtiene el contexto del reporte; por defecto, puede ser simplemente el queryset.
				contexto_reporte = await sync_to_async(self.obtener_contexto_reporte)(queryset, form.cleaned_data)
				#-- Procesa la salida.
				return await self.procesar_reporte_async(contexto_reporte, form.cleaned_data)
			else:
				# Devuelve el HTML de errores en JSON
				context = await sync_to_async(self.get_context_data)(form=form)
				context["data_has_errors"] = True
				html = await sync_to_async(render_to_string)(self.template_name, context, request=request)
				return JsonResponse({"success": False, "html": html})
				# return await self.form_invalid(form)
		
		#-- Si no hay parámetros, se renderiza la respuesta con el formulario.
		context_data = await sync_to_async(self.get_context_data)(form=form)
		return await sync_to_async(self.render_to_response)(context_data)
	
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		#-- Sólo asignar data si la querystring contiene datos.
		if len(self.request.GET) > 0:
			kwargs['data'] = self.request.GET
		return kwargs	
	
	# async def form_invalid(self, form):
	# 	#-- Obtener el contexto usando la versión síncrona de get_context_data.
	# 	context = await sync_to_async(self.get_context_data)(form=form)
	# 	#-- Agrega la bandera de errores.
	# 	context["data_has_errors"] = True
	# 	#-- Renderiza la respuesta con el contexto actualizado.
	# 	return await sync_to_async(super().render_to_response)(context)
	# async def form_invalid(self, form):
	# 	#-- Obtener el contexto usando la versión síncrona de get_context_data.
	# 	context = await sync_to_async(self.get_context_data)(form=form)
	# 	#-- Agrega la bandera de errores.
	# 	context["data_has_errors"] = True
    #     # Renderiza el HTML (por ejemplo, puedes renderizar el fragmento del modal de errores)
	# 	html = await sync_to_async(render_to_string)(self.template_name, context, request=self.request)
	# 	# Si la solicitud es AJAX, devuelve JSON con el HTML de error
	# 	return JsonResponse({"success": False, "html": html})
	
	# async def procesar_reporte_async(self, contexto_reporte, cleaned_data):
	# 	"""
	# 	Procesa la salida según 'tipo_salida'. Por ejemplo:
	# 	  - 'pantalla': renderiza la plantilla con el contexto.
	# 	  - 'pdf_preliminar': genera el PDF usando la función generar_pdf.
	# 	  - Otros: email, whatsapp (placeholders).
	# 	"""
	# 	tipo_salida = cleaned_data.get("tipo_salida", "pantalla").lower()
	# 	
	# 	print("Entra acá***")
	# 	
	# 	if tipo_salida == "pantalla":
	# 		context = await sync_to_async(self.get_context_data)(**contexto_reporte)
	# 		return await sync_to_async(self.render_to_response)(context)
	# 	elif tipo_salida == "pdf_preliminar":
	# 		html_string = await sync_to_async(render_to_string)(self.template_name, contexto_reporte)
	# 		pdf_file = await sync_to_async(HTML(string=html_string, base_url=self.request.build_absolute_uri()).write_pdf)()
	# 		return HttpResponse(pdf_file, content_type="application/pdf")
	# 	# elif tipo_salida == "email":
	# 	#     enviar_email_reporte(contexto_reporte, cleaned_data.get("email"))
	# 	#     return HttpResponseRedirect(self.get_success_url())
	# 	# elif tipo_salida == "whatsapp":
	# 	#     enviar_whatsapp_reporte(contexto_reporte, cleaned_data.get("celular"))
	# 	#     return HttpResponseRedirect(self.get_success_url())
	# 	else:
	# 		context = await sync_to_async(self.get_context_data)(**contexto_reporte)
	# 		return await sync_to_async(self.render_to_response)(context)
	async def procesar_reporte_async(self, contexto_reporte, cleaned_data):
		"""
		Procesa la salida según 'tipo_salida'. Por ejemplo:
		  - 'pantalla': renderiza la plantilla con el contexto.
		  - 'pdf_preliminar': genera el PDF usando la función generar_pdf.
		  - Otros: email, whatsapp (placeholders).
		"""
		tipo_salida = cleaned_data.get("tipo_salida", "pantalla").lower()
		
		# Genera un token único
		token = str(uuid.uuid4())
		# Guarda el contexto en la sesión (asegúrate de que el contexto sea serializable o almacena solo los parámetros necesarios)
		self.request.session[token] = contexto_reporte
		
		# Construir la URL según el tipo de salida
		if tipo_salida == "pantalla":
			# Por ejemplo, asumamos que la URL de salida para pantalla es 'ventacompro_vista_pantalla'
			url = reverse("ventacompro_vista_pantalla") + f"?token={token}"
		elif tipo_salida == "pdf_preliminar":
			url = reverse("ventacompro_vista_pdf") + f"?token={token}&format=pdf"
		else:
			# Para otros casos, redirige a pantalla
			url = reverse("ventacompro_vista_pantalla") + f"?token={token}"
		
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


@method_decorator(login_required, name='dispatch')
class InformeTemplateView(TemplateView):
	pass