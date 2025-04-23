# neumatic\apps\informes\views\comprobanteventa_list_views.py
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views import View
from zipfile import ZipFile
from io import BytesIO

from django.core.mail import EmailMessage

from utils.helpers.export_helpers import ExportHelper

from ..views.list_views_generics import *
from apps.maestros.models.base_models import ComprobanteVenta
from ..forms.buscador_comprobanteventa_forms import BuscadorComprobanteVentaForm


class ConfigViews:
	# Modelo
	model = ComprobanteVenta
	
	# Formulario asociado al modelo
	form_class = BuscadorComprobanteVentaForm
	
	# Aplicación asociada al modelo
	app_label = "informes"
	
	# Nombre del modelo en minúsculas
	model_string = model.__name__.lower()
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	
	# Plantilla de la lista del CRUD
	template_list = f"{app_label}/maestro_informe_list.html"
	
	# Contexto de los datos de la lista
	context_object_name = "objetos"
	
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
	search_fields = []
	
	ordering = ['nombre_comprobante_venta']
	
	paginate_by = 8
	
	report_title = "Reporte de Comprobantes de Venta"
	
	table_headers = {
		'estatus_comprobante_venta': (1, 'Estatus'),
		'nombre_comprobante_venta': (4, 'Nombre Comprobante'),
		'mult_venta': (1, 'Mult. Venta'),
		'mult_saldo': (1, 'Mult. Saldo'),
		'mult_stock': (1, 'Mult. Stock'),
		'mult_comision': (1, 'Mult. Comisión'),
		'mult_caja': (1, 'Mult. Caja'),
		'mult_estadistica': (1, 'Mult. Estadísticas'),
		'libro_iva': (1, 'Libro IVA'),
		'estadistica': (1, 'Estadísticas'),
		'electronica': (1, 'Electrónica'),
		'presupuesto': (1, 'Presupuesto'),
		'pendiente': (1, 'Pendiente'),
		'codigo_afip_a': (1, 'Cód. AFIP A'),
		'codigo_afip_b': (1, 'Cód. AFIP B'),
		'info_michelin_auto': (1, 'I/M auto'),
		'info_michelin_camion': (1, 'I/M camión'),
	}
	
	table_data = [
		{'field_name': 'estatus_comprobante_venta', 'date_format': None},
		{'field_name': 'nombre_comprobante_venta', 'date_format': None},
		{'field_name': 'mult_venta', 'date_format': None},
		{'field_name': 'mult_saldo', 'date_format': None},
		{'field_name': 'mult_stock', 'date_format': None},
		{'field_name': 'mult_comision', 'date_format': None},
		{'field_name': 'mult_caja', 'date_format': None},
		{'field_name': 'mult_estadistica', 'date_format': None},
		{'field_name': 'libro_iva', 'date_format': None},
		{'field_name': 'estadistica', 'date_format': None},
		{'field_name': 'electronica', 'date_format': None},
		{'field_name': 'presupuesto', 'date_format': None},
		{'field_name': 'pendiente', 'date_format': None},
		{'field_name': 'codigo_afip_a', 'date_format': None},
		{'field_name': 'codigo_afip_b', 'date_format': None},
		{'field_name': 'info_michelin_auto', 'date_format': None},
		{'field_name': 'info_michelin_camion', 'date_format': None},
	]


class ComprobanteVentaInformeListView(InformeListView):
	model = ConfigViews.model
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	search_fields = DataViewList.search_fields
	ordering = DataViewList.ordering
	
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
		queryset = super().get_queryset()
		form = self.form_class(self.request.GET)
		
		if form.is_valid():
			
			estatus = form.cleaned_data.get('estatus')
			
			if estatus not in ['activos', 'inactivos', 'todos']:
				estatus = 'activos'
			
			if estatus:
				match estatus:
					case "activos":
						queryset = queryset.filter(estatus_comprobante_venta=True)
					case "inactivos":
						queryset = queryset.filter(estatus_comprobante_venta=False)
			
			queryset = queryset.order_by("nombre_comprobante_venta")
			
		else:
			#-- Agregar clases css a los campos con errores.
			print("El form no es válido (desde la vista)")
			print(f"{form.errors = }")
			form.add_error_classes()
						
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorComprobanteVentaForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class ComprobanteVentaInformesView(View):
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
		queryset_filtrado = ComprobanteVentaInformeListView()
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
			helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
			
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
		helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
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


class ComprobanteVentaInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset (el listado de clientes) ya filtrado.
		queryset_filtrado = ComprobanteVentaInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Generar el pdf.
		helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
		buffer = helper.export_to_pdf()
		
		#-- Preparar la respuesta HTTP.
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
		
		return response
