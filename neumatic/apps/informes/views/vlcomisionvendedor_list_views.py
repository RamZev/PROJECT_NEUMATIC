# neumatic\apps\informes\views\vlcomisionvendedor_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static
from decimal import Decimal

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Paragraph

from .report_views_generics import *
from apps.informes.models import VLComisionVendedor
from ..forms.buscador_vlcomisionvendedor_forms import BuscadorComisionVendedorForm
from utils.utils import deserializar_datos, formato_argentino
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Comisión Según Facturación"
	
	#-- Modelo.
	model = VLComisionVendedor
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorComisionVendedorForm
	
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
	
	#-- Plantilla Vista Preliminar PDF.
	reporte_pdf = f"informes/reportes/{model_string}_pdf.html"
	
	#-- Establecer las columnas del reporte y sus anchos(en punto).
	header_data = {
		"id_vendedor_id": (40, "Vendedor"),
		"nombre_vendedor": (40, "Nombre"),
		"comprobante": (40, "Comprobante"),
		"fecha_comprobante": (40, "Fecha"),
		"nombre_cliente": (40, "Nombre"),
		"reventa": (40, "Reventa"),
		"id_producto_id": (40, "Código"),
		"medida": (40, "Producto"),
		"nombre_producto_marca": (180, "Marca"),
		"cantidadnombre_producto_familia": (40, "Artículo"),
		"gravado": (40, "Gravado"),
		"pje_comision": (40, "%"),
		"comision": (40, "Comisión"),
	}


