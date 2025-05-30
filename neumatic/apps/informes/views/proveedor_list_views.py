# neumatic\apps\informes\views\proveedor_list_views.py
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views import View
from zipfile import ZipFile
from io import BytesIO

from django.core.mail import EmailMessage

from django.db.models.functions import Lower
from django.db.models import Q

from utils.helpers.export_helpers import ExportHelper

from ..views.list_views_generics import *
from apps.maestros.models.proveedor_models import Proveedor
from ..forms.buscador_proveedor_forms import BuscadorProveedorForm


class ConfigViews:
	# Modelo
	model = Proveedor
	
	# Formulario asociado al modelo
	form_class = BuscadorProveedorForm
	
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
	search_fields = []
	
	ordering = ['nombre_proveedor']
	
	paginate_by = 8
	
	report_title = "Reporte de Proveedores"
	
	table_headers = {
		'id_proveedor': (1, 'Código'),
		'nombre_proveedor': (3, 'Nombre Proveedor'),
		'domicilio_proveedor': (3, 'Domicilio'),
		'id_localidad': (1, 'Localidad'),
		'id_localidad.codigo_postal': (1, 'C.P.'),
		'id_tipo_iva.codigo_iva': (1, 'IVA'),
		'cuit': (1, 'CUIT'),
		'telefono_proveedor': (1, 'Teléfono'),
	}
	
	table_data = [
		{'field_name': 'id_proveedor', 'date_format': None},
		{'field_name': 'nombre_proveedor', 'date_format': None},
		{'field_name': 'domicilio_proveedor', 'date_format': None},
		{'field_name': 'id_localidad', 'date_format': None},
		{'field_name': 'id_localidad.codigo_postal', 'date_format': None},
		{'field_name': 'id_tipo_iva.codigo_iva', 'date_format': None},
		{'field_name': 'cuit', 'date_format': None},
		{'field_name': 'telefono_proveedor', 'date_format': None},
	]


class ProveedorInformeListView(InformeListView):
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
			orden = form.cleaned_data.get('orden', 'nombre')
			desde = form.cleaned_data.get('desde', '').lower()
			hasta = form.cleaned_data.get('hasta', '').lower()
			
			if estatus not in ['activos', 'inactivos', 'todos']:
				estatus = 'activos'
			
			if estatus:
				match estatus:
					case "activos":
						queryset = queryset.filter(estatus_proveedor=True)
					case "inactivos":
						queryset = queryset.filter(estatus_proveedor=False)
			
			if orden not in ['nombre', 'codigo']:
				orden = 'nombre'
			
			orden = "nombre_proveedor" if orden == "nombre" else "id_proveedor"
			
			queryset = queryset.order_by(orden)
			
			if orden == 'nombre_proveedor':
				#-- Anotar un campo en minúsculas para la comparación insensible a mayúsculas/minúsculas.
				queryset = queryset.annotate(nombre_lower=Lower('nombre_proveedor'))
				
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
				
				
			elif orden == 'id_proveedor':
				if desde and hasta:
					queryset = queryset.filter(id_proveedor__range=(desde, hasta))
				elif desde:
					queryset = queryset.filter(id_proveedor__gte=desde)
				elif hasta:
					queryset = queryset.filter(id_proveedor__lte=hasta)
			
		else:
			#-- Agregar clases css a los campos con errores.
			print("El form no es válido (desde la vista)")
			print(f"{form.errors = }")
			form.add_error_classes()
						
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorProveedorForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class ProveedorInformesView(View):
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
		queryset_filtrado = ProveedorInformeListView()
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


class ProveedorInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset (el listado de clientes) ya filtrado.
		queryset_filtrado = ProveedorInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Generar el pdf.
		helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
		buffer = helper.export_to_pdf()
		
		#-- Preparar la respuesta HTTP.
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="informe_{ConfigViews.model_string}.pdf"'
		
		return response
