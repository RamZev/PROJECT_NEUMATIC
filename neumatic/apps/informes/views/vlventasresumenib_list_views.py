# neumatic\apps\informes\views\vlventasresumenib_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static
from decimal import Decimal
from django.db.models import Sum, F, FloatField, ExpressionWrapper

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
#------------------------

from .report_views_generics import *
from apps.informes.models import VLVentasResumenIB
from apps.ventas.models.factura_models import DetalleFactura
from ..forms.buscador_vlventasresumenib_forms import BuscadorVLVentasResumenIBForm
from utils.utils import deserializar_datos, formato_argentino
from apps.maestros.templatetags.custom_tags import formato_es_ar
from utils.helpers.export_helpers import ExportHelper, PDFGenerator


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
		"provincia": (180, "Provincia"),
		"por_menor": (65, "Por Menor"),
		"reparacion": (65, "Reparación"),
		"por_mayor": (65, "Por Mayor"),
		"total_gravado": (65, "Total Gravado"),
		"iva": (65, "I.V.A."),
		"total": (65, "TOTAL"),
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
		
		# #-- Convertir a lista explícitamente (solo ids).
		# ids_provincias = list(provincias.values_list('id_provincia', flat=True)) if provincias else []
		
		#-- Convertir a diccionario usando dictionary comprehension {id: provincia}.
		ids_provincias_dict = {prov.id_provincia: prov.nombre_provincia for prov in provincias} if provincias else {}
		
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
		
		# **************************************************
		totales = {}
		id_santa_fe = 13
		sucursal_santa_fe = "Santa Fe"
		#-- Inicializar los totales como Decimals.
		tg_pmenor = Decimal(0)
		tg_reparacion = Decimal(0)
		tg_pmayor = Decimal(0)
		tg_gravado = Decimal(0)
		tg_iva = Decimal(0)
		tg_total = Decimal(0)
		
		#-- Crear el diccionario con las provincias seleccionadas para las totalizaciones.
		for id, provincia in ids_provincias_dict.items():
			totales[id] = {
				"provincia": provincia,
				"por_menor": Decimal(0),
				"reparacion": Decimal(0),
				"por_mayor": Decimal(0),
				"total_gravado": Decimal(0),
				"iva": Decimal(0),
				"total": Decimal(0),
				"gravado_bruto": Decimal(0),  # Nuevo campo para acumular
				"iva_bruto": Decimal(0)       # Nuevo campo para acumular
			}
		#-- Se agrega la provincia de Santa Fe al final.
		totales[id_santa_fe] = {
			"provincia": sucursal_santa_fe,
			"por_menor": Decimal(0),
			"reparacion": Decimal(0),
			"por_mayor": Decimal(0),
			"total_gravado": Decimal(0),
			"iva": Decimal(0),
			"total": Decimal(0),
			"gravado_bruto": Decimal(0),  # Para acumular todo el gravado de SF
			"iva_bruto": Decimal(0)       # Para acumular todo el IVA de SF
		}
		
		#-- Obtener IDs de facturas distintas a Santa Fe.
		facturas_santa_fe = [obj.id_factura for obj in queryset 
							if obj.id_provincia_id not in ids_provincias_dict]
		
		#-- Calcular servicios totales (para Santa Fe).
		servicios_totales = DetalleFactura.objects.filter(
			id_factura__in=facturas_santa_fe,
			id_producto__tipo_producto='S'
		).annotate(
			base=ExpressionWrapper(
				F('total') / (F('alic_iva')/100 + 1) * F('id_factura__id_comprobante_venta__mult_venta'),
				output_field=FloatField()
			)
		).aggregate(total_servicios=Sum('base'))['total_servicios'] or Decimal('0')
		
		#-- Calcular servicios con importe mayor al máximo (para Santa Fe).
		facturas_mayores_santa_fe = [
			obj.id_factura for obj in queryset 
			if obj.id_provincia_id not in ids_provincias_dict 
			and abs(float(obj.gravado)) > float(importe_max)
		]
		
		servicios_mayores = DetalleFactura.objects.filter(
			id_factura__in=facturas_mayores_santa_fe,
			id_producto__tipo_producto='S'
		).annotate(
			base=ExpressionWrapper(
				F('total') / (F('alic_iva')/100 + 1) * F('id_factura__id_comprobante_venta__mult_venta'),
				output_field=FloatField()
			)
		).aggregate(total_servicios=Sum('base'))['total_servicios'] or Decimal('0')
		print(f"{servicios_mayores = }")
		
		#-- Se procesa el queryset.
		for obj in queryset:
			if obj.id_provincia_id in ids_provincias_dict:
				id_prov = obj.id_provincia_id
				
				totales[id_prov]["por_mayor"] += Decimal(str(obj.gravado)).quantize(Decimal('0.00'))
				totales[id_prov]["iva"] += Decimal(str(obj.iva)).quantize(Decimal('0.00'))
				totales[id_prov]["total_gravado"] = totales[id_prov]["por_mayor"].quantize(Decimal('0.00'))  # Solo por_mayor
				totales[id_prov]["total"] = (totales[id_prov]["total_gravado"] + totales[id_prov]["iva"]).quantize(Decimal('0.00'))
				
			else:
				id_prov = id_santa_fe
				
				#-- Acumular valores brutos.
				totales[id_prov]["gravado_bruto"] += Decimal(str(obj.gravado)).quantize(Decimal('0.00'))
				totales[id_prov]["iva_bruto"] += Decimal(str(obj.iva)).quantize(Decimal('0.00'))
				
				if abs(float(obj.gravado)) > float(importe_max):
					totales[id_prov]["por_mayor"] += Decimal(str(obj.gravado)).quantize(Decimal('0.00'))
				
				totales[id_prov]["total_gravado"] += obj.gravado
				totales[id_prov]["iva"] += obj.iva
				totales[id_prov]["total_gravado"] = (totales[id_prov]["por_menor"] + totales[id_prov]["reparacion"] + totales[id_prov]["por_mayor"]).quantize(Decimal('0.00'))
				totales[id_prov]["total"] = (totales[id_prov]["total_gravado"] + totales[id_prov]["iva"]).quantize(Decimal('0.00'))
		
		#-------------------------------------
		#-- CÁLCULOS ESPECIALES PARA SANTA FE (provincia 13).
		if id_santa_fe in totales:
			#-- 1. Reparación (servicios).
			totales[id_santa_fe]["reparacion"] = Decimal(str(servicios_totales)).quantize(Decimal('0.00'))
			
			#-- 2. Ajustar por_mayor restando servicios mayores.
			totales[id_santa_fe]["por_mayor"] = (totales[id_santa_fe]["por_mayor"] - Decimal(str(servicios_mayores))).quantize(Decimal('0.00'))
			
			#-- 3. Calcular por_menor (gravado total - por_mayor - reparacion).
			totales[id_santa_fe]["por_menor"] = (totales[id_santa_fe]["gravado_bruto"] - totales[id_santa_fe]["por_mayor"] - totales[id_santa_fe]["reparacion"]).quantize(Decimal('0.00'))
			
			#-- 4. Calcular total_gravado (suma de los tres conceptos).
			totales[id_santa_fe]["total_gravado"] = (
				totales[id_santa_fe]["por_menor"] + 
				totales[id_santa_fe]["reparacion"] + 
				totales[id_santa_fe]["por_mayor"]
			).quantize(Decimal('0.00'))
			
			#-- 5. Total general (total_gravado + iva).
			totales[id_santa_fe]["iva"] = totales[id_santa_fe]["iva_bruto"].quantize(Decimal('0.00'))
			totales[id_santa_fe]["total"] = (totales[id_santa_fe]["total_gravado"] + totales[id_santa_fe]["iva"]).quantize(Decimal('0.00'))
		#-------------------------------------
		
		for p, v in totales.items():
			tg_pmenor += v["por_menor"]
			tg_reparacion += v["reparacion"]
			tg_pmayor += v["por_mayor"]
			tg_gravado += v["total_gravado"]
			tg_iva += v["iva"]
			tg_total += v["total"]
		
		# **************************************************
		
		#-- Convertir a lista los datos para iterar con más facilidad en la plantilla.
		totales = list(totales.values())
		
		#-- Serializar los datos.
		totales = serializar_datos(totales)
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": totales,
			"tg_pmenor": tg_pmenor,
			"tg_reparacion": tg_reparacion,
			"tg_pmayor": tg_pmayor,
			"tg_gravado": tg_gravado,
			"tg_iva": tg_iva,
			"tg_total": tg_total,
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