class VLComisionVendedorInformeView(InformeFormView):
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
		vendedor = cleaned_data.get("vendedor", None)
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		
		id_vendedor = vendedor.id_vendedor if vendedor else None
		
		return VLComisionVendedor.objects.obtener_datos(id_vendedor, fecha_desde, fecha_hasta)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando, calculando subtotales y totales generales, etc,
		tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		vendedor = cleaned_data.get("vendedor")
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		param = {
			"Vendedor": vendedor.nombre_vendedor if vendedor else "Todos",
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		dominio = f"http://{self.request.get_host()}"
		
		
		# **************************************************
		#-- Estructura para agrupar datos por Vendedor.
		datos_por_vendedor = {}
		
		for obj in queryset:
			#-- Identificar al Vendedor.
			vendedor_id = obj.id_vendedor_id
			nombre_vendedor = obj.nombre_vendedor.strip()  #-- Limpieza en caso de espacios extras.
			
			#-- Si el Vendedor aún no está en el diccionario, se inicializa.
			if vendedor_id not in datos_por_vendedor:
				datos_por_vendedor[vendedor_id] = {
					"id_vendedor": vendedor_id,
					"vendedor": nombre_vendedor,
					"detalle": [],
					"total_gravado_vendedor": Decimal(0),
					"total_comision_vendedor": Decimal(0),
				}
			
			#-- Crear el diccionario con los datos del detalle del Vendedor.
			detalle_data = {
				"comprobante": obj.comprobante,
				"fecha": obj.fecha_comprobante.strftime("%d/%m/%Y"),
				"cliente": obj.nombre_cliente,
				"reventa": obj.reventa,
				"id_producto": obj.id_producto_id,
				"producto": obj.medida,
				"marca": obj.nombre_producto_marca,
				"articulo": obj.nombre_producto_familia,
				"gravado": obj.gravado if obj.gravado else Decimal(0),
				"pje_comision": obj.pje_comision if obj.pje_comision else Decimal(0),
				"monto_comision": Decimal(0) if not obj.pje_comision or not obj.gravado or obj.pje_comision == 0 else round((obj.gravado * obj.pje_comision)/100, 2)
			}
			
			#-- Agregar el detalle a la lista de detalles y acumular el total.
			datos_por_vendedor[vendedor_id]["detalle"].append(detalle_data)
			datos_por_vendedor[vendedor_id]["total_gravado_vendedor"] += Decimal(0) if not obj.gravado else obj.gravado
			datos_por_vendedor[vendedor_id]["total_comision_vendedor"] += Decimal(0) if not obj.pje_comision or not obj.gravado or obj.pje_comision == 0 else round((obj.gravado * obj.pje_comision)/100, 2)
		
		#-- Convertir a lista los datos para iterar con más facilidad en la plantilla.
		datos_por_vendedor = list(datos_por_vendedor.values())
		
		# **************************************************
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": datos_por_vendedor,
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


def vlcomisionvendedor_vista_pantalla(request):
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


def vlcomisionvendedor_vista_pdf(request):
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
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.pdf"'
	
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
	generator = CustomPDFGenerator(contexto_reporte, pagesize=landscape(A4))
	
	#-- Construir datos de la tabla:
	
	#-- Datos de las columnas de la tabla (headers).
	headers = [
		("Comprobante", 80),
		("Fecha", 40),
		("Cliente", 160),
		("Rvta.", 20),
		("Producto", 30),
		("Medida", 60),
		("Marca", 120),
		("Artículo", 120),
		("Gravado", 60),
		("%", 30),
		("Comisión", 60)
	]
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value[0] for value in headers]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value[1] for value in headers]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('ALIGN', (8,0), (-1,-1), 'RIGHT'),
	]
	
	#-- Contador de filas (empezamos en 1 porque la 0 es el header).
	current_row = 1
	
	#-- Agregar los datos a la tabla.
	for vendedor in contexto_reporte.get("objetos", []):
		#-- Datos agrupado por.
		table_data.append([
			f"Vendedor: [{vendedor['id_vendedor']}] {vendedor['vendedor']}",
			"", "", "", "", "", "", "", "", "", ""
		])
		
		#-- Aplicar estilos a la fila de agrupación (fila actual).
		table_style_config.extend([
			('SPAN', (0,current_row), (-1,current_row)),
			('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold')
		])
		
		current_row += 1
		
		#-- Agregar filas del detalle.
		for det in vendedor['detalle']:
			table_data.append([
				det['comprobante'],
				det['fecha'],
				Paragraph(det['cliente'], generator.styles['CellStyle']),
				det['reventa'],
				det['id_producto'],
				det['producto'],
				Paragraph(det['marca'], generator.styles['CellStyle']),
				Paragraph(det['articulo'], generator.styles['CellStyle']),
				formato_argentino(det['gravado']),
				f"{formato_argentino(det['pje_comision'])}%",
				formato_argentino(det['monto_comision'])
			])
			current_row += 1
		
		#-- Fila Total agrupación.
		total_gravado = vendedor['total_gravado_vendedor']
		total_comision = vendedor['total_comision_vendedor']
		
		table_data.append(["", "", "", "", "", "", "", 
					 "Totales:", formato_argentino(total_gravado), "", formato_argentino(total_comision)])
		
		#-- Aplicar estilos a la fila de total (fila actual).
		table_style_config.extend([
			('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold'),
			('LINEABOVE', (0,current_row), (-1,current_row), 0.5, colors.black),
		])
		
		current_row += 1
		
		#-- Fila divisoria.
		table_data.append(["", "", "", "", "", "", ""])
		# table_style_config.append(
		# 	('LINEBELOW', (0,current_row), (-1,current_row), 0.5, colors.blue),
		# )
		current_row += 1
	
	return generator.generate(table_data, col_widths, table_style_config)		

def _format_date(date_value):
	"""Helper para formatear fechas"""
	if not date_value:
		return ""
	
	if isinstance(date_value, str):
		try:
			return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
		except ValueError:
			return date_value
	else:
		return date_value.strftime("%d/%m/%Y")
# -------------------------------------------------------------------------------------------------



def vlcomisionvendedor_vista_excel(request):
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
	view_instance = VLComisionVendedorInformeView()
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


def vlcomisionvendedor_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLComisionVendedorInformeView()
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
