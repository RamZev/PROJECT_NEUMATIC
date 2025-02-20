# neumatic\apps\informes\views\ventacompro_list_views.py

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
from collections import defaultdict

from .report_views_generics import *
from apps.informes.models import VLVentaCompro
from ..forms.buscador_ventacompro_forms import BuscadorVentaComproForm
from utils.utils import deserializar_datos


class ConfigViews:
	
	#-- Título del reporte.
	report_title = "Ventas por Comprobantes"
	
	#-- Modelo.
	model = VLVentaCompro
	
	#-- Formulario asociado al modelo.
	form_class = BuscadorVentaComproForm
	
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
	
	#-- Plantilla Vista Preliminar Pantalla.
	reporte_pantalla = f"informes/reportes/{model_string}_list.html"
	
	#-- Plantilla Vista Preliminar PDF.
	reporte_pdf = f"informes/reportes/{model_string}_pdf.html"


class VLVentaComproInformeView(InformeFormView):
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
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		sucursal = cleaned_data.get("sucursal")
		
		return VLVentaCompro.objects.obtener_venta_compro(fecha_desde, fecha_hasta, sucursal)
	
	def obtener_contexto_reporte(self, queryset, cleaned_data):
		"""
		Aquí se estructura el contexto para el reporte, agrupando los comprobantes,
		calculando subtotales y totales generales, tal como se requiere para el listado.
		"""
		
		#-- Parámetros del listado.
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		solo_totales_comprobante = cleaned_data.get("solo_totales_comprobante", False)
		sucursal = cleaned_data.get("sucursal").nombre_sucursal if cleaned_data.get("sucursal") else "Todas"
		
		param = {
			"Sucursal": sucursal,
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")		
		
		dominio = f"http://{self.request.get_host()}"
		
		#-- Agrupar y estructurar datos del queryset.
		datos_agrupados = []
		totales_generales = {"contado": Decimal(0), "cta_cte": Decimal(0)}
		agrupados = defaultdict(lambda: {
			"comprobantes": [],
			"subtotal": {
				"contado": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
				"cta_cte": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
			},
		})
		
		for item in queryset:
			tipo = item.nombre_comprobante_venta
			condicion = "contado" if item.condicion == "Contado" else "cta_cte"
			monto_total = Decimal(item.total)
			
			agrupados[tipo]["comprobantes"].append({
				"comprobante": item.comprobante,
				"fecha": item.fecha_comprobante,
				"condicion": item.condicion,
				"cliente_id": item.id_cliente_id,
				"cliente_nombre": item.nombre_cliente,
				"gravado": Decimal(item.gravado),
				"iva": Decimal(item.iva),
				"percep_ib": Decimal(item.percep_ib),
				"total": monto_total,
			})
			
			agrupados[tipo]["subtotal"][condicion]["gravado"] += Decimal(item.gravado)
			agrupados[tipo]["subtotal"][condicion]["iva"] += Decimal(item.iva)
			agrupados[tipo]["subtotal"][condicion]["percep_ib"] += Decimal(item.percep_ib)
			agrupados[tipo]["subtotal"][condicion]["total"] += monto_total
			totales_generales[condicion] += monto_total
		
		for tipo, datos in agrupados.items():
			datos_agrupados.append({"tipo": tipo, **datos})
		
		#-- Se retorna un contexto que será consumido tanto para la vista en pantalla como para la generación del PDF.
		return {
			"objetos": datos_agrupados,
			"total_general": totales_generales,
			"solo_totales_comprobante": solo_totales_comprobante,
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


def vlventacompro_vista_pantalla(request):
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


def vlventacompro_vista_pdf(request):
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
