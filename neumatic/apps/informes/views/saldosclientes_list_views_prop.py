# neumatic\apps\informes\views\saldosclientes_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from datetime import date, datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from django.forms.models import model_to_dict

from .report_views_generics import *
from apps.informes.models import VLSaldosClientes
from ..forms.buscador_saldosclientes_forms import BuscadorSaldosClientesForm
from utils.utils import deserializar_datos


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Saldos de Clientes"
	
	#-- Modelo.
	model = VLSaldosClientes
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorSaldosClientesForm
	
	#-- Aplicación asociada al modelo.
	app_label = "informes"
	
	#-- Nombre del modelo en minúsculas.
	model_string = model.__name__.lower()
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"  # <== vlventacompro_list
	
	#-- Plantilla base.
	template_list = f'{app_label}/maestro_informe.html'
	
	#-- Vista del home del proyecto.
	home_view_name = "home"
	
	#-- Nombre de la url.
	success_url = reverse_lazy(list_view_name)
	
	#-- Archivo JavaScript específico.
	js_file = "js/filtros_saldos_clientes.js"
	
	# #-- URL de la vista que genera el .zip con los informes.
	# url_zip = f"{model_string}_informe_generado"
	
	#-- URL de la vista que genera la salida a pantalla.
	# url_pantalla = f"{model_string}_vista_pantalla"
	url_pantalla = f"{model_string}_vista_pantalla_prop"
	
	#-- URL de la vista que genera el .pdf.
	# url_pdf = f"{model_string}_vista_pdf"
	url_pdf = f"{model_string}_vista_pdf_prop"
	
	#-- Plantilla Vista Preliminar Pantalla.
	reporte_pantalla = f"informes/reportes/{model_string}_list.html"
	
	#-- Plantilla Vista Preliminar PDF.
	reporte_pdf = f"informes/reportes/{model_string}_pdf.html"


class VLSaldosClientesInformeView_prop(InformeFormView):
	config = ConfigViews  #-- Ahora la configuración estará disponible en self.config.
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	success_url = ConfigViews.success_url
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		# "list_view_name": ConfigViews.list_view_name,
		# "table_headers": DataViewList.table_headers,
		# "table_data": DataViewList.table_data,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}_prop.html",
		"js_file": ConfigViews.js_file,
		"url_pantalla": ConfigViews.url_pantalla,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def obtener_queryset(self, cleaned_data):
		fecha_hasta = cleaned_data.get('fecha_hasta')
		vendedor = cleaned_data.get('vendedor')
		
		if vendedor:
			queryset = VLSaldosClientes.objects.obtener_saldos_clientes(fecha_hasta, vendedor.id_vendedor)
		else:
			queryset = VLSaldosClientes.objects.obtener_saldos_clientes(fecha_hasta)
		
		return queryset
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		fecha_hasta = cleaned_data.get('fecha_hasta')
		vendedor = cleaned_data.get('vendedor')
		
		param = {
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		if vendedor:
			param["Clientes del vendedor"] = vendedor.nombre_vendedor
		else:
			param["Listado"] = "Todos los Clientes"
			
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		#-- Calcular el saldo total.
		saldo_total = 0
		
		#-- Convertir cada objeto del queryset a un diccionario.
		# objetos_serializables = [model_to_dict(item) for item in queryset]
		objetos_serializables = [raw_to_dict(item) for item in queryset]
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": objetos_serializables,
			'saldo_total': saldo_total,
			"parametros": param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
		}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = kwargs.get("form") or self.get_form()
		
		context["form"] = form
		if form.errors:
			context["data_has_errors"] = True
		return context


def vlsaldosclientes_vista_pantalla_prop(request):
	#-- Obtener el token de la querystring.
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Obtener el contexto(datos) previamente guardados en la sesión.
	# contexto_reporte = request.session.pop(token, None)
	contexto_reporte = deserializar_datos(request.session.pop(token, None))
	
	if not contexto_reporte:
		return HttpResponse("Contexto no encontrado o expirado", status=400)
	
	#-- Generar el listado a pantalla.
	return render(request, ConfigViews.reporte_pantalla, contexto_reporte)
	# return render(request, "informes/reportes/mercaderiaporcliente_list.html", contexto_reporte)


def vlsaldosclientes_vista_pdf_prop(request):
	#-- Obtener el token de la querystring.
	token = request.GET.get("token")
	
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Obtener el contexto(datos) previamente guardados en la sesión.
	# contexto_reporte = deserializar_datos(request.session.pop(token, None))
	contexto_reporte = deserializar_datos(request.session.get(token, None))
	
	if not contexto_reporte:
		return HttpResponse("Contexto no encontrado o expirado", status=400)
	
	#-- Preparar la respuesta HTTP.
	# html_string = render_to_string("informes/reportes/mercaderiaporcliente_pdf.html", contexto_reporte, request=request)
	html_string = render_to_string(ConfigViews.reporte_pdf, contexto_reporte, request=request)
	pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
	
	return response



# def model_to_full_dict(instance):
# 	"""
# 	Convierte una instancia de un modelo de Django en un diccionario,
# 	incluyendo todos los campos, incluso aquellos no editables.
# 	"""
# 	data = {}
# 	for field in instance._meta.get_fields():
# 		# Excluir campos ManyToMany si es necesario
# 		if isinstance(field, ManyToManyField):
# 			continue
# 		# Obtener el valor del campo
# 		value = getattr(instance, field.name)
# 		data[field.name] = value
# 	return data

def raw_to_dict(instance):
	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
	data = instance.__dict__.copy()
	data.pop('_state', None)
	return data