# neumatic\apps\informes\views\productocai_list_views.py
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views import View
from zipfile import ZipFile
from io import BytesIO

from django.core.mail import EmailMessage

from utils.helpers.export_helpers import ExportHelper

from ..views.list_views_generics import *
from apps.maestros.models.base_models import ProductoCai
from ..forms.buscador_productocai_forms import BuscadorProductoCaiForm


class ConfigViews:
	# Modelo
	model = ProductoCai
	
	# Formulario asociado al modelo
	form_class = BuscadorProductoCaiForm
	
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
	
	ordering = []
	
	paginate_by = 8
	
	report_title = "Reporte de Producto CAIs"
	
	table_info = {
		"estatus_cai": {
			"label": "Estatus",
			"col_width_table": 1,
			"col_width_pdf": 40,
			"pdf_paragraph": False,
			"date_format": None,
			"table": True,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"cai": {
			"label": "CAI",
			"col_width_table": 2,
			"col_width_pdf": 100,
			"pdf_paragraph": False,
			"date_format": None,
			"table": True,
			"pdf": True,
			"excel": True,
			"csv": True
		},
		"descripcion_cai": {
			"label": "Descripción CAI",
			"col_width_table": 9,
			"col_width_pdf": 200,
			"pdf_paragraph": False,
			"date_format": None,
			"table": True,
			"pdf": True,
			"excel": True,
			"csv": True
		},
	}


class ProductoCaiInformeListView(InformeListView):
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
		"table_info": DataViewList.table_info,
		"buscador_template": f"{ConfigViews.app_label}/buscador_{ConfigViews.model_string}.html",
		"js_file": ConfigViews.js_file,
		"url_zip": ConfigViews.url_zip,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def get_queryset(self):
		queryset = self.model.objects.none()
		form = self.form_class(self.request.GET)
		
		if form.is_valid():
			
			estatus = form.cleaned_data.get('estatus', 'activos')
			
			if estatus:
				match estatus:
					case "activos":
						queryset = self.model.objects.filter(estatus_cai=True)
					case "inactivos":
						queryset = self.model.objects.filter(estatus_cai=False)
					case "todos":
						queryset = self.model.objects.all()
			
			queryset = queryset.order_by("cai")
			
		else:
			#-- Agregar clases css a los campos con errores.
			form.add_error_classes()
						
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorProductoCaiForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class ProductoCaiInformesView(View):
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
		queryset_filtrado = ProductoCaiInformeListView()
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
			table = DataViewList.table_info.copy()
			
			#-- Generar los formatos seleccionados.
			if "pdf" in formatos:
				#-- Filtrar los campos que se van a exportar a PDF.
				table_info = { field: table[field] for field in table if table[field]['pdf'] }
				
				#-- Generar el PDF.
				helper = ExportHelper(queryset, table_info, DataViewList.report_title)
				
				pdf_content = helper.export_to_pdf()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.pdf", pdf_content)
			
			if "excel" in formatos:
				#-- Filtrar los campos que se van a exportar a Excel.
				table_info = { field: table[field] for field in table if table[field]['excel'] }
				
				#-- Generar el Excel.
				helper = ExportHelper(queryset, table_info, DataViewList.report_title)
				
				excel_content = helper.export_to_excel()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.xlsx", excel_content)
			
			if "csv" in formatos:
				#-- Filtrar los campos que se van a exportar a CSV.
				table_info = { field: table[field] for field in table if table[field]['csv'] }
				
				#-- Generar el CSV.
				helper = ExportHelper(queryset, table_info, DataViewList.report_title)
				
				csv_content = helper.export_to_csv()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.csv", csv_content)
		
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
		
		if "excel" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.xlsx", helper.generar_excel(), 
					   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
		
		if "csv" in formatos:
			attachments.append((f"informe_{ConfigViews.model_string}.csv", helper.generar_csv(), 
					   "text/csv"))
		
		#-- Crear y enviar el correo.
		subject = DataViewList.report_title
		body = "Adjunto encontrarás el informe solicitado."
		email_message = EmailMessage(subject, body, to=[email])
		for filename, content, mime_type in attachments:
			email_message.attach(filename, content, mime_type)
		
		email_message.send()
		
		#-- Responder con un mensaje de éxito.
		return JsonResponse({"success": True, "message": "Informe enviado correctamente al correo."})


class ProductoCaiInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset (el listado de clientes) ya filtrado.
		queryset_filtrado = ProductoCaiInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Filtrar los campos que se van a exportar a PDF.
		table = DataViewList.table_info.copy()
		table_info = { field: table[field] for field in table if table[field]['pdf'] }
		
		#-- Generar el PDF.
		helper = ExportHelper(queryset, table_info, DataViewList.report_title)
		buffer = helper.export_to_pdf()
		
		#-- Preparar la respuesta HTTP.
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="{ConfigViews.model_string}.pdf"'
		
		return response
