# neumatic\apps\informes\views\cliente_list_views.py

from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.templatetags.static import static

from django.db.models.functions import Lower
from django.db.models import Q

#-- ReportLab:
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.platypus import Paragraph

from .report_views_generics import *
from apps.maestros.models.cliente_models import Cliente
from ..forms.buscador_cliente_forms import BuscadorClienteForm
from utils.utils import deserializar_datos, normalizar, raw_to_dict
from utils.helpers.export_helpers import ExportHelper, PDFGenerator, add_row_table


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Reporte de Clientes"
	
	#-- Modelo.
	model = Cliente
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorClienteForm
	
	#-- Aplicación asociada al modelo.
	app_label = "informes"
	
	#-- Nombre del modelo en minúsculas.
	model_string = model.__name__.lower()
	
	#-- Plantilla base.
	template_list = f'{app_label}/maestro_informe.html'
	
	#-- Vista del home del proyecto.
	home_view_name = "home"
	
	#-- Archivo JavaScript específico.
	js_file = None
	
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
	
	#-- Establecer las columnas del reporte y sus atributos.
	table_info = {
		"estatus_cliente": {
			"label": "Estatus",
			"col_width_pdf": 30,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"id_cliente": {
			"label": "Código",
			"col_width_pdf": 40,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"nombre_cliente":{
			"label": "Nombre Cliente",
			"col_width_pdf": 190,
			"pdf_paragraph": True,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"domicilio_cliente": {
			"label": "Domicilio",
			"col_width_pdf": 160,
			"pdf_paragraph": True,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"id_localidad_id": {
			"label": "Id. Localidad",
			"col_width_pdf": 0,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": False,
			"excel": True,
			"csv": True
		},
		"nombre_localidad": {
			"label": "Localidad",
			"col_width_pdf": 140,
			"pdf_paragraph": True,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"codigo_postal": {
			"label": "C.P.",
			"col_width_pdf": 40,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"codigo_iva": {
			"label": "IVA",
			"col_width_pdf": 40,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"cuit": {
			"label": "CUIT",
			"col_width_pdf": 50,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"telefono_cliente": {
			"label": "Teléfono",
			"col_width_pdf": 100,
			"pdf_paragraph": False,
			"date_format": None,
			"pdf": True,
			"excel": True,
			"csv": True
		},
	}


class ClienteInformeView(InformeFormView):
	config = ConfigViews  #-- Ahora la configuración estará disponible en self.config.
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_pantalla": ConfigViews.url_pantalla,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def obtener_queryset(self, cleaned_data):
		estatus = cleaned_data.get('estatus', 'activos')
		orden = cleaned_data.get('orden', 'nombre')
		desde = cleaned_data.get('desde', '').lower()
		hasta = cleaned_data.get('hasta', '').lower()
		vendedor = cleaned_data.get('vendedor')
		provincia = cleaned_data.get('provincia')
		localidad = cleaned_data.get('localidad')
		
		if estatus:
			match estatus:
				case "activos":
					queryset = ConfigViews.model.objects.filter(
						estatus_cliente=True
					).select_related(
						"id_localidad", "id_tipo_iva"
					)
				case "inactivos":
					queryset = ConfigViews.model.objects.filter(
						estatus_cliente=False
					).select_related(
						"id_localidad", "id_tipo_iva"
					)
				case "todos":
					queryset = ConfigViews.model.objects.all().select_related(
						"id_localidad", "id_tipo_iva"
					)
		
		if orden not in ['nombre', 'codigo']:
			orden = 'nombre'
		
		orden = "nombre_cliente" if orden == "nombre" else "id_cliente"
		
		# queryset = queryset.order_by(orden)
		
		if orden == 'nombre_cliente':
			#-- Anotar un campo en minúsculas para la comparación insensible a mayúsculas/minúsculas.
			queryset = queryset.annotate(nombre_lower=Lower('nombre_cliente'))
			
			if desde and hasta:
				#-- Filtrar clientes cuyos nombres comienzan con letras en el rango desde-hasta.
				queryset = queryset.filter(
					Q(nombre_lower__gte=desde) &  # Nombres mayor o igual a "desde"
					Q(nombre_lower__lt=chr(ord(hasta[0]) + 1))  # Menor que la siguiente letra de "hasta"
				)
			elif desde:
				#-- Filtrar solo clientes mayores o iguales a "desde".
				queryset = queryset.filter(nombre_lower__gte=desde)
			elif hasta:
				#-- Filtrar solo clientes menores que la siguiente letra de "hasta".
				queryset = queryset.filter(nombre_lower__lt=chr(ord(hasta[0]) + 1))
			
			
		elif orden == 'id_cliente':
			if desde and hasta:
				queryset = queryset.filter(id_cliente__range=(desde, hasta))
			elif desde:
				queryset = queryset.filter(id_cliente__gte=desde)
			elif hasta:
				queryset = queryset.filter(id_cliente__lte=hasta)
		
		if vendedor:
			queryset = queryset.filter(id_vendedor=vendedor.id_vendedor)
		
		if provincia:
			queryset = queryset.filter(id_provincia=provincia.id_provincia)
		
		if localidad:
			queryset = queryset.filter(id_localidad=localidad.id_localidad)
		
		queryset = queryset.order_by(orden)
		
		#-- Convertir QUERYSET a LISTA DE DICCIONARIOS con los nombres de las relaciones.
		queryset_list = []
		for obj in queryset:
			obj_dict = raw_to_dict(obj)
			#-- Agregar los nombres de las relaciones.
			obj_dict['nombre_localidad'] = obj.id_localidad.nombre_localidad if obj.id_localidad else ""
			obj_dict['codigo_postal'] = obj.id_localidad.codigo_postal if obj.id_localidad else ""
			obj_dict['codigo_iva'] = obj.id_tipo_iva.codigo_iva if obj.id_tipo_iva else ""
			queryset_list.append(obj_dict)
		
		return queryset_list
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		estatus = cleaned_data.get('estatus', 'activos')
		orden = cleaned_data.get('orden', 'nombre')
		desde = cleaned_data.get('desde', '').lower()
		hasta = cleaned_data.get('hasta', '').lower()
		vendedor = cleaned_data.get('vendedor')
		provincia = cleaned_data.get('provincia')
		localidad = cleaned_data.get('localidad')
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		dominio = f"http://{self.request.get_host()}"
		
		param_left = {
			"Vendedor": vendedor.nombre_vendedor if vendedor else "Todos",
			"Provincia": provincia.nombre_provincia if provincia else "Todas",
			"Localidad": localidad.nombre_localidad if localidad else "Todas",
		}
		param_right = {
			"Estatus": estatus,
			"Ordenado por": orden,
		}
		if desde and hasta:
			param_right.update({
				"Desde": desde,
				"Hasta": hasta,
				}
			)
		
		# **************************************************
		# **************************************************
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": queryset,
			"parametros_i": param_left,
			"parametros_d": param_right,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
		}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = kwargs.get("form") or self.get_form()
		
		context["form"] = form
		
		return context


def cliente_vista_pantalla(request):
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


def cliente_vista_pdf(request):
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
	
	#-- Extraer los campos de las columnas de la tabla (headers).
	table_info = ConfigViews.table_info
	fields = [ field for field in table_info if table_info[field]['pdf']]
	
	#-- Extraer Títulos de las columnas de la tabla (headers).
	headers_titles = [value['label'] for value in table_info.values() if value['pdf']]
	
	#-- Extraer Ancho de las columnas de la tabla.
	col_widths = [value['col_width_pdf'] for value in table_info.values() if value['pdf']]
	
	table_data = [headers_titles]
	
	#-- Estilos específicos adicionales iniciales de la tabla.
	table_style_config = [
		('ALIGN', (1,0), (1,-1), 'RIGHT'),
	]
	
	#-- Agregar los datos a la tabla.
	objetos = contexto_reporte.get("objetos", [])
	add_row_table(table_data, objetos, fields, table_info, generator)
	
	return generator.generate(table_data, col_widths, table_style_config)		


def cliente_vista_excel(request):
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
	view_instance = ClienteInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	#-- Filtrar los headers de las columnas.
	headers_titles = {field: ConfigViews.table_info[field] for field in ConfigViews.table_info if ConfigViews.table_info[field]['excel']}
	
	helper = ExportHelper(
		queryset=queryset,
		table_info=headers_titles,
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


def cliente_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = ClienteInformeView()
	view_instance.request = request
	queryset = view_instance.obtener_queryset(cleaned_data)
	
	#-- Filtrar los headers de las columnas.
	headers_titles = {field: ConfigViews.table_info[field] for field in ConfigViews.table_info if ConfigViews.table_info[field]['csv']}
	
	#-- Usar el helper para exportar a CSV.
	helper = ExportHelper(
		queryset=queryset,
		table_info=headers_titles,
		report_title=ConfigViews.report_title
	)
	csv_data = helper.export_to_csv()
	
	response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
	response["Content-Disposition"] = f'inline; filename="{ConfigViews.report_title}.csv"'
	
	return response
