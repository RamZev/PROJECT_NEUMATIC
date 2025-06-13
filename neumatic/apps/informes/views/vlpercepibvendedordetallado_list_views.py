# neumatic\apps\informes\views\vlpercepibvendedordetallado_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static
from decimal import Decimal

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import Paragraph

from .report_views_generics import *
from apps.informes.models import VLPercepIBVendedorDetallado
from ..forms.buscador_vlpercepibvendedordetallado_forms import BuscadorPercepIBVendedorDetalladoForm
from utils.utils import deserializar_datos, formato_argentino, format_date, normalizar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Percepciones por Vendedores - Detallado por Comprobantes"
	
	#-- Modelo.
	model = VLPercepIBVendedorDetallado
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorPercepIBVendedorDetalladoForm
	
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
	
	#-- Establecer las columnas del reporte y sus atributos.
	table_info = {
		"nombre_vendedor": {
			"label": "Vendedor",
			# "col_width_table": 0,
			"col_width_pdf": 80,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"comprobante": {
			"label": "Comprobante",
			# "col_width_table": 0,
			"col_width_pdf": 80,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"id_cliente_id": {
			"label": "Código",
			# "col_width_table": 0,
			"col_width_pdf": 40,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"nombre_cliente": {
			"label": "Cliente",
			# "col_width_table": 0,
			"col_width_pdf": 220,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"cuit": {
			"label": "C.U.I.T.",
			# "col_width_table": 0,
			"col_width_pdf": 40,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"neto": {
			"label": "Neto",
			# "col_width_table": 0,
			"col_width_pdf": 80,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
		"percep_ib": {
			"label": "Percepción",
			# "col_width_table": 0,
			"col_width_pdf": 80,
			# "pdf_paragraph": False,
			# "date_format": None,
			# "table": False,
			# "pdf": True,
			# "excel": True,
			# "csv": True
		},
	}


class VLPercepIBVendedorDetalladoInformeView(InformeFormView):
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
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		return VLPercepIBVendedorDetallado.objects.obtener_datos(fecha_desde, fecha_hasta)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		param = {
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		# **************************************************
		
		#-- Agrupar los objetos por el número de comprobante.
		grouped_data = {}
		
		for obj in queryset:
			id_vendedor = obj.id_vendedor_id  #-- Campo que agrupa los datos.
			if id_vendedor not in grouped_data:
				grouped_data[id_vendedor] = {
					'vendedor': obj.nombre_vendedor,
					'comprobantes': [],
					'total_neto': Decimal(0),
					'total_percep': Decimal(0),
				}
			#-- Añadir el comprobante al grupo.
			grouped_data[id_vendedor]['comprobantes'].append(obj)
			#-- Calcular el subtotal por vendedor.
			grouped_data[id_vendedor]['total_neto'] += obj.neto
			grouped_data[id_vendedor]['total_percep'] += obj.percep_ib
		
		#-- Convertir los datos agrupados a un formato serializable:
		#-- Se recorre cada grupo y se convierte cada producto a diccionario usando raw_to_dict.
		for vendedor, data in grouped_data.items():
			data['comprobantes'] = [raw_to_dict(comprobante) for comprobante in data['comprobantes']]
			data['total_neto'] = float(data['total_neto'])
			data['total_percep'] = float(data['total_percep'])
		
		# **************************************************
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": grouped_data,
			"parametros": param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
			# 'css_url_new': f"{dominio}{static('css/reportes_new.css')}",
		}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = kwargs.get("form") or self.get_form()
		
		context["form"] = form
		if form.errors:
			context["data_has_errors"] = True
		return context

def raw_to_dict(instance):
	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
	data = instance.__dict__.copy()
	data.pop('_state', None)
	return data


def vlpercepibvendedordetallado_vista_pantalla(request):
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


def vlpercepibvendedordetallado_vista_pdf(request):
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
	generator = CustomPDFGenerator(contexto_reporte, pagesize=portrait(A4), body_font_size=7)
	
	#-- Construir datos de la tabla:
	
	#-- Datos de las columnas de la tabla (headers).
	headers = [
		("Comprobante", 80),
		("Fecha", 40),
		("Código", 35),
		("Cliente", 220),
		("C.U.I.T.", 40),
		("Neto", 80),
		("Percep. IB", 60)
	]
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value[0] for value in headers]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value[1] for value in headers]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('ALIGN', (4,0), (-1,-1), 'RIGHT'),
	]
	
	#-- Contador de filas (empezamos en 1 porque la 0 es el header).
	current_row = 1
	
	#-- Agregar los datos a la tabla.
	datos = contexto_reporte.get("objetos", {})
	
	for id_vendedor, dato in datos.items():
		#-- Datos agrupado por.
		table_data.append([
			f"Vendedor: [{id_vendedor}] {dato['vendedor']}",
			"", "", "", "", "", ""
		])
		
		#-- Aplicar estilos a la fila de agrupación (fila actual).
		table_style_config.extend([
			('SPAN', (0,current_row), (-1,current_row)),
			('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold')
		])
		
		current_row += 1
		
		#-- Agregar filas del detalle.
		for det in dato['comprobantes']:
			table_data.append([
				det['comprobante'],
				format_date(det['fecha_comprobante']),
				det['id_cliente_id'],
				Paragraph(str(det['nombre_cliente']), generator.styles['CellStyle']),
				det['cuit'],
				formato_argentino(det['neto']),
				formato_argentino(det['percep_ib'])
			])
			current_row += 1
		
		#-- Fila Total agrupación.
		total_neto = dato['total_neto']
		total_percep = dato['total_percep']
		table_data.append(["", "", "", "", "", formato_argentino(total_neto), formato_argentino(total_percep)])
		
		#-- Aplicar estilos a la fila de total (fila actual).
		table_style_config.extend([
			('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold'),
			# ('LINEABOVE', (0,current_row), (-1,current_row), 0.5, colors.black),
		])
		
		current_row += 1
		
		#-- Fila divisoria.
		table_data.append(["", "", "", "", "", "", ""])
		table_style_config.append(
			('LINEBELOW', (0,current_row), (-1,current_row), 0.5, colors.gray),
		)
		current_row += 1
	
	return generator.generate(table_data, col_widths, table_style_config)		


def vlpercepibvendedordetallado_vista_excel(request):
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
	view_instance = VLPercepIBVendedorDetalladoInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	helper = ExportHelper(
		queryset=queryset,
		table_info=ConfigViews.table_info,
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


def vlpercepibvendedordetallado_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLPercepIBVendedorDetalladoInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	#-- Usar el helper para exportar a CSV.
	helper = ExportHelper(
		queryset=queryset,
		table_info=ConfigViews.table_info,
		report_title=ConfigViews.report_title
	)
	csv_data = helper.export_to_csv()
	
	response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.csv"'
	
	return response
