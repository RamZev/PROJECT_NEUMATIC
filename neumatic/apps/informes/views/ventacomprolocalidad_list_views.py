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

from .list_views_generics import *
from apps.informes.models import VLVentaComproLocalidad
from ..forms.buscador_ventacomprolocalidad_forms import BuscadorVentaComproLocalidadForm


class ConfigViews:
	# Modelo
	model = VLVentaComproLocalidad
	
	# Formulario asociado al modelo
	form_class = BuscadorVentaComproLocalidadForm
	
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
	
	report_title = "Ventas por Localidad"
	
	table_headers = {
		'fecha_comprobante': (1, 'Fecha'),
		'comprobante': (2, 'Comprobante'),
		'id_cliente_id': (1, 'Cliente'),
		'nombre_cliente': (2, 'Nombre'),
		'cuit': (1, 'CUIT'),
		'codigo_postal': (1, 'C.P.'),
		'gravado': (1, 'Gravado'),
		'exento': (1, 'Exento'),
		'iva': (1, 'IVA'),
		'percep_ib': (1, 'Percep. IB'),
		'total': (1, 'Total'),
		'iniciales': (1, 'Op.'),
	}
	
	table_data = [
		{'field_name': 'fecha_comprobante', 'date_format': 'd/m/Y'},
		{'field_name': 'comprobante', 'date_format': None},
		{'field_name': 'id_cliente_id', 'date_format': None},
		{'field_name': 'nombre_cliente', 'date_format': None},
		{'field_name': 'cuit', 'date_format': None},
		{'field_name': 'codigo_postal', 'date_format': None},
		{'field_name': 'gravado', 'date_format': None},
		{'field_name': 'exento', 'date_format': None},
		{'field_name': 'iva', 'date_format': None},
		{'field_name': 'percep_ib', 'date_format': None},
		{'field_name': 'total', 'date_format': None},
		{'field_name': 'iniciales', 'date_format': None},
	]
	
	#-- Texto de totalización y Columnas a totalizar.
	# total_columns = {"Total Pendiente: ": ['saldo']}


class VLVentaComproLocalidadInformeListView(InformeListView):
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
		queryset = VLVentaComproLocalidad.objects.none()		
		
		# form = self.form_class(self.request.GET)
		
		# Comprobamos si hay datos GET (parámetros de la URL)
		if any(value for key, value in self.request.GET.items() if value):
			form = BuscadorVentaComproLocalidadForm(self.request.GET)
		else:
			form = BuscadorVentaComproLocalidadForm()  # Formulario vacío para la carga inicial
		
		if form.is_valid():
			sucursal = form.cleaned_data.get('sucursal', None)
			fecha_desde = form.cleaned_data.get('fecha_desde', date(date.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', date.today())
			codigo_postal = form.cleaned_data.get('codigo_postal', None)
			
			if not fecha_desde:
				fecha_hasta = date(date.today().year, 1, 1)
			
			if not fecha_hasta:
				fecha_hasta = date.today()
			
			queryset = VLVentaComproLocalidad.objects.obtener_venta_compro_localidad(fecha_desde, fecha_hasta)
			
			if sucursal:
				queryset = VLVentaComproLocalidad.objects.filter(id_sucursal_id=sucursal.id_sucursal)
			
			if codigo_postal:
				queryset = VLVentaComproLocalidad.objects.filter(codigo_postal=codigo_postal)
				
			
		else:
			#-- Agregar clases css a los campos con errores.
			# print("El form no es válido (desde la vista)")
			# print(f"{form.errors = }")
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorVentaComproLocalidadForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class VLVentaComproLocalidadInformesView(View):
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
		queryset_filtrado = VLVentaComproLocalidadInformeListView()
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


class VLVentaComproLocalidadInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset ya filtrado.
		queryset_filtrado = VLVentaComproLocalidadInformeListView()
		queryset_filtrado.request = request
		# queryset = queryset_filtrado.get_queryset()
		raw_queryset = queryset_filtrado.get_queryset()
		
		#-- Convertir RawQuerySet en una lista de diccionarios para trabajar con los datos.
		queryset = list(raw_queryset)  #-- Esto lo hace compatible para iterar y sumar manualmente.

		#-- Inicializar el formulario con los datos GET.
		form = BuscadorVentaComproLocalidadForm(request.GET or None)
		
		if form.is_valid():
			sucursal = form.cleaned_data.get("sucursal", None)
			fecha_desde = form.cleaned_data.get("fecha_desde", None)
			fecha_hasta = form.cleaned_data.get("fecha_hasta", None)
			codigo_postal = form.cleaned_data.get("codigo_postal", None)
			
			reporte = 'informes/reportes/ventacomprolocalidad_pdf.html'
			
			param = {
				"Desde": fecha_desde.strftime("%d/%m/%Y"),
				"Hasta": fecha_hasta.strftime("%d/%m/%Y"),
			}
			
			param.update({"C.P.": codigo_postal if codigo_postal else "Todos"})
			param.update({"Sucursal": sucursal.nombre_sucursal if sucursal else "Todas"})
			
			#-- Calcular el total general.
			total_general = sum(item.total for item in queryset if hasattr(item, "total"))
			
			fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			
			#-- Renderizar la plantilla HTML con los datos.
			dominio = f"http://{request.get_host()}"
			
			html_string = render_to_string(reporte, {
				'objetos': queryset,
				'total_general': total_general,  # Añadir el total general al contexto
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