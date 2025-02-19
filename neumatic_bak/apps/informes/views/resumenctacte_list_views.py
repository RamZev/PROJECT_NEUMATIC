# neumatic\apps\informes\views\resumenctacte_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from datetime import date, datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from django.forms.models import model_to_dict

from django.db.models.fields.related import ManyToManyField

from .report_views_generics import *
from apps.informes.models import VLResumenCtaCte
from apps.maestros.models.cliente_models import Cliente
from ..forms.buscador_resumenctacte_forms import BuscadorResumenCtaCteForm
from utils.utils import deserializar_datos


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Resumen de Cuenta Corriente"
	
	#-- Modelo.
	model = VLResumenCtaCte
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorResumenCtaCteForm
	
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
	js_file = "js/filtros_resumen_cta_cte.js"
	
	# #-- URL de la vista que genera el .zip con los informes.
	# url_zip = f"{model_string}_informe_generado"
	
	#-- URL de la vista que genera la salida a pantalla.
	url_pantalla = f"{model_string}_vista_pantalla"
	
	#-- URL de la vista que genera el .pdf.
	url_pdf = f"{model_string}_vista_pdf"
	
	#-- Plantilla Vista Preliminar Pantalla.
	reporte_pantalla = f"informes/reportes/{model_string}_list.html"
	
	#-- Plantilla Vista Preliminar PDF.
	reporte_pdf = f"informes/reportes/{model_string}_pdf.html"


class VLResumenCtaCteInformeView(InformeFormView):
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
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_pantalla": ConfigViews.url_pantalla,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def obtener_queryset(self, cleaned_data):
		resumen_pendiente = cleaned_data.get('resumen_pendiente')
		condicion_venta = cleaned_data.get('condicion_venta')
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		id_cliente = cleaned_data.get('id_cliente', None)
		
		if resumen_pendiente:
			queryset = VLResumenCtaCte.objects.obtener_fact_pendientes(id_cliente)
		else:
			if condicion_venta == "0":
				queryset = VLResumenCtaCte.objects.obtener_resumen_cta_cte(id_cliente, fecha_desde, fecha_hasta, 1, 2)
			else:
				queryset = VLResumenCtaCte.objects.obtener_resumen_cta_cte(id_cliente, fecha_desde, fecha_hasta, condicion_venta, condicion_venta)
		
		return queryset
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		resumen_pendiente = cleaned_data.get('resumen_pendiente', None)
		condicion_venta = cleaned_data.get('condicion_venta', None)
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		id_cliente = cleaned_data.get('id_cliente', None)
		observaciones = cleaned_data.get("observaciones", None)
		
		# if not fecha_desde:
		# 	fecha_desde = date(date.today().year, 1, 1)
		
		# if not fecha_hasta:
		# 	fecha_hasta = date.today()
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		#-- Obtener los datos el cliente.
		cliente_data = {}
		cliente = Cliente.objects.get(pk=id_cliente)
		cliente_data = {
			"id_cliente": cliente.id_cliente,
			"nombre_cliente": cliente.nombre_cliente,
			"domicilio_cliente": cliente.domicilio_cliente,
			"telefono_cliente": cliente.telefono_cliente,
			"codigo_postal": cliente.codigo_postal,
			"localidad": cliente.id_localidad.nombre_localidad if cliente.id_localidad else "",
			"provincia": cliente.id_provincia.nombre_provincia if cliente.id_provincia else "",
			"nombre_vendedor": cliente.id_vendedor.nombre_vendedor if cliente.id_vendedor else "",
		}
		
		# ------------------------------------------------------------------------------
		saldo_anterior = 0
		
		param = {}
		if resumen_pendiente:
			#-- Reporte Resumen de Cuenta Pendiente.
			
			#-- Plantilla Vista Preliminar Pantalla.
			ConfigViews.reporte_pantalla = 'informes/reportes/facturas_pendientes_list.html'
			
			#-- Plantilla Vista Preliminar PDF.
			ConfigViews.reporte_pdf = 'informes/reportes/facturas_pendientes_pdf.html'
			
			param["Tipo"] = "Resumen de Cuenta Pendiente"
		else:
			#-- Reporte Resumen de Cuenta Corriente.
			
			#-- Plantilla Vista Preliminar Pantalla.
			ConfigViews.reporte_pantalla = 'informes/reportes/resumen_cta_cte_list.html'
			
			#-- Plantilla Vista Preliminar PDF.
			ConfigViews.reporte_pdf = 'informes/reportes/resumen_cta_cte_pdf.html'
			
			param = {
				"Desde": fecha_desde.strftime("%d/%m/%Y"),
				"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
			}
			
			match condicion_venta:
				case "1":
					param["Condición"] = "Contado"
				case "2":
					param["Condición"] = "Cuenta Corriente"
				case "0":
					param["Condición"] = "Ambos"
			
			#-- Determinar Saldo Anterior.
			saldo_anterior_queryset = VLResumenCtaCte.objects.obtener_saldo_anterior(id_cliente, fecha_desde)
			
			#-- Extraer el saldo desde el queryset.
			saldo_anterior = next(iter(saldo_anterior_queryset), None).saldo_anterior if saldo_anterior_queryset else Decimal('0.0')
			saldo_anterior = Decimal(saldo_anterior or 0.0)  # Conversión explícita
		
		#-- Obtener el saldo total desde el último registro del queryset.
		saldo_total = queryset[-1].saldo_acumulado if queryset else 0
		
		#-- Calcular la sumatoria de los intereses.
		intereses_total = sum(item.intereses for item in queryset)
		
		#-- Convertir cada objeto del queryset a un diccionario.
		objetos_serializables = [model_to_dict(item) for item in queryset]
		# ------------------------------------------------------------------------------
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": objetos_serializables,
			'saldo_total': saldo_total,
			'intereses_total': intereses_total,
			'total_general': saldo_anterior + saldo_total + intereses_total,
			"saldo_anterior": saldo_anterior,
			'observaciones': observaciones,
			'cliente': cliente_data,
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


def vlresumenctacte_vista_pantalla(request):
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


def vlresumenctacte_vista_pdf(request):
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

# def raw_to_dict(instance):
# 	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
# 	data = instance.__dict__.copy()
# 	data.pop('_state', None)
# 	return data