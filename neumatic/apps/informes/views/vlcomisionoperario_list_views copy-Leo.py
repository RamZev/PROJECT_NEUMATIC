# neumatic\apps\informes\views\vlcomisionoperario_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static
from decimal import Decimal

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait, landscape

from .report_views_generics import *
from apps.informes.models import VLComisionOperario
from ..forms.buscador_vlcomisionoperario_forms import BuscadorComisionOperarioForm
from utils.utils import deserializar_datos, formato_argentino, normalizar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Comisiones a Operarios"
	
	#-- Modelo.
	model = VLComisionOperario
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorComisionOperarioForm
	
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
		"nombre_operario": (40, "Operario"),
		"comprobante": (40, "Comprobante"),
		"fecha_comprobante": (40, "Fecha"),
		"id_producto_id": (180, "Código"),
		"nombre_producto_familia": (40, "Servicio"),
		"total": (40, "Total"),
		"comision_operario": (40, "%"),
		"monto_comision": (40, "Comisión"),
	}


class VLComisionOperarioInformeView(InformeFormView):
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
		operario = cleaned_data.get("operario", None)
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		
		id_operario = operario.id_operario if operario else None
		
		return VLComisionOperario.objects.obtener_datos(id_operario, fecha_desde, fecha_hasta)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando, calculando subtotales y totales generales, etc,
		tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		operario = cleaned_data.get("operario")
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		param = {
			"Operario": operario.nombre_operario if operario else "Todos",
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		dominio = f"http://{self.request.get_host()}"
		
		# **************************************************
		#-- Estructura para agrupar datos por Operario.
		datos_por_operario = {}
		
		for obj in queryset:
			#-- Identificar al Operario.
			operario_id = obj.id_operario_id
			nombre_operario = obj.nombre_operario.strip()  #-- Limpieza en caso de espacios extras.
			
			#-- Si el Operario aún no está en el diccionario, se inicializa.
			if operario_id not in datos_por_operario:
				datos_por_operario[operario_id] = {
					"id_operario": operario_id,
					"operario": nombre_operario,
					"detalle": [],
					"total_operario": Decimal(0),
				}
			
			#-- Crear el diccionario con los datos del detalle del Operario.
			detalle_data = {
				"comprobante": obj.comprobante,
				"fecha": obj.fecha_comprobante.strftime("%d/%m/%Y"),
				"id_producto_id": obj.id_producto_id,
				"nombre_producto_familia": obj.nombre_producto_familia,
				"total": obj.total,
				"comision_operario": obj.comision_operario,
				"monto_comision": obj.monto_comision,
			}
			
			#-- Agregar el detalle a la lista de detalles y acumular el total.
			datos_por_operario[operario_id]["detalle"].append(detalle_data)
			datos_por_operario[operario_id]["total_operario"] += obj.monto_comision
		
		#-- Convertir a lista los datos para iterar con más facilidad en la plantilla.
		datos_por_operario = list(datos_por_operario.values())
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": datos_por_operario,
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


def vlcomisionoperario_vista_pantalla(request):
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


def vlcomisionoperario_vista_pdf(request):
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
	headers = [
		("Comprobante", 80),
		("Fecha", 40),
		("Código", 40),
		("Servicio", 180),
		("Total", 60),
		("%", 40),
		("Comisión", 60)
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
	for operario in contexto_reporte.get("objetos", []):
		#-- Datos agrupado por.
		table_data.append([
			f"Operario: [{operario['id_operario']}] {operario['operario']}",
			"", "", "", "", "", ""
		])
		
		#-- Aplicar estilos a la fila de agrupación (fila actual).
		table_style_config.extend([
			('SPAN', (0,current_row), (-1,current_row)),
			('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold')
		])
		
		current_row += 1
		
		#-- Agregar filas del detalle.
		for det in operario['detalle']:
			table_data.append([
				det['comprobante'],
				det['fecha'],
				det['id_producto_id'],
				det['nombre_producto_familia'],
				formato_argentino(det['total']),
				f"{formato_argentino(det['comision_operario'])}%",
				formato_argentino(det['monto_comision'])
			])
			current_row += 1
		
		#-- Fila Total agrupación.
		total_operario = operario['total_operario']
		table_data.append(["", "", "", "", "", "Total Operario:", formato_argentino(total_operario)])
		
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


def vlcomisionoperario_vista_excel(request):
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
	view_instance = VLComisionOperarioInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	helper = ExportHelper(
		queryset=queryset,
		table_info=ConfigViews.header_data,
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


def vlcomisionoperario_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLComisionOperarioInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	#-- Usar el helper para exportar a CSV.
	helper = ExportHelper(
		queryset=queryset,
		table_info=ConfigViews.header_data,
		report_title=ConfigViews.report_title
	)
	csv_data = helper.export_to_csv()
	
	response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.csv"'
	
	return response
