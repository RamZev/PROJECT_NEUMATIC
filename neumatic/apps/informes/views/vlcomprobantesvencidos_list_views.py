# neumatic\apps\informes\views\vlcomprobantesvencidos_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.platypus import Paragraph

from .report_views_generics import *
from apps.informes.models import VLComprobantesVencidos
from ..forms.buscador_vlcomprobantesvencidos_forms import BuscadorComprobantesVencidosForm
from utils.utils import deserializar_datos, serializar_queryset, formato_argentino, format_date, normalizar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Comprobantes Vencidos"
	
	#-- Modelo.
	model = VLComprobantesVencidos
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorComprobantesVencidosForm
	
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
	
	#-- Establecer las columnas del reporte y sus anchos(en punto).
	header_data = {
		"fecha_comprobante": (40, "Fecha"),
		"dias_vencidos": (30, "Días"),
		"comprobante": (80, "Número"),
		"id_cliente_id": (30, "Cliente"),
		"nombre_cliente": (180, "Nombre"),
		"total": (60, "Total Comprobante"),
		"entrega": (60, "Entrega a Cta."),
		"saldo": (60, "Saldo Pendiente"),
	}


class VLComprobantesVencidosInformeView(InformeFormView):
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
		dias = cleaned_data.get("dias") or 0
		vendedor = cleaned_data.get("vendedor", None)
		sucursal = cleaned_data.get('sucursal', None)
		
		id_vendedor = vendedor.id_vendedor if vendedor else None
		id_sucursal = sucursal.id_sucursal if sucursal else None
		
		return VLComprobantesVencidos.objects.obtener_compro_vencidos(dias, id_vendedor, id_sucursal)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		dias = cleaned_data.get("dias") or 0
		vendedor = cleaned_data.get("vendedor", None)
		sucursal = cleaned_data.get('sucursal', None)
		
		param = {
			"Vendedor": vendedor.nombre_vendedor if vendedor else "Todos",
			"Sucursal": sucursal.nombre_sucursal if sucursal else "Todas",
			"Antigüedad mayor a (días)": dias,
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		#-- Convertir cada objeto del queryset a un diccionario.
		objetos_serializables = serializar_queryset(queryset)
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": objetos_serializables,
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


def vlcomprobantesvencidos_vista_pantalla(request):
	#-- Obtener el token de la querystring.
	token = request.GET.get("token")
	
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Obtener el contexto(datos) previamente guardados en la sesión.
	contexto_reporte = deserializar_datos(request.session.pop(token, None))
	
	if not contexto_reporte:
		return HttpResponse("Contexto no encontrado o expirado", status=400)
	
	#-- Generar el listado a pantalla.
	return render(request, ConfigViews.reporte_pantalla, contexto_reporte)


def vlcomprobantesvencidos_vista_pdf(request):
	#-- Obtener el token de la querystring.
	token = request.GET.get("token")
	
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Obtener el contexto(datos) previamente guardados en la sesión.
	# contexto_reporte = deserializar_datos(request.session.pop(token, None))
	contexto_reporte = deserializar_datos(request.session.get(token, None))
	
	if not contexto_reporte:
		return HttpResponse("Contexto no encontrado o expirado", status=400)
	
	#-- Generar el PDF usando ReportLab
	pdf_file = generar_pdf(contexto_reporte)
	
	#-- Preparar la respuesta HTTP.
	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="{normalizar(ConfigViews.report_title)}.pdf"'
	
	return response

class CustomPDFGenerator(PDFGenerator):
	#-- Método que se puede sobreescribir/extender según requerimientos.
	# def _get_header_bottom_left(self, context):
	# 	"""Personalización del Header-bottom-left"""
	# 	
	# 	# custom_text = context.get("texto_personalizado", "")
	# 	# 
	# 	# if custom_text:
	# 	# 	return f"<b>NOTA:</b> {custom_text}"
	# 	
	# 	id_cliente = 10025
	# 	cliente = "Leoncio R. Barrios H."
	# 	domicilio = "Jr. San Pedro 1256. Surquillo, Lima."
	# 	Telefono = "971025647"
	# 	
	# 	# return f"Cliente: [{id_cliente}] {cliente} <br/> {domicilio}"
	# 	# return f"Cliente: [{id_cliente}] {cliente} <br/> {domicilio} <br/> Tel. {Telefono} <br/>"
	# 	return f"Cliente: [{id_cliente}] {cliente} <br/> {domicilio} <br/> Tel. {Telefono} <br/> Tel. {Telefono} "
	# 	# return f"Cliente: [{id_cliente}] {cliente} <br/> {domicilio} <br/> Tel. {Telefono} <br/> Tel. {Telefono} <br/> Tel. {Telefono}"
	# 	
	# 	# return super()._get_header_bottom_left(context)
	
	#-- Método que se puede sobreescribir/extender según requerimientos.
	# def _get_header_bottom_right(self, context):
	# 	"""Añadir información adicional específica para este reporte"""
	# 	base_content = super()._get_header_bottom_right(context)
	# 	saldo_total = context.get("saldo_total", 0)
	# 	return f"""
	# 		{base_content}<br/>
	# 		<b>Total General:</b> {formato_es_ar(saldo_total)}
	# 	"""
	pass

def generar_pdf(contexto_reporte):
	#-- Crear instancia del generador personalizado.
	generator = CustomPDFGenerator(contexto_reporte, pagesize=portrait(A4))
	
	#-- Construir datos de la tabla:
	
	#-- Datos de las columnas de la tabla (headers).
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value[1] for value in ConfigViews.header_data.values()]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value[0] for value in ConfigViews.header_data.values()]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('ALIGN', (1,0), (1,-1), 'RIGHT'),
		('ALIGN', (5,0), (-1,-1), 'RIGHT'),
	]
	
	#-- Agregar los datos a la tabla.
	for obj in contexto_reporte.get("objetos", []):
		table_data.append([
			format_date(obj['fecha_comprobante']),
			obj['dias_vencidos'],
			obj['comprobante'],
			obj['id_cliente_id'],
			Paragraph(str(obj['nombre_cliente']), generator.styles['CellStyle']),
			formato_argentino(obj['total']),
			formato_argentino(obj['entrega']),
			formato_argentino(obj['saldo'])
		])
	
	return generator.generate(table_data, col_widths, table_style_config)		


def vlcomprobantesvencidos_vista_excel(request):
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
	view_instance = VLComprobantesVencidosInformeView()
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
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.xlsx"'
	
	return response


def vlcomprobantesvencidos_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLComprobantesVencidosInformeView()
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
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.csv"'
	
	return response
