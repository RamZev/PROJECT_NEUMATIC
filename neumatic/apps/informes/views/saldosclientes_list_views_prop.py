# neumatic\apps\informes\views\saldosclientes_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
# from decimal import Decimal
# from datetime import date, datetime
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
# from django.forms.models import model_to_dict

#-- Recursos necesarios para generar el pdf.
from io import BytesIO
from reportlab.lib.pagesizes import A4  # o letter, según requieras
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

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
			'css_url_new': f"{dominio}{static('css/reportes_new.css')}",
			'header_bottom_left': "",
			'header_bottom_right': "header_bottom_right",
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

#-- Vista para generar el PDF con WeasyPrint. -----------------------------------
# def vlsaldosclientes_vista_pdf_prop(request):
# 	#-- Obtener el token de la querystring.
# 	token = request.GET.get("token")
# 	
# 	if not token:
# 		return HttpResponse("Token no proporcionado", status=400)
# 	
# 	#-- Obtener el contexto(datos) previamente guardados en la sesión.
# 	# contexto_reporte = deserializar_datos(request.session.pop(token, None))
# 	contexto_reporte = deserializar_datos(request.session.get(token, None))
# 	
# 	if not contexto_reporte:
# 		return HttpResponse("Contexto no encontrado o expirado", status=400)
# 	
# 	#-- Preparar la respuesta HTTP.
# 	# html_string = render_to_string("informes/reportes/mercaderiaporcliente_pdf.html", contexto_reporte, request=request)
# 	html_string = render_to_string(ConfigViews.reporte_pdf, contexto_reporte, request=request)
# 	pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
# 
# 	response = HttpResponse(pdf_file, content_type="application/pdf")
# 	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
# 	
# 	return response
#--------------------------------------------------------------------------------

#-- Vista para generar el PDF con ReportLab. ------------------------------------
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
	
	#-- Generar el PDF usando ReportLab
	pdf_file = generar_pdf_saldos_clientes(contexto_reporte, request)
	
	#-- Preparar la respuesta HTTP.
	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
	
	return response


def raw_to_dict(instance):
	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
	data = instance.__dict__.copy()
	data.pop('_state', None)
	return data


#-- Para generar el PDF. ----------------------------------------------------------------------------------
# Canvas personalizado para numerar páginas "Página xxx / yyy"
class NumberedCanvas(canvas.Canvas):
	def __init__(self, *args, **kwargs):
		super(NumberedCanvas, self).__init__(*args, **kwargs)
		self._saved_page_states = []
	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()
	def save(self):
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self.draw_page_number(num_pages)
			super(NumberedCanvas, self).showPage()
		super(NumberedCanvas, self).save()
	def draw_page_number(self, page_count):
		page_text = "Página %d / %d" % (self._pageNumber, page_count)
		self.setFont("Helvetica", 9)
		self.drawCentredString(self._pagesize[0]/2.0, 15, page_text)

# Función para dibujar header y footer en cada página
def header_footer(canvas_obj, doc):
	canvas_obj.saveState()
	width, height = doc.pagesize
	# styles = getSampleStyleSheet()
	
	# --- Header ---
	header_top_height = 50
	# Sección superior izquierda: logotipo
	logo_path = doc.contexto_reporte.get("logo_url", "")  # Asumiendo que el contexto está en doc.contexto_reporte
	logo_area_width = (width - doc.leftMargin - doc.rightMargin) * 0.25
	logo_height = 30
	logo_x = doc.leftMargin - 30
	logo_y = height - header_top_height + (header_top_height - logo_height) / 2
	try:
		canvas_obj.drawImage(logo_path, logo_x, logo_y, width=logo_area_width,
							height=logo_height, preserveAspectRatio=True, mask='auto')
	except Exception:
		canvas_obj.setFont("Helvetica", 10)
		canvas_obj.drawString(logo_x, logo_y, "[Logo]")
	
	# Sección superior derecha: título
	titulo = doc.contexto_reporte.get("titulo", "Reporte")
	font_name = "Helvetica-BoldOblique"
	font_size = 12
	available_width = width - doc.leftMargin - doc.rightMargin
	text_width = canvas_obj.stringWidth(titulo, font_name, font_size)
	
	# Reducir el tamaño de fuente si el texto excede el ancho disponible (hasta un tamaño mínimo, por ejemplo, 6)
	while text_width > available_width and font_size > 6:
		font_size -= 0.5
		text_width = canvas_obj.stringWidth(titulo, font_name, font_size)
	
	canvas_obj.setFont(font_name, font_size)
	canvas_obj.drawRightString(width - doc.rightMargin, (height - header_top_height/2)-10, titulo)

	# Mientras el texto exceda el ancho disponible, reducimos el tamaño de fuente
	while text_width > available_width and font_size > 6:
		font_size -= 0.5
		text_width = canvas_obj.stringWidth(titulo, font_name, font_size)

	canvas_obj.setFont(font_name, font_size)
	canvas_obj.drawRightString(width - doc.rightMargin, (height - header_top_height/2)-10, titulo)	
	
	# --- Header-bottom ---
	#-- Línea inferior de header-top (inicio de header-bottom).
	line_y_start = height - header_top_height  
	canvas_obj.setLineWidth(1)
	canvas_obj.setStrokeColor(colors.black)
	canvas_obj.line(doc.leftMargin, line_y_start, width - doc.rightMargin, line_y_start)	
	# ----------------------------------------------------------------------------------
	header_bottom_text_left = doc.contexto_reporte.get("header_bottom_left", "")
	
	# Contenido derecho: se construye a partir del diccionario 'parametros'
	parametros = doc.contexto_reporte.get("parametros", {})
	lines = []
	for key, value in parametros.items():
		lines.append(f"<b>{key}:</b> {value}")
	header_bottom_text_right = "<br/>".join(lines)
	
	# Definir estilos para cada sección
	p_style_left = ParagraphStyle('headerBottomLeft', fontSize=9, leading=12, alignment=TA_LEFT)
	p_style_right = ParagraphStyle('headerBottomRight', fontSize=9, leading=12, alignment=TA_RIGHT)
	
	p_left = Paragraph(header_bottom_text_left, p_style_left)
	p_right = Paragraph(header_bottom_text_right, p_style_right)
	
	available_width = (width - doc.leftMargin - doc.rightMargin) / 2.0
	# Llamar wrap() para cada Paragraph
	left_w, left_h = p_left.wrap(available_width, 100)
	right_w, right_h = p_right.wrap(available_width, 100)
	header_bottom_height = max(left_h, right_h)
	header_bottom_y = height - header_top_height - header_bottom_height
	
	p_left.drawOn(canvas_obj, doc.leftMargin, header_bottom_y)
	p_right.drawOn(canvas_obj, doc.leftMargin + available_width, header_bottom_y)
	
	#-- Dibujar línea horizontal al final del header-bottom.
	line_y_end = header_bottom_y
	canvas_obj.line(doc.leftMargin, line_y_end, width - doc.rightMargin, line_y_end)	
	# ----------------------------------------------------------------------------------
	
	# --- Footer ---
	footer_y = 15
	
	# Dibujar línea decorativa justo encima del footer:
	line_y = footer_y + 12  # 12 puntos por encima del footer
	canvas_obj.setLineWidth(1)
	canvas_obj.setStrokeColor(colors.black)
	canvas_obj.line(doc.leftMargin, line_y, width - doc.rightMargin, line_y)

	canvas_obj.setFont("Helvetica-Oblique", 9)
	canvas_obj.drawString(doc.leftMargin, footer_y, "M.A.A.Soft")
	now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
	canvas_obj.setFont("Helvetica", 9)
	canvas_obj.drawRightString(width - doc.rightMargin, footer_y, now_str)
	
	canvas_obj.restoreState()

