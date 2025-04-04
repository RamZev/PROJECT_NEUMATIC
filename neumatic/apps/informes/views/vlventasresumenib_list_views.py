# neumatic\apps\informes\views\vlventasresumenib_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render

from django.http import HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from decimal import Decimal

from .report_views_generics import *
from apps.informes.models import VLVentasResumenIB
from ..forms.buscador_vlventasresumenib_forms import BuscadorVLVentasResumenIBForm
from utils.utils import deserializar_datos, serializar_queryset, formato_argentino
from utils.helpers.export_helpers import ExportHelper


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Resumen de Ventas por Provincias"
	
	#-- Modelo.
	model = VLVentasResumenIB
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorVLVentasResumenIBForm
	
	#-- Aplicación asociada al modelo.
	app_label = "informes"
	
	#-- Nombre del modelo en minúsculas.
	model_string = model.__name__.lower()
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	
	#-- Plantilla base.
	template_list = f'{app_label}/maestro_informe.html'
	
	#-- Vista del home del proyecto.
	home_view_name = "home"
	
	#-- Nombre de la url.
	success_url = reverse_lazy(list_view_name)
	
	#-- Archivo JavaScript específico.
	js_file = None
	
	# #-- URL de la vista que genera el .zip con los informes.
	# url_zip = f"{model_string}_informe_generado"
	
	#-- URL de la vista que genera la salida a pantalla.
	url_pantalla = f"{model_string}_vista_pantalla"
	
	#-- URL de la vista que genera el .pdf.
	url_pdf = f"{model_string}_vista_pdf"
	
	#-- URL de la vista que genera el Excel.
	url_excel = f"{model_string}_vista_excel"
	
	#-- URL de la vista que genera el CSV.
	url_csv = f"{model_string}_vista_csv"
	
	#-- Plantilla Vista Preliminar Pantalla.
	reporte_pantalla = f"informes/reportes/{model_string}_list.html"
	
	#-- Plantilla Vista Preliminar PDF.
	reporte_pdf = f"informes/reportes/{model_string}_pdf.html"
	
	#-- Establecer las columnas del reporte y sus anchos(en punto).
	header_data = {
		"nombre_provincia": (40, "Provincia"),
		"por_menor": (180, "Por Menor"),
		"reparacion": (40, "Reparación"),
		"por_mayor": (180, "Por Mayor"),
		"total_gravado": (40, "TotalGravado"),
		"iva": (40, "I.V.A."),
		"total": (40, "Total"),
	}


class VLVentasResumenIBInformeView(InformeFormView):
	config = ConfigViews  #-- Ahora la configuración estará disponible en self.config.
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	success_url = ConfigViews.success_url
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_pantalla": ConfigViews.url_pantalla,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def obtener_queryset(self, cleaned_data):
		sucursal = cleaned_data.get("sucursal")
		anno = cleaned_data.get("anno")
		mes = cleaned_data.get("mes")
		
		id_sucursal = sucursal.id_sucursal if sucursal else None
		
		return VLVentasResumenIB.objects.obtener_datos(anno, mes, id_sucursal)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		sucursal = cleaned_data.get("sucursal")
		anno = cleaned_data.get("anno")
		mes = cleaned_data.get("mes")
		importe_max = cleaned_data.get("importe_max") or 0
		provincias = cleaned_data.get("provincias")
		
		id_sucursal = sucursal.id_sucursal if sucursal else None
		print(f"{provincias = }")
		
		#-- Convertir a lista explícitamente.
		ids_provincias = list(provincias.values_list('id_provincia', flat=True)) if provincias else []
		print(f"{ids_provincias = }")
		
		meses = {
			"01": "Enero",
			"02": "Febrero",
			"03": "Marzo",
			"04": "Abril",
			"05": "Mayo",
			"06": "Junio",
			"07": "Julio",
			"08": "Agosto",
			"09": "Septiembre",
			"10": "Octubre",
			"11": "Noviembre",
			"12": "Diciembre",
		}
		param = {
			"Sucursal": sucursal.nombre_sucursal,
			"Período": f"{meses[mes]}/{anno}",
			"Imp. máx. P/menor": formato_argentino(importe_max),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		print(f"{param = }")
		# **************************************************
		#-- Inicializar los totales como Decimals.
		total_gravado = Decimal(0)
		total_exento = Decimal(0)
		total_iva = Decimal(0)
		total_percep_ib = Decimal(0)
		total_total = Decimal(0)
		
		#-- Iterar sobre cada objeto en el queryset y acumular los totales.
		for obj in queryset:
			total_gravado   += obj.gravado
			total_exento    += obj.exento
			total_iva       += obj.iva
			total_percep_ib += obj.percep_ib
			total_total     += obj.total
		# **************************************************
		
		#-- Serializar el queryset.
		queryset_serializado = serializar_queryset(queryset)
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": queryset_serializado,
			"total_gravado": total_gravado,
			"total_exento": total_exento,
			"total_iva": total_iva,
			"total_percep_ib": total_percep_ib,
			"total_total": total_total,
			"parametros": param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
			'css_url_new': f"{dominio}{static('css/reportes_new.css')}",
		}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = kwargs.get("form") or self.get_form()
		
		context["form"] = form
		if form.errors:
			context["data_has_errors"] = True
		return context


def vlventasresumenib_vista_pantalla(request):
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


def vlventasresumenib_vista_pdf(request):
	return HttpResponse("Reporte en PDF aún no implementado.", status=400)
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
	html_string = render_to_string(ConfigViews.reporte_pdf, contexto_reporte, request=request)
	pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
	
	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
	
	return response


def vlventasresumenib_vista_excel(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	# ---------------------------------------------
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	# ---------------------------------------------
	
	#-- Instanciar la vista y obtener el queryset.
	view_instance = VLVentasResumenIBInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	helper = ExportHelper(
		queryset=queryset,
		table_headers=ConfigViews.header_data,
		report_title=ConfigViews.report_title
	)
	excel_data = helper.export_to_excel()
	
	response = HttpResponse(
		excel_data,
		content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	)
	#-- Inline permite visualizarlo en el navegador si el navegador lo soporta.
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.xlsx"'
	return response


def vlventasresumenib_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLVentasResumenIBInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	#-- Usar el helper para exportar a CSV.
	helper = ExportHelper(
		queryset=queryset,
		table_headers=ConfigViews.header_data,
		report_title=ConfigViews.report_title
	)
	csv_data = helper.export_to_csv()
	
	response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.csv"'
	
	return response



# --------------------------------

objetos = []
lista_provincias = []
totales = {}
for obj in objetos:
	
	if obj.id_provincia_id in lista_provincias:
		id_prov = obj.id_provincia_id
	else:
		id_prov = 13   # Santan Fe.
	
	if id_prov not in totales:
		totales[id_prov] = {
			"Provincia": obj.nombre_provincia,
			"Por Menor": Decimal(0),
			"Reparación": Decimal(0),
			"Por Mayor": Decimal(0),
			"Total Gravado": Decimal(0),
			"I.V.A.": Decimal(0),
			"TOTAL": Decimal(0),
		}
	
	totales[id_prov]["Por Mayor"] += obj.gravado