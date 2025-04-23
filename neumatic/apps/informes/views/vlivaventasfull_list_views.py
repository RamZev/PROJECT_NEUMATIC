# neumatic\apps\informes\views\vlivaventasfull_list_views.py

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
from apps.informes.models import VLIVAVentasFULL
from apps.maestros.models.empresa_models import Empresa
from ..forms.buscador_vlivaventasfull_forms import BuscadorVLIVAVentasFULLForm
from utils.utils import deserializar_datos, serializar_queryset, formato_argentino, format_date, normalizar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Libro de I.V.A. Ventas"
	
	#-- Modelo.
	model = VLIVAVentasFULL
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorVLIVAVentasFULLForm
	
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
	
	#-- Establecer las columnas del reporte y sus anchos(en punto).
	header_data = {
		"comprobante": (85, "Comprobante"),
		"fecha_comprobante": (50, "Fecha"),
		"nombre_cliente": (220, "Nombre"),
		"codigo_iva": (40, "Sit. IVA"),
		"cuit": (50, "CUIT"),
		"gravado": (75, "Gravado"),
		"exento": (75, "Exento"),
		"iva": (75, "I.V.A."),
		"percep_ib": (75, "Percep. IB"),
		"total": (75, "Total"),
	}


class VLIVAVentasFULLInformeView(InformeFormView):
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
		sucursal = cleaned_data.get("sucursal", None)
		anno = cleaned_data.get("anno")
		mes = cleaned_data.get("mes")
		
		id_sucursal = sucursal.id_sucursal if sucursal else None
		
		return VLIVAVentasFULL.objects.obtener_datos(id_sucursal, anno, mes)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		anno = cleaned_data.get("anno") or 0
		mes = cleaned_data.get("mes")
		folio = cleaned_data.get("folio") or 0
		
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
			"Mes": meses[mes],
			"Año": anno,
		}
		
		empresa = Empresa.objects.get(pk=1)
		datos_empresa = {
			"cuit": empresa.cuit,
			"empresa": empresa.nombre_fiscal,
			"domicilio": empresa.domicilio_empresa,
			"cp": empresa.codigo_postal,
			"provincia": empresa.id_provincia.nombre_provincia,
			"localidad": empresa.id_localidad.nombre_localidad,
			"sit_iva": empresa.id_iva.nombre_iva
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		
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
			"ultimo_folio": folio,
			"datos_empresa": datos_empresa,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': "",
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


def vlivaventasfull_vista_pantalla(request):
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


def vlivaventasfull_vista_pdf(request):
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
		
		empresa = context.get('datos_empresa')
		
		return f"""{empresa['empresa']} <br/>
				   {empresa['domicilio']} <br/>
				   <strong>C.P.:</strong> {empresa['cp']} {empresa['provincia']} - {empresa['localidad']} <br/>
				   {empresa['sit_iva']}  <strong>C.U.I.T.:</strong> {empresa['cuit']}"""
	
	#-- Método que se puede sobreescribir/extender según requerimientos.
	def _get_header_bottom_right(self, context):
		"""Añadir información adicional específica para este reporte"""
		
		params = context.get("parametros", {})
		self.folio_base = context.get("ultimo_folio", 0)
		
		try:
			self.folio_base = int(self.folio_base) if self.folio_base else 0
		except (ValueError, TypeError):
			self.folio_base = 0
		
		#-- Devolver solo los otros parámetros aquí, el folio se calculará en _draw_header_bottom_content.
		other_params = "<br/>".join([f"<b>{k}:</b> {v}" for k, v in params.items()])
		
		return other_params
	
	def _draw_header_bottom_content(self, canvas_obj, doc, left_content, right_content, start_y):
		"""Se extiende el método que dibuja el contenido del header-bottom incluyendo el folio dinámico"""
		
		#-- Calcular el folio actual basado en la página.
		current_page = getattr(canvas_obj, '_pageNumber', 1)
		folio_display = current_page if self.folio_base == 0 else self.folio_base + current_page
		
		#-- Formatear el folio con 6 dígitos y ceros a la izquierda.
		folio_formateado = str(folio_display).zfill(6)
		
		#-- Añadir el folio al contenido derecho.
		folio_info = f"<b>Folio:</b> {folio_formateado}"
		if right_content:
			right_content += f"<br/>{folio_info}"
		else:
			right_content = folio_info
		
		#-- Llamar al método original con el contenido modificado.
		super()._draw_header_bottom_content(canvas_obj, doc, left_content, right_content, start_y)


def generar_pdf(contexto_reporte):
	#-- Crear instancia del generador personalizado.
	generator = CustomPDFGenerator(contexto_reporte, pagesize=landscape(A4), body_font_size=8)
	
	#-- Construir datos de la tabla:
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value[1] for value in ConfigViews.header_data.values()]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value[0] for value in ConfigViews.header_data.values()]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('FONTSIZE', (0,0), (-1,-1), 8),
		('LEADING', (0,0), (-1,-1), 10),
		('ALIGN', (5,0), (-1,-1), 'RIGHT'),
	]
	
	#-- Agregar los datos a la tabla.
	for obj in contexto_reporte.get("objetos", []):
		table_data.append([
			obj['comprobante'],
			format_date(obj['fecha_comprobante']),
			Paragraph(str(obj['nombre_cliente']), generator.styles['CellStyle']),
			obj['codigo_iva'],
			obj['cuit'],
			formato_argentino(obj['gravado']),
			formato_argentino(obj['exento']),
			formato_argentino(obj['iva']),
			formato_argentino(obj['percep_ib']),
			formato_argentino(obj['total'])
		])
	
	#-- Fila de Totales.
	total_gravado = contexto_reporte.get('total_gravado')
	total_exento = contexto_reporte.get('total_exento')
	total_iva = contexto_reporte.get('total_iva')
	total_percep_ib = contexto_reporte.get('total_percep_ib')
	total_total = contexto_reporte.get('total_total')
	
	table_data.append(["", "", "", "", "Totales:", 
						formato_argentino(total_gravado),
						formato_argentino(total_exento),
						formato_argentino(total_iva),
						formato_argentino(total_percep_ib),
						formato_argentino(total_total),
					])
	
	#-- Aplicar estilos a la fila de total (fila actual).
	table_style_config.extend([
		('ALIGN', (0,-1), (-1,-1), 'RIGHT'),
		('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
		('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
	])
		
	return generator.generate(table_data, col_widths, table_style_config)		


def vlivaventasfull_vista_excel(request):
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
	view_instance = VLIVAVentasFULLInformeView()
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


def vlivaventasfull_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLIVAVentasFULLInformeView()
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