def generar_pdf_saldos_clientes(contexto_reporte, request):
	"""
	Recibe el contexto del reporte y retorna un PDF generado con ReportLab.
	"""
	buffer = BytesIO()
	
	# Configuración del documento: tamaño, márgenes (ajusta según necesites)
	doc = BaseDocTemplate(
		buffer,
		pagesize=A4,
		leftMargin=10,
		rightMargin=10,
		topMargin=0,    # Deja espacio para header (120)
		bottomMargin=40
	)
	
	# Define el Frame para el cuerpo (ajusta la altura restando espacio para header/footer)
	frame = Frame(
		doc.leftMargin,
		doc.bottomMargin,
		doc.width,
		doc.height - 80,  # Ajusta según lo usado en header y footer
		id="body"
	)
	
	# PageTemplate con función header_footer
	template = PageTemplate(id="reportTemplate", frames=[frame], onPage=header_footer)
	doc.addPageTemplates([template])
	
	story = []
	styles = getSampleStyleSheet()
	
	# Construir datos de la tabla:
	header_data = [
		"Cliente", "Nombre", "Domicilio", "C.P.", "Localidad",
		"Teléfono", "Saldo", "1er. Comp. Pend.", "Último Pago", "Sub Cuenta"
	]
	table_data = [header_data]
	for obj in contexto_reporte.get("objetos", []):
		primer_fact = obj.get("primer_fact_impaga")
		if primer_fact:
			if isinstance(primer_fact, str):
				primer_fact = datetime.strptime(primer_fact, "%Y-%m-%d").strftime("%d/%m/%Y")
			else:
				primer_fact = primer_fact.strftime("%d/%m/%Y")
		else:
			primer_fact = ""
		ultimo_pago = obj.get("ultimo_pago")
		if ultimo_pago:
			if isinstance(ultimo_pago, str):
				try:
					ultimo_pago = datetime.strptime(ultimo_pago, "%Y-%m-%d").strftime("%d/%m/%Y")
				except Exception:
					ultimo_pago = ultimo_pago
			else:
				ultimo_pago = ultimo_pago.strftime("%d/%m/%Y")
		else:
			ultimo_pago = ""
		row = [
			obj.get("id_cliente_id", ""),
			Paragraph(obj.get("nombre_cliente", ""), styles["BodyText"]),
			Paragraph(obj.get("domicilio_cliente", ""), styles["BodyText"]),
			obj.get("codigo_postal", ""),
			Paragraph(obj.get("nombre_localidad", ""), styles["BodyText"]),
			obj.get("telefono_cliente", ""),
			"{:,.2f}".format(float(obj.get("saldo", 0))),
			primer_fact,
			ultimo_pago,
			obj.get("sub_cuenta", "")
		]
		table_data.append(row)
	
	# Crear la tabla y aplicar estilos
	table = Table(table_data, repeatRows=1)
	table_style = TableStyle([
		('BACKGROUND', (0,0), (-1,0), colors.gray),
		('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
		('ALIGN', (0,0), (-1,-1), 'CENTER'),
		('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
		('FONTSIZE', (0,0), (-1,0), 10),
		('BOTTOMPADDING', (0,0), (-1,0), 8),
		('GRID', (0,0), (-1,-1), 0.5, colors.black),
	])
	table.setStyle(table_style)
	
	story.append(table)
	
	doc.contexto_reporte = contexto_reporte
	doc.build(story, canvasmaker=NumberedCanvas)
	pdf = buffer.getvalue()
	buffer.close()
	return pdf