# -------------------------------------------------------------------------------------------------
def vlventasresumenib_vista_pdf(request):
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
	generator = CustomPDFGenerator(contexto_reporte, pagesize=portrait(A4))
	
	#-- Construir datos de la tabla:
	
	#-- Obtener los títulos de las columnas (headers).
	header_data = [value[1] for value in ConfigViews.header_data.values()]
	table_data = [header_data]
	
	for obj in contexto_reporte.get("objetos", []):
		
		row = [
			obj.get("provincia", ""),
			formato_es_ar(obj.get("por_menor", 0)),
			formato_es_ar(obj.get("reparacion", 0)),
			formato_es_ar(obj.get("por_mayor", 0)),
			formato_es_ar(obj.get("total_gravado", 0)),
			formato_es_ar(obj.get("iva", 0)),
			formato_es_ar(obj.get("total", 0))
		]
		table_data.append(row)
		
	#-- Agregar fila de total.
	tg_pmenor = contexto_reporte.get("tg_pmenor", 0)
	tg_reparacion = contexto_reporte.get("tg_reparacion", 0)
	tg_pmayor = contexto_reporte.get("tg_pmayor", 0)
	tg_gravado = contexto_reporte.get("tg_gravado", 0)
	tg_iva = contexto_reporte.get("tg_iva", 0)
	tg_total = contexto_reporte.get("tg_total", 0)
	
	total_row = ["Totales:", 
			  formato_es_ar(tg_pmenor),
			  formato_es_ar(tg_reparacion),
			  formato_es_ar(tg_pmayor),
			  formato_es_ar(tg_gravado),
			  formato_es_ar(tg_iva),
			  formato_es_ar(tg_total)
	]
	table_data.append(total_row)
	
	#-- Configuración específica de la tabla de datos:
	
	#-- Extrae los anchos de las columnas de la estructura ConfigViews.header_data.
	col_widths = [value[0] for value in ConfigViews.header_data.values()]
	
	#-- Estilos específicos adicionales de la tabla.
	table_style_config = [
		('ALIGN', (1,0), (-1,-1), 'RIGHT'),
		('LINEABOVE', (0, len(table_data)-1), (-1, len(table_data)-1), 0.5, colors.black),
		('FONTNAME', (0, len(table_data)-1), (-1, len(table_data)-1), 'Helvetica-Bold'),
	]
	
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
