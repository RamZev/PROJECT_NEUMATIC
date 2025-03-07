# neumatic\apps\informes\views\vlremitosvendedor_list_views.py

from django.urls import reverse_lazy
from django.shortcuts import render

from django.http import HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
# from django.forms.models import model_to_dict
from decimal import Decimal

from .report_views_generics import *
from apps.informes.models import VLRemitosVendedor
from ..forms.buscador_vlremitosvendedor_forms import BuscadorRemitosVendedorForm
from utils.utils import deserializar_datos, serializar_queryset
from utils.helpers.export_helpers import ExportHelper


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Remitos por Vendedor"
	
	#-- Modelo.
	model = VLRemitosVendedor
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorRemitosVendedorForm
	
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
		"id_cliente_id": (40, "Cliente"),
		"nombre_cliente": (40, "Nombre"),
		"fecha_comprobante": (40, "Fecha"),
		"comprobante": (40, "Comprobante"),
		"nombre_producto": (40, "Descripción"),
		"medida": (180, "Medida"),
		"cantidad": (40, "Cantidad"),
		"precio": (40, "Precio"),
		"total": (40, "Total"),
	}


class VLRemitosVendedorInformeView(InformeFormView):
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
	
	def transformar_cleaned_data(self, cleaned_data):
		#-- Convertir a id si existen.
		if cleaned_data.get("vendedor"):
			ven = cleaned_data["vendedor"]
			cleaned_data["vendedor"] = ven.id_vendedor
			cleaned_data["nombre_vendedor"] = ven.nombre_vendedor
		
		return cleaned_data
	
	def obtener_queryset(self, cleaned_data):
		id_vendedor = cleaned_data.get("vendedor")
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		
		return VLRemitosVendedor.objects.obtener_remitos_vendedor(id_vendedor, fecha_desde, fecha_hasta)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		vendedor = cleaned_data.get("nombre_vendedor", "")
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		param = {
			"Vendedor": vendedor,
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		
		# **************************************************
		# Estructura para agrupar datos por cliente
		datos_por_cliente = {}
		total_general = Decimal(0)
		
		for obj in queryset:
			# Identificar al cliente
			cliente_id = obj.id_cliente_id
			nombre_cliente = obj.nombre_cliente.strip()  # Limpieza en caso de espacios extras
			
			# Si el cliente aún no está en el diccionario, se inicializa
			if cliente_id not in datos_por_cliente:
				datos_por_cliente[cliente_id] = {
					# "cliente": f"[{cliente_id}] {nombre_cliente}",
					"id_cliente": cliente_id,
					"cliente": nombre_cliente,
					"comprobantes": {},
					"total_cliente": Decimal(0),
				}
			
			# Agrupar por comprobante dentro del cliente
			num_comprobante = obj.numero_comprobante
			if num_comprobante not in datos_por_cliente[cliente_id]["comprobantes"]:
				datos_por_cliente[cliente_id]["comprobantes"][num_comprobante] = {
					"fecha": obj.fecha_comprobante.strftime("%d/%m/%Y"),
					"fecha_order": obj.fecha_comprobante,  # Para ordenar por fecha
					"numero_comprobante": num_comprobante,   # Para ordenar por número
					"comprobante": obj.comprobante,
					"productos": [],
					"total_comprobante": Decimal(0),
				}
			
			#-- Crear el diccionario con los datos requeridos para el reporte.
			producto_data = {
				"fecha": obj.fecha_comprobante.strftime("%d/%m/%Y"),
				"comprobante": obj.comprobante,
				"descripcion": obj.nombre_producto,
				"medida": obj.medida,
				"cantidad": obj.cantidad,
				"precio": obj.precio,
				"total": obj.total,
			}
			
			#-- Agregar el producto a la lista del comprobante y acumular totales.
			datos_por_cliente[cliente_id]["comprobantes"][num_comprobante]["productos"].append(producto_data)
			datos_por_cliente[cliente_id]["comprobantes"][num_comprobante]["total_comprobante"] += obj.total
			datos_por_cliente[cliente_id]["total_cliente"] += obj.total
			total_general += obj.total
		
		#-- Convertir la estructura de diccionarios a listas ordenadas para iterar en el template.
		datos = []
		for cliente_info in datos_por_cliente.values():
			#-- Convertir comprobantes (diccionario) a lista y ordenarlos por (fecha, número de comprobante).
			comprobantes_list = list(cliente_info["comprobantes"].values())
			comprobantes_list.sort(key=lambda x: (x["fecha_order"], x["numero_comprobante"]))
			cliente_info["comprobantes"] = comprobantes_list
			
			#-- Convertir los totales a float para facilitar el formateo en el template.
			cliente_info["total_cliente"] = float(cliente_info["total_cliente"])
			for comp in cliente_info["comprobantes"]:
				comp["total_comprobante"] = float(comp["total_comprobante"])
			datos.append(cliente_info)

		#-- Ordenar la lista de datos por el nombre del cliente.
		datos.sort(key=lambda x: x["cliente"])
		# **************************************************
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": datos,
			"total_general": float(total_general),
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

def raw_to_dict(instance):
	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
	data = instance.__dict__.copy()
	data.pop('_state', None)
	return data


def vlremitosvendedor_vista_pantalla(request):
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
	# return render(request, "informes/reportes/ventacompro_list.html", contexto_reporte)


def vlremitosvendedor_vista_pdf(request):
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
	# html_string = render_to_string("informes/reportes/ventacompro_pdf.html", contexto_reporte, request=request)
	html_string = render_to_string(ConfigViews.reporte_pdf, contexto_reporte, request=request)
	pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
	
	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
	
	return response


def vlremitosvendedor_vista_excel(request):
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
	view_instance = VLRemitosVendedorInformeView()
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
	# Inline permite visualizarlo en el navegador si el navegador lo soporta.
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.xlsx"'
	return response


def vlremitosvendedor_vista_csv(request):
	token = request.GET.get("token")
	if not token:
		return HttpResponse("Token no proporcionado", status=400)
	
	#-- Recuperar los parámetros de filtrado desde la cache.
	data = cache.get(token)
	if not data or "cleaned_data" not in data:
		return HttpResponse("Datos no encontrados o expirados", status=400)
	
	cleaned_data = data["cleaned_data"]
	
	#-- Instanciar la vista para reejecutar la consulta y obtener el queryset.
	view_instance = VLRemitosVendedorInformeView()
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
