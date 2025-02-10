# neumatic\apps\informes\views\list_views_generics_prop.py

import asyncio
from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed

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
	
	# async def setup(self, request, *args, **kwargs):
	# 	await sync_to_async(super().setup)(request, *args, **kwargs)
	
# 	async def trace(self, request, *args, **kwargs):
# 		# Si el método TRACE no está permitido, devolvemos http_method_not_allowed.
# 		return await self.http_method_not_allowed(request, *args, **kwargs)
# 	
# 	async def head(self, request, *args, **kwargs):
# 		# Usa la implementación síncrona de head envuelta en sync_to_async.
# 		return await sync_to_async(super().head)(request, *args, **kwargs)
# 
# 	async def options(self, request, *args, **kwargs):
# 		return await sync_to_async(super().options)(request, *args, **kwargs)
	
	async def post(self, request, *args, **kwargs):
		return await self.get(request, *args, **kwargs)
	
	async def get(self, request, *args, **kwargs):
		self.object = None
		form = await sync_to_async(self.get_form)()
		
		if request.GET and any(value for key, value in request.GET.items() if value):
			if form.is_valid():
				print("** El formulario es válido **")
				#-- Se ejecuta la consulta en un hilo aparte.
				queryset = await sync_to_async(self.obtener_queryset)(form.cleaned_data)
				#-- Obtiene el contexto del reporte; por defecto, puede ser simplemente el queryset.
				contexto_reporte = await sync_to_async(self.obtener_contexto_reporte)(queryset, form.cleaned_data)
				#-- Procesa la salida.
				return await self.procesar_reporte_async(contexto_reporte, form.cleaned_data)
			else:
				print("** El formulario NO es válido **")
				return await self.form_invalid(form)
				return await sync_to_async(self.form_invalid)(form)
		
		#-- Si no hay parámetros, se renderiza la respuesta con el formulario.
		context_data = await sync_to_async(self.get_context_data)(form=form)
		return await sync_to_async(self.render_to_response)(context_data)
	
	# # Sobrescribir http_method_not_allowed para que sea async
	# async def http_method_not_allowed(self, request, *args, **kwargs):
	# 	allowed = self._allowed_methods()
	# 	return HttpResponseNotAllowed(allowed)	
	
	# # Métodos asíncronos que envuelven a los métodos heredados síncronos:
	# async def get_context_data_async(self, **kwargs):
	# 	return await sync_to_async(super().get_context_data)(**kwargs)
	# 
	# async def render_to_response_async(self, context, **response_kwargs):
	# 	return await sync_to_async(super().render_to_response)(context, **response_kwargs)
	 
	async def form_invalid(self, form):
		#-- Obtener el contexto usando la versión síncrona de get_context_data.
		context = await sync_to_async(self.get_context_data)(form=form)
		#-- Agrega la bandera de errores.
		context["data_has_errors"] = True
		#-- Renderiza la respuesta con el contexto actualizado.
		return await sync_to_async(super().render_to_response)(context)
	
	async def procesar_reporte_async(self, contexto_reporte, cleaned_data):
		"""
		Procesa la salida según 'tipo_salida'. Por ejemplo:
		  - 'pantalla': renderiza la plantilla con el contexto.
		  - 'pdf_preliminar': genera el PDF usando la función generar_pdf.
		  - Otros: email, whatsapp (placeholders).
		"""
		tipo_salida = cleaned_data.get("tipo_salida", "pantalla").lower()

		if tipo_salida == "pantalla":
			context = await sync_to_async(self.get_context_data)(**contexto_reporte)
			return await sync_to_async(self.render_to_response)(context)
		# elif tipo_salida == "pdf_preliminar":
		#     pdf_file = generar_pdf(contexto_reporte)
		#     return HttpResponse(pdf_file, content_type="application/pdf")
		# elif tipo_salida == "email":
		#     enviar_email_reporte(contexto_reporte, cleaned_data.get("email"))
		#     return HttpResponseRedirect(self.get_success_url())
		# elif tipo_salida == "whatsapp":
		#     enviar_whatsapp_reporte(contexto_reporte, cleaned_data.get("celular"))
		#     return HttpResponseRedirect(self.get_success_url())
		else:
			context = await sync_to_async(self.get_context_data)(**contexto_reporte)
			return await sync_to_async(self.render_to_response)(context)
	
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