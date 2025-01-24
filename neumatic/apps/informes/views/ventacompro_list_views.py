# neumatic\apps\informes\views\totalremitosclientes_list_views.py
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views import View
from zipfile import ZipFile
from io import BytesIO
from django.core.mail import EmailMessage
from datetime import date
from decimal import Decimal
from utils.helpers.export_helpers import ExportHelper

from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static
from collections import defaultdict
import pprint

from .list_views_generics import *
from apps.informes.models import VLVentaCompro
from ..forms.buscador_ventacompro_forms import BuscadorVentaComproForm


class ConfigViews:
	# Modelo
	model = VLVentaCompro
	
	# Formulario asociado al modelo
	form_class = BuscadorVentaComproForm
	
	# Aplicación asociada al modelo
	app_label = "informes"
	
	# Nombre del modelo en minúsculas
	model_string = model.__name__.lower()
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	
	# Plantilla de la lista del CRUD
	template_list = f'{app_label}/maestro_informe_list.html'
	
	# Contexto de los datos de la lista
	context_object_name = 'objetos'
	
	# Vista del home del proyecto
	home_view_name = "home"
	
	# Nombre de la url 
	success_url = reverse_lazy(list_view_name)
	
	# Archivo JavaScript específico.
	js_file = None
	
	# URL de la vista que genera el .zip con los informes.
	url_zip = f"{model_string}_informe_generado"
	
	# URL de la vista que genera el .pdf.
	url_pdf = f"{model_string}_informe_pdf"


class DataViewList:
	# search_fields = ['nombre_cliente', 'cuit']
	
	# ordering = ['nombre_cliente']
	
	paginate_by = 8
	
	report_title = "Ventas por Comprobantes"
	
	table_headers = {
		'comprobante': (2, 'Comprobante'),
		'fecha_comprobante': (1, 'Fecha'),
		'condicion': (1, 'Condición'),
		'id_cliente_id': (1, 'Cliente'),
		'nombre_cliente': (2, 'Nombre'),
		'gravado': (1, 'Gravado'),
		'iva': (2, 'IVA'),
		'percep_ib': (1, 'Percepp. IB'),
		'total': (1, 'Total'),
	}
	
	table_data = [
		{'field_name': 'comprobante', 'date_format': None},
		{'field_name': 'fecha_comprobante', 'date_format': 'd/m/Y'},
		{'field_name': 'condicion', 'date_format': None},
		{'field_name': 'id_cliente_id', 'date_format': None},
		{'field_name': 'nombre_cliente', 'date_format': None},
		{'field_name': 'gravado', 'date_format': None},
		{'field_name': 'iva', 'date_format': None},
		{'field_name': 'percep_ib', 'date_format': None},
		{'field_name': 'total', 'date_format': None},
	]
	
	#-- Texto de totalización y Columnas a totalizar.
	# total_columns = {"Total Pendiente: ": ['saldo']}


