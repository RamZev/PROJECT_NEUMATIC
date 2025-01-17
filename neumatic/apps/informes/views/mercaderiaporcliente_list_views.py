# neumatic\apps\informes\views\mercaderiaporcliente_list_views.py
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

from ..views.list_views_generics import *
from apps.informes.models import VLMercaderiaPorCliente
from ..forms.buscador_mercaderiaporcliente_forms import BuscadorMercaderiaPorClienteForm


class ConfigViews:
	# Modelo
	model = VLMercaderiaPorCliente
	
	# Formulario asociado al modelo
	form_class = BuscadorMercaderiaPorClienteForm
	
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
	
	report_title = "Mercadería por Cliente"
	
	table_headers = {
		'nombre_comprobante_venta': (1, 'Comprobante'),
		'numero': (1, 'Número'),
		'fecha_comprobante': (1, 'Fecha'),
		'nombre_producto_marca': (1, 'Marca'),
		'nombre_producto': (1, 'Producto'),
		'cantidad': (1, 'Cantidad'),
		'precio': (1, 'Precio'),
		'total': (1, 'Total'),
	}
	
	table_data = [
		{'field_name': 'nombre_comprobante_venta', 'date_format': None},
		{'field_name': 'numero', 'date_format': None},
		{'field_name': 'fecha_comprobante', 'date_format': 'd/m/Y'},
		{'field_name': 'nombre_producto_marca', 'date_format': None},
		{'field_name': 'nombre_producto', 'date_format': None},
		{'field_name': 'cantidad', 'date_format': None},
		{'field_name': 'precio', 'date_format': None},
		{'field_name': 'total', 'date_format': None},
	]
	
	#-- Texto de totalización y Columnas a totalizar.
	# total_columns = {"Total Pendiente: ": ['saldo']}


class VLMercaderiaPorClienteInformeListView(InformeListView):
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
		queryset = VLMercaderiaPorCliente.objects.none()		
		
		# form = self.form_class(self.request.GET)
		
		# Comprobamos si hay datos GET (parámetros de la URL)
		if any(value for key, value in self.request.GET.items() if value):
			form = BuscadorMercaderiaPorClienteForm(self.request.GET)
			print("Entra al IF: Hay datos en el GET")
		else:
			form = BuscadorMercaderiaPorClienteForm()  # Formulario vacío para la carga inicial
			print("Entra al ELSE: No hay datos útiles en el GET")	
		
		if form.is_valid():
			cliente = form.cleaned_data.get('cliente', None)
			fecha_desde = form.cleaned_data.get('fecha_desde', date(date.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', date.today())
			
			if not fecha_desde:
				fecha_hasta = date(date.today().year, 1, 1)
			
			if not fecha_hasta:
				fecha_hasta = date.today()
			
			queryset = VLMercaderiaPorCliente.objects.obtener_fact_pendientes(cliente.id_cliente, fecha_desde, fecha_hasta)
			
		else:
			#-- Agregar clases css a los campos con errores.
			# print("El form no es válido (desde la vista)")
			# print(f"{form.errors = }")
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorMercaderiaPorClienteForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class VLMercaderiaPorClienteInformesView(View):
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
		queryset_filtrado = VLMercaderiaPorClienteInformeListView()
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


class VLMercaderiaPorClienteInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset ya filtrado.
		queryset_filtrado = VLMercaderiaPorClienteInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		# ------------------------------------------------------------------------------
		#-- Agrupar los objetos por el número de comprobante.
		grouped_data = {}
		for obj in queryset:
			comprobante_num = obj.numero_comprobante  # Este es el campo que agrupa los datos
			if comprobante_num not in grouped_data:
				grouped_data[comprobante_num] = []
			grouped_data[comprobante_num].append(obj)
		
		# ------------------------------------------------------------------------------
		
		#-- Inicializar el formulario con los datos GET.
		form = BuscadorMercaderiaPorClienteForm(request.GET or None)
		
		if form.is_valid():
			cliente = form.cleaned_data.get("cliente", None)
			fecha_desde = form.cleaned_data.get("fecha_desde", None)
			fecha_hasta = form.cleaned_data.get("fecha_hasta", None)
			
			reporte = 'informes/reportes/mercaderiaporcliente_pdf.html'
			titulo_reporte = "Mercadería por Cliente"
			param = {
				"Desde": fecha_desde,
				"Hasta": fecha_hasta,
			}
			
			#-- Validar que el cliente exista antes de acceder a sus datos.
			cliente_data = {}
			if cliente:
				cliente_data = {
					"id_cliente": cliente.id_cliente,
					"nombre_cliente": cliente.nombre_cliente,
				}
			else:
				#-- Si el formulario no es válido, manejar errores o enviar respuesta.
				return HttpResponse(f"Error en el formulario: {form.errors}", status=400)
		
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		#-- Renderizar la plantilla HTML con los datos.
		html_string = render_to_string(reporte, {
			'objetos': grouped_data,
			'cliente': cliente_data,
			'parametros': param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': titulo_reporte,
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

"""
{2600001647: [ <VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>, <VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>], 
 2600022788: [<VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>, <VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>], 
 2600022887: [<VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>], 
 2600022888: [<VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>, <VLMercaderiaPorCliente: VLMercaderiaPorCliente object (2)>]}
"""