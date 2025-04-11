# neumatic\apps\informes\views\vlcomisionvendedor_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render

from django.http import HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from decimal import Decimal

from .report_views_generics import *
from apps.informes.models import VLComisionVendedor
from ..forms.buscador_vlcomisionvendedor_forms import BuscadorComisionVendedorForm
from utils.utils import deserializar_datos
from utils.helpers.export_helpers import ExportHelper


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
				"gravado": obj.gravado,
				"pje_comision": obj.pje_comision,
				"monto_comision": round((obj.gravado*obj.pje_comision)/100, 2) if obj.pje_comision != 0 else 0.00
			}
			
			#-- Agregar el detalle a la lista de detalles y acumular el total.
			datos_por_vendedor[vendedor_id]["detalle"].append(detalle_data)
			datos_por_vendedor[vendedor_id]["total_gravado_vendedor"] += obj.gravado
			datos_por_vendedor[vendedor_id]["total_comision_vendedor"] += round((obj.gravado*obj.pje_comision)/100, 2)
		
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