class VLVentaComproInformeListView(InformeListView):
	model = ConfigViews.model
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	# search_fields = DataViewList.search_fields
	# ordering = DataViewList.ordering
	
	extra_context = {
		"master_title": f'Informes - {ConfigViews.model._meta.verbose_name_plural}',
		"home_view_name": ConfigViews.home_view_name,
		"list_view_name": ConfigViews.list_view_name,
		"table_headers": DataViewList.table_headers,
		"table_data": DataViewList.table_data,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_zip": ConfigViews.url_zip,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def get_queryset(self):
		# queryset = super().get_queryset()
		
		#-- Inicializa el queryset con un queryset vacío por defecto.
		queryset = VLVentaCompro.objects.none()		
		
		# form = self.form_class(self.request.GET)
		
		# Comprobamos si hay datos GET (parámetros de la URL)
		if any(value for key, value in self.request.GET.items() if value):
			form = BuscadorVentaComproForm(self.request.GET)
		else:
			form = BuscadorVentaComproForm()  # Formulario vacío para la carga inicial
		
		if form.is_valid():
			sucursal = form.cleaned_data.get('sucursal', None)
			fecha_desde = form.cleaned_data.get('fecha_desde', date(date.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', date.today())
			totales_comprobante = form.cleaned_data.get('totales_comprobante', None)
			
			if not fecha_desde:
				fecha_hasta = date(date.today().year, 1, 1)
			
			if not fecha_hasta:
				fecha_hasta = date.today()
			
			queryset = VLVentaCompro.objects.obtener_venta_compro(
				fecha_desde, 
				fecha_hasta, 
				sucursal=sucursal
			)
			
		else:
			#-- Agregar clases css a los campos con errores.
			# print("El form no es válido (desde la vista)")
			# print(f"{form.errors = }")
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorVentaComproForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class VLVentaComproInformesView(View):
	"""Vista para gestionar informes de clientes, exportaciones y envíos por correo."""
	
	def get(self, request, *args, **kwargs):
		"""Gestión de solicitudes GET."""
		
		#-- "email" o "download".
		action = request.GET.get("action", "download")
		
		#-- Formatos seleccionados por el usuario.
		formatos = request.GET.getlist("formato_envio")
		
		#-- Email si aplica envío.
		email = request.GET.get("email", "")
		
		#-- Obtener el queryset filtrado.
		queryset_filtrado = VLVentaComproInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Generar y retornar el archivo ZIP.
		if action == "email":
			#-- Manejar el envío por correo electrónico.
			return self.enviar_por_email(queryset, formatos, email)
		else:
			#-- Manejar la generación y descarga del archivo ZIP.
			return self.generar_archivos_zip(queryset, formatos)
	
	def generar_archivos_zip(self, queryset, formatos):
		"""Generar un archivo ZIP con los formatos seleccionados."""
		
		buffer = BytesIO()
		with ZipFile(buffer, "w") as zip_file:
			helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title, DataViewList.total_columns)
			
			#-- Generar los formatos seleccionados.
			if "pdf" in formatos:
				pdf_content = helper.export_to_pdf()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.pdf", pdf_content)
			
			if "csv" in formatos:
				csv_content = helper.export_to_csv()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.csv", csv_content)
			
			if "word" in formatos:
				word_content = helper.export_to_word()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.docx", word_content)
			
			if "excel" in formatos:
				excel_content = helper.export_to_excel()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.xlsx", excel_content)
		
		#-- Preparar respuesta para descargar el archivo ZIP.
		buffer.seek(0)
		response = HttpResponse(buffer, content_type="application/zip")
		response["Content-Disposition"] = f'attachment; filename="informe_{ConfigViews.model_string}.zip"'
		
		return response
	
	def enviar_por_email(self, queryset, formatos, email):
		"""Enviar los informes seleccionados por correo electrónico."""
		helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title, DataViewList.total_columns)
		attachments = []
		
		#-- Generar los formatos seleccionados y añadirlos como adjuntos.
		if "pdf" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.pdf", helper.generar_pdf(), 
					   "application/pdf"))
		
		if "csv" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.csv", helper.generar_csv(), 
					   "text/csv"))
		
		if "word" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.docx", helper.generar_word(), 
					   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
		
		if "excel" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.xlsx", helper.generar_excel(), 
					   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
		
		#-- Crear y enviar el correo.
		subject = DataViewList.report_title
		body = "Adjunto encontrarás el informe solicitado."
		email_message = EmailMessage(subject, body, to=[email])
		for filename, content, mime_type in attachments:
			email_message.attach(filename, content, mime_type)
		
		email_message.send()
		
		#-- Responder con un mensaje de éxito.
		return JsonResponse({"success": True, "message": "Informe enviado correctamente al correo."})


class VLVentaComproInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset ya filtrado.
		queryset_filtrado = VLVentaComproInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Inicializar el formulario con los datos GET.
		form = BuscadorVentaComproForm(request.GET or None)
		
		if form.is_valid():
			sucursal = form.cleaned_data.get('sucursal', None)
			fecha_desde = form.cleaned_data.get('fecha_desde', date(date.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', date.today())
			totales_comprobante = form.cleaned_data.get('totales_comprobante', None)
			
			reporte = 'informes/reportes/ventacompro_pdf.html'
			
			param = {
				"Sucursal": sucursal.nombre_sucursal if sucursal else "Todas",
				"Desde": fecha_desde,
				"Hasta": fecha_hasta,
			}
			
			fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			
			#-- Estructura para agrupar los datos.
			datos = defaultdict(lambda: {
				"comprobantes": [],
				"subtotal": {
					"contado": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
					"cta_cte": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
				},
			})
			
			#-- Total general.
			total_general = {
				"contado": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
				"cta_cte": {"gravado": Decimal(0), "iva": Decimal(0), "percep_ib": Decimal(0), "total": Decimal(0)},
			}
			
			for item in queryset:
				tipo = item.nombre_comprobante_venta
				condicion = "contado" if item.condicion == "Contado" else "cta_cte"
				monto_total = Decimal(item.total)
				
				#-- Agregar el comprobante al grupo.
				datos[tipo]["comprobantes"].append({
					"comprobante": item.comprobante,
					"fecha": item.fecha_comprobante,
					"condicion": item.condicion,
					"cliente_id": item.id_cliente_id,
					"cliente_nombre": item.nombre_cliente,
					"gravado": Decimal(item.gravado),
					"iva": Decimal(item.iva),
					"percep_ib": Decimal(item.percep_ib),
					"total": monto_total,
					"columna": condicion,  # Para identificar si va en Contado o Cta. Cte.
				})
				
				# Actualizar subtotales por condición
				datos[tipo]["subtotal"][condicion]["gravado"] += Decimal(item.gravado)
				datos[tipo]["subtotal"][condicion]["iva"] += Decimal(item.iva)
				datos[tipo]["subtotal"][condicion]["percep_ib"] += Decimal(item.percep_ib)
				datos[tipo]["subtotal"][condicion]["total"] += monto_total
				
				# Actualizar totales generales
				total_general[condicion]["gravado"] += Decimal(item.gravado)
				total_general[condicion]["iva"] += Decimal(item.iva)
				total_general[condicion]["percep_ib"] += Decimal(item.percep_ib)
				total_general[condicion]["total"] += monto_total			
			
			# pprint.pprint(datos)
			print(datos)
			
			#-- Renderizar la plantilla HTML con los datos.
			dominio = f"http://{request.get_host()}"
			
			html_string = render_to_string(reporte, {
				'objetos': datos,
				'total_general': total_general,
				'parametros': param,
				'fecha_hora_reporte': fecha_hora_reporte,
				'titulo': DataViewList.report_title,
				'logo_url': f"{dominio}{static('img/logo_01.png')}",
				'css_url': f"{dominio}{static('css/reportes.css')}",
			})
			
			#-- Preparar la respuesta HTTP.
			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
			HTML(string=html_string).write_pdf(response)
			
			try:
				HTML(string=html_string).write_pdf(response)
			except Exception as e:
				return HttpResponse(f"Error generando el PDF: {str(e)}", status=500)
			
			return response
		else:
			# Manejar errores del formulario
			return HttpResponse(f"Error en el formulario: {form.errors}", status=400)



"""
{'FACTURA ELECTRONICA': {'comprobantes': [{'comprobante': 'FF A 0026-00022788', 'fecha': datetime.date(2024, 8, 14), 'condicion': 'Cta. Cte.', 'cliente_id': 2, 'cliente_nombre': 'Cliente nuevo', 'gravado': Decimal('233057.85'), 'iva': Decimal('48942.15'),'percep_ib': Decimal('0.00'), 'total': Decimal('282000.00'), 'columna': 'cta_cte'},
										  {'comprobante': 'FF A 0026-00022887', 'fecha': datetime.date(2024, 8, 22), 'condicion': 'Cta. Cte.', 'cliente_id': 2, 'cliente_nombre': 'Cliente nuevo', 'gravado': Decimal('19958.68'), 'iva': Decimal('4191.32'), 'percep_ib': Decimal('0.00'), 'total': Decimal('24150.00'), 'columna': 'cta_cte'}, 
										  {'comprobante': 'FF A 0026-00022888', 'fecha': datetime.date(2024, 8, 22), 'condicion': 'Cta. Cte.', 'cliente_id': 2, 'cliente_nombre': 'Cliente nuevo', 'gravado': Decimal('28527.28'), 'iva': Decimal('5990.72'), 'percep_ib': Decimal('0.00'), 'total': Decimal('34518.00'), 'columna': 'cta_cte'}, 
										  {'comprobante': 'FF A 0043-00004729', 'fecha': datetime.date(2025, 1, 9), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('4000.00'), 'columna': 'cta_cte'}, 
										  {'comprobante': 'FF B 0021-00014151', 'fecha': datetime.date(2024, 12, 1), 'condicion': 'Cta. Cte.', 'cliente_id': 1, 'cliente_nombre': 'CLIENTE DE PRUEBA 1', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('1000.00'), 'columna': 'cta_cte'}, 
										  {'comprobante': 'FF B 0022-00037268', 'fecha': datetime.date(2025, 1, 8), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('3000.00'), 'columna': 'cta_cte'}], 
						 'subtotal': {'contado': {'gravado': Decimal('0'), 'iva': Decimal('0'), 'percep_ib': Decimal('0'), 'total': Decimal('0')}, 
									  'cta_cte': {'gravado': Decimal('281543.81'), 'iva': Decimal('59124.19'), 'percep_ib': Decimal('0.00'), 'total': Decimal('348668.00')}}}, 
 'NOTA DE CREDITO ELEC': {'comprobantes': [{'comprobante': 'CF A 0026-00001647', 'fecha': datetime.date(2024, 8, 24), 'condicion': 'Cta. Cte.', 'cliente_id': 2, 'cliente_nombre': 'Cliente nuevo', 'gravado': Decimal('-233057.85'), 'iva': Decimal('-48942.15'), 'percep_ib': Decimal('-5826.45'), 'total': Decimal('-287826.45'), 'columna': 'cta_cte'}, 
										   {'comprobante': 'CF A 0026-00991647', 'fecha': datetime.date(2025, 1, 8), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('-100.00'), 'columna': 'cta_cte'}], 
						  'subtotal': {'contado': {'gravado': Decimal('0'), 'iva': Decimal('0'), 'percep_ib': Decimal('0'), 'total': Decimal('0')}, 
					 				   'cta_cte': {'gravado': Decimal('-233057.85'), 'iva': Decimal('-48942.15'), 'percep_ib': Decimal('-5826.45'), 'total': Decimal('-287926.45')}}}, 
 'NOTA DE DEBITO ELECT': {'comprobantes': [{'comprobante': 'DF A 0021-00002355', 'fecha': datetime.date(2024, 12, 5), 'condicion': 'Cta. Cte.', 'cliente_id': 1, 'cliente_nombre': 'CLIENTE DE PRUEBA 1', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('2000.00'), 'columna': 'cta_cte'}], 
						  'subtotal': {'contado': {'gravado': Decimal('0'), 'iva': Decimal('0'), 'percep_ib': Decimal('0'), 'total': Decimal('0')}, 
					 				   'cta_cte': {'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('2000.00')}}}, 
 'RECIBO': {'comprobantes': [{'comprobante': 'RB R 0001-00136062', 'fecha': datetime.date(2025, 1, 6), 'condicion': 'Cta. Cte.', 'cliente_id': 1, 'cliente_nombre': 'CLIENTE DE PRUEBA 1', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('200.00'), 'columna': 'cta_cte'}, 
							 {'comprobante': 'RB R 0002-00147031', 'fecha': datetime.date(2025, 1, 9), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('1200.00'), 'columna': 'cta_cte'}, 
							 {'comprobante': 'RB R 0008-00024559', 'fecha': datetime.date(2024, 12, 1), 'condicion': 'Cta. Cte.', 'cliente_id': 1, 'cliente_nombre': 'CLIENTE DE PRUEBA 1', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('500.00'), 'columna': 'cta_cte'}], 
			'subtotal': {'contado': {'gravado': Decimal('0'), 'iva': Decimal('0'), 'percep_ib': Decimal('0'), 'total': Decimal('0')}, 
						 'cta_cte': {'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('1900.00')}}}, 
'REMITO': {'comprobantes': [{'comprobante': 'RF R 0033-00007993', 'fecha': datetime.date(2024, 6, 24), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('0.00'), 'columna': 'cta_cte'}, 
							{'comprobante': 'RF R 0033-00008602', 'fecha': datetime.date(2024, 8, 12), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('0.00'), 'columna': 'cta_cte'}, 
							{'comprobante': 'RF R 0042-00003037', 'fecha': datetime.date(2024, 7, 12), 'condicion': 'Cta. Cte.', 'cliente_id': 9, 'cliente_nombre': 'AdmiraPlus Cargo Logistics, SAC', 'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('0.00'), 'columna': 'cta_cte'}], 
		   'subtotal': {'contado': {'gravado': Decimal('0'), 'iva': Decimal('0'), 'percep_ib': Decimal('0'), 'total': Decimal('0')}, 
				  		'cta_cte': {'gravado': Decimal('0.00'), 'iva': Decimal('0.00'), 'percep_ib': Decimal('0.00'), 'total': Decimal('0.00')}}}}

"""