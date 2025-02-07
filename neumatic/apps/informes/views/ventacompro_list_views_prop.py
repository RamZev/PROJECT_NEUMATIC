# neumatic\apps\informes\views\ventacompro_list_views_prop.py
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render

from django.templatetags.static import static

# from django.http import HttpResponse, JsonResponse
# from django.views import View
# from zipfile import ZipFile
# from io import BytesIO
# from django.core.mail import EmailMessage
# from datetime import date
from decimal import Decimal
# from utils.helpers.export_helpers import ExportHelper

from datetime import datetime
# from django.template.loader import render_to_string
# from weasyprint import HTML
# from django.templatetags.static import static
from collections import defaultdict

from .list_views_generics_prop import *    # <== Cambiar acá!.
from apps.informes.models import VLVentaCompro
from ..forms.buscador_ventacompro_forms import BuscadorVentaComproForm


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
	template_list = f'{app_label}/maestro_informe_list_prop.html'
	
	# # Contexto de los datos de la lista
	# context_object_name = 'objetos'
	
	#-- Vista del home del proyecto.
	home_view_name = "home"
	
	#-- Nombre de la url.
	success_url = reverse_lazy(list_view_name)
	
	#-- Archivo JavaScript específico.
	js_file = None
	
	# #-- URL de la vista que genera el .zip con los informes.
	# url_zip = f"{model_string}_informe_generado"
	
	# #-- URL de la vista que genera el .pdf.
	# url_pdf = f"{model_string}_informe_pdf"


class VLVentaComproInformeView(InformeFormView):
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	success_url = ConfigViews.success_url
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		# "list_view_name": ConfigViews.list_view_name,
		# "table_headers": DataViewList.table_headers,
		# "table_data": DataViewList.table_data,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		# "url_zip": ConfigViews.url_zip,
		# "url_pdf": ConfigViews.url_pdf,
	}
	
	def get(self, request, *args, **kwargs):
		"""
		Maneja las solicitudes GET.
		Si se ha seleccionado una opción de salida, redirige a la vista correspondiente.
		"""
		
		tipo_salida = request.GET.get('tipo_salida', 'pantalla')
		
		print(tipo_salida)
		
		# if tipo_salida != 'pantalla' and any(value for key, value in request.GET.items() if value):
		# 	return self.redirigir_a_opcion_salida(tipo_salida)
		# else:
		# 	return redirect(reverse("ventacompro_preliminar_pantalla") + f"?{request.GET.urlencode()}")
		
		#-- Verificar si hay parámetros en la URL.
		if any(value for key, value in request.GET.items() if value):
			return self.redirigir_a_opcion_salida(tipo_salida)
		
		#-- Si no hay parámetros, mostrar solo el formulario.
		return self.render_to_response(self.get_context_data())
	
	def redirigir_a_opcion_salida(self, request, tipo_salida):
		"""
		Redirige a la vista correspondiente según la opción de salida seleccionada.
		"""
		if tipo_salida == 'pantalla':
			return redirect(reverse("ventacompro_preliminar_pantalla") + f"?{request.GET.urlencode()}")
		elif tipo_salida == 'pdf_preliminar':
			return redirect(reverse('generar_pdf') + f"?{self.request.GET.urlencode()}")
		elif tipo_salida == 'email':
			return redirect(reverse('enviar_email') + f"?{self.request.GET.urlencode()}")
		elif tipo_salida == 'whatsapp':
			return redirect(reverse('enviar_whatsapp') + f"?{self.request.GET.urlencode()}")
		else:
			return redirect(reverse('buscador_ventacompro'))	
	
	def get_queryset(self):
		"""
		Obtiene el queryset filtrado según los parámetros del formulario.
		Solo devuelve datos si el formulario ha sido enviado (si hay parámetros GET).
		"""
		
		#-- Inicializa el queryset con un queryset vacío por defecto.
		queryset = VLVentaCompro.objects.none()		
		
		#-- Comprobamos si hay datos GET (parámetros de la URL).
		if any(value for key, value in self.request.GET.items() if value):
			form = self.form_class(self.request.GET)
		else:
			form = self.form_class()  # Formulario vacío para la carga inicial
			return queryset  # No devuelve datos en la primera carga
		
		if form.is_valid():
			#-- Obtener los datos del formulario (parámetros).
			sucursal = form.cleaned_data.get('sucursal', None)
			fecha_desde = form.cleaned_data.get('fecha_desde', datetime(datetime.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', datetime.today())
			solo_totales_comprobante = form.cleaned_data.get('solo_totales_comprobante', None)
			
			#-- Aplica los filtros al queryset.
			queryset = VLVentaCompro.objects.obtener_venta_compro(
				fecha_desde, 
				fecha_hasta, 
				sucursal=sucursal
			)
			
			print(list(queryset))
			
		else:
			#-- Agregar clases css a los campos con errores.
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		"""
		Agrega el formulario y los datos filtrados al contexto.
		"""
		
		context = super().get_context_data(**kwargs)
		
		#-- Obtiene el queryset filtrado.
		queryset = self.get_queryset()
		
		#-- Obtiene el formulario.
		form = self.form_class(self.request.GET or None)
		
		#-- Agrega el formulario y los datos al contexto.
		context["form"] = form
		context["objetos"] = queryset
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class VistaPreliminarPantallaView(InformeTemplateView):
	template_name = "informes/reportes/ventacompro_list.html"
	
	def get(self, request, *args, **kwargs):
		
		# Obtener los parámetros del formulario desde la URL
		form_data = request.GET
		
		# Procesar los datos del formulario (similar a get_queryset en VLVentaComproInformeView)
		sucursal = form_data.get('sucursal')
		fecha_desde = form_data.get('fecha_desde', datetime(datetime.today().year, 1, 1))
		fecha_hasta = form_data.get('fecha_hasta', datetime.today())
		solo_totales_comprobante = form_data.get('solo_totales_comprobante', False)
		
		# Aplicar los filtros al queryset
		queryset = VLVentaCompro.objects.obtener_venta_compro(
			fecha_desde, 
			fecha_hasta, 
			sucursal=sucursal
		)
		
		param = {
			"Sucursal": sucursal.nombre_sucursal if sucursal else "Todas",
			"Desde": fecha_desde.strftime("%d/%m/%Y"),
			"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
		}
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		#-- Estructura para agrupar los datos.
		datos_agrupados = []
		totales_generales = {
			# "contado": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
			# "cta_cte": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
			"contado": Decimal(0),
			"cta_cte": Decimal(0),
		}
		
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
			
			#-- Agregar el comprobante.
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
			
			#-- Actualizar subtotales.
			agrupados[tipo]["subtotal"][condicion]["gravado"] += Decimal(item.gravado)
			agrupados[tipo]["subtotal"][condicion]["iva"] += Decimal(item.iva)
			agrupados[tipo]["subtotal"][condicion]["percep_ib"] += Decimal(item.percep_ib)
			agrupados[tipo]["subtotal"][condicion]["total"] += monto_total
			
			#-- Actualizar totales generales.
			# totales_generales[condicion]["gravado"] += Decimal(item.gravado)
			# totales_generales[condicion]["iva"] += Decimal(item.iva)
			# totales_generales[condicion]["percep_ib"] += Decimal(item.percep_ib)
			# totales_generales[condicion]["total"] += monto_total
			totales_generales[condicion] += monto_total
			
		#-- Convertir a lista para facilitar la iteración en la plantilla.
		for tipo, datos in agrupados.items():
			datos_agrupados.append({"tipo": tipo, **datos})
		
		
		dominio = f"http://{request.get_host()}"
		
		# Pasar los datos a la plantilla
		context = {
			'objetos': datos_agrupados,
			'total_general': totales_generales,
			'solo_totales_comprobante': solo_totales_comprobante,
			'parametros': param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': ConfigViews.report_title,
			'logo_url': f"{dominio}{static('img/logo_01.png')}",
			'css_url': f"{dominio}{static('css/reportes.css')}",
			
		}
		
		return render(request, self.template_name, context)