# # neumatic\apps\informes\views\totalremitosclientes_list_views.py

# from django.urls import reverse_lazy, reverse
# from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.shortcuts import render

from django.http import HttpResponse
# from django.views import View
# from zipfile import ZipFile
# from io import BytesIO
# from django.core.mail import EmailMessage
# from datetime import date
from decimal import Decimal
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from django.forms.models import model_to_dict

from .report_views_generics import *
from apps.informes.models import VLRemitosClientes
from apps.maestros.models.cliente_models import Cliente
from ..forms.buscador_remitosclientes_forms import BuscadorRemitosClientesForm
from utils.utils import deserializar_datos


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Remitos por Cliente"
	
	#-- Modelo.
	model = VLRemitosClientes
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorRemitosClientesForm
	
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


class VLRemitosClientesInformeView(InformeFormView):
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
		# "buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_pantalla": ConfigViews.url_pantalla,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def obtener_queryset(self, cleaned_data):
		id_cliente = cleaned_data.get('id_cliente', None)
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		queryset = VLRemitosClientes.objects.obtener_remitos_por_cliente(id_cliente, fecha_desde, fecha_hasta)
		
		return queryset
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		id_cliente = cleaned_data.get('id_cliente', None)
		fecha_desde = cleaned_data.get('fecha_desde')
		fecha_hasta = cleaned_data.get('fecha_hasta')
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		param = {
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		#-- Obtener los datos el cliente.
		cliente_data = {}
		cliente = Cliente.objects.get(pk=id_cliente)
		cliente_data = {
			"id_cliente": cliente.id_cliente,
			"nombre_cliente": cliente.nombre_cliente,
		}
		
		# Agrupar los objetos por el número de comprobante.
		grouped_data = {}
		total_general = Decimal(0)
		
		for obj in queryset:
			comprobante_num = obj.numero_comprobante  # Campo que agrupa los datos.
			if comprobante_num not in grouped_data:
				grouped_data[comprobante_num] = {
					'productos': [],
					'subtotal': Decimal(0),
				}
			# Añadir el producto al grupo.
			grouped_data[comprobante_num]['productos'].append(obj)
			# Calcular el subtotal por comprobante.
			grouped_data[comprobante_num]['subtotal'] += obj.total
			# Acumular el total general.
			total_general += obj.total
		
		# Convertir cada grupo a un diccionario serializable.
		objetos_serializables = []
		for comprobante, data in grouped_data.items():
			# Convertir cada producto a diccionario usando raw_to_dict en lugar de model_to_dict.
			productos_serializables = [raw_to_dict(producto) for producto in data['productos']]
			objetos_serializables.append({
				'numero_comprobante': comprobante,
				'productos': productos_serializables,
				'subtotal': float(data['subtotal']),  # Convertir a float para la serialización.
			})	
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": objetos_serializables,
			"total_general": total_general,
			'cliente': cliente_data,
			"parametros": param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
		}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = kwargs.get("form") or self.get_form()
		
		context["form"] = form
		if form.errors:
			context["data_has_errors"] = True
		return context


def vlremitosclientes_vista_pantalla(request):
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
	return render(request, "informes/reportes/remitosclientes_list.html", contexto_reporte)


def vlremitosclientes_vista_pdf(request):
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
	html_string = render_to_string("informes/reportes/remitosclientes_pdf.html", contexto_reporte, request=request)
	pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

	response = HttpResponse(pdf_file, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
	
	return response



def raw_to_dict(instance):
	"""Convierte una instancia de una consulta raw a un diccionario, eliminando claves internas."""
	data = instance.__dict__.copy()
	data.pop('_state', None)
	return data