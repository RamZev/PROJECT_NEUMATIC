# neumatic\apps\informes\views\vlventamostrador_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static
from django.forms.models import model_to_dict

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import Paragraph

from .report_views_generics import *
from apps.informes.models import VLVentaMostrador
from ..forms.buscador_vlventamostrador_forms import BuscadorVentaMostradorForm
from utils.utils import deserializar_datos, formato_argentino, format_date, normalizar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Ventas por Mostrador"
	
	#-- Modelo.
	model = VLVentaMostrador
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorVentaMostradorForm
	
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
		"fecha_comprobante": (45, "Fecha"),
		"comprobante": (80, "Comprobante"),
		"id_cliente_id": (35, "Cliente"),
		"nombre_cliente": (190, "Nombre"),
		"reventa": (20, "Rta."),
		"tipo_producto": (20, "T/P"),
		"id_producto_id": (30, "Código"),
		"nombre_producto": (200, "Descripción"),
		"cantidad": (40, "Cantidad"),
		"precio": (70, "Precio"),
		"total": (80, "Total")
	}


class VLVentaMostradorInformeView(InformeFormView):
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
		sucursal = cleaned_data.get('sucursal', None)
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		tipo_venta = cleaned_data.get('tipo_venta', None)
		tipo_cliente = cleaned_data.get('tipo_cliente', None)
		tipo_producto = cleaned_data.get('tipo_producto', None)
		datos_cliente = cleaned_data.get('datos_cliente', None)
		
		return VLVentaMostrador.objects.obtener_venta_mostrador(
			fecha_desde, 
			fecha_hasta, 
			sucursal=sucursal, 
			tipo_venta=tipo_venta, 
			tipo_cliente=tipo_cliente, 
			tipo_producto=tipo_producto
		)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		sucursal = cleaned_data.get('sucursal', None)
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		tipo_venta = cleaned_data.get('tipo_venta', None)
		tipo_cliente = cleaned_data.get('tipo_cliente', None)
		tipo_producto = cleaned_data.get('tipo_producto', None)
		datos_cliente = cleaned_data.get('datos_cliente', None)
		
		tipo_venta_dict = {"T": "Todas", "M": "Mostrador", "R": "Reventa"}
		tipo_cliente_dict = {"T": "Todos", "M": "Minoristas", "R": "Revendedores"}
		tipo_producto_dict = {"T": "Todos", "P": "Producto", "S": "Servicio"}
		
		param_right = {
			"Sucursal": sucursal.nombre_sucursal if sucursal else "Todas",
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		param_left = {
			"Tipo Venta": tipo_venta_dict.get(tipo_venta, "Desconocido"),
			"Tipo Cliente": tipo_cliente_dict.get(tipo_cliente, "Desconocido"),
			"Tipo Producto": tipo_producto_dict.get(tipo_producto, "Desconocido"),
		}

		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		#-- Calcular el total general.
		total_general = sum(item.total for item in queryset if hasattr(item, "total"))
		
		#-- Convertir cada objeto del queryset a un diccionario.
		objetos_serializables = [model_to_dict(item) for item in queryset]		
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": objetos_serializables,
			"total_general": total_general,
			"parametros_i": param_left,
			"parametros_d": param_right,
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


def vlventamostrador_vista_pantalla(request):
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


def vlventamostrador_vista_pdf(request):
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
	def _get_header_bottom_left(self, context):
		"""Personalización del Header-bottom-left"""
		
		params = context.get("parametros_i", {})
		
		return "<br/>".join([f"<b>{k}:</b> {v}" for k, v in params.items()])		
	
	#-- Método que se puede sobreescribir/extender según requerimientos.
	def _get_header_bottom_right(self, context):
		"""Añadir información adicional específica para este reporte"""
		
		params = context.get("parametros_d", {})
		
		return "<br/>".join([f"<b>{k}:</b> {v}" for k, v in params.items()])
		

def generar_pdf(contexto_reporte):
	#-- Crear instancia del generador personalizado.
	generator = CustomPDFGenerator(contexto_reporte, pagesize=landscape(A4), body_font_size=7)
	
	#-- Construir datos de la tabla:
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value[1] for value in ConfigViews.header_data.values()]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value[0] for value in ConfigViews.header_data.values()]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('ALIGN', (8,0), (-1,-1), 'RIGHT'),
	]
	
	#-- Contador de filas (empezamos en 1 porque la 0 es el header).
	current_row = 1
	
	#-- Agregar los datos a la tabla.
	objetos = contexto_reporte.get("objetos", [])
	previous_comprobante = None
	
	for obj in objetos:
		#-- Agregar filas del detalle.
		current_comprobante = obj['comprobante']
		if current_comprobante != previous_comprobante:
			table_data.append([
				format_date(obj['fecha_comprobante']),
				obj['comprobante'],
				obj['id_cliente_id'],
				Paragraph(str(obj['nombre_cliente']), generator.styles['CellStyle']),
				obj['reventa'],
				obj['tipo_producto'],
				obj['id_producto_id'],
				Paragraph(str(obj['nombre_producto']), generator.styles['CellStyle']),
				formato_argentino(obj['cantidad']),
				formato_argentino(obj['precio']),
				formato_argentino(obj['total'])
			])
		else:
			table_data.append([
				"",
				"",
				"",
				"",
				"",
				obj['tipo_producto'],
				obj['id_producto_id'],
				Paragraph(str(obj['nombre_producto']), generator.styles['CellStyle']),
				formato_argentino(obj['cantidad']),
				formato_argentino(obj['precio']),
				formato_argentino(obj['total'])
			])
		previous_comprobante = current_comprobante
		
		current_row += 1
			
	#-- Fila Total General.
	table_data.append(["", "", "", "", "", "", "", "", "", "Total General:", formato_argentino(contexto_reporte.get('total_general'))])
	
	#-- Aplicar estilos a la fila de total (fila actual).
	table_style_config.extend([
		('FONTNAME', (0,current_row), (-1,current_row), 'Helvetica-Bold'),
		('LINEABOVE', (0,current_row), (-1,current_row), 0.5, colors.black),
	])
	
	return generator.generate(table_data, col_widths, table_style_config)		


def vlventamostrador_vista_excel(request):
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
	view_instance = VLVentaMostradorInformeView()
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


def vlventamostrador_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLVentaMostradorInformeView()
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
