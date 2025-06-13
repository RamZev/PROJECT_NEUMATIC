# neumatic\apps\informes\views\producto_list_views.py
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views import View
from zipfile import ZipFile
from io import BytesIO
from reportlab.lib.pagesizes import A4, portrait, landscape
from django.core.mail import EmailMessage
from django.db.models.functions import Lower
from django.db.models import Q
from utils.helpers.export_helpers import ExportHelper

from ..views.list_views_generics import *
from apps.maestros.models.producto_models import Producto
from ..forms.buscador_producto_forms import BuscadorProductoForm


class ConfigViews:
	# Modelo
	model = Producto
	
	# Formulario asociado al modelo
	form_class = BuscadorProductoForm
	
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
	ordering = []
	paginate_by = 8
	
	report_title = "Lista de Precios"
	
	table_headers = {
		'id_producto': (1, 'Código'),
		'medida': (1, 'Medida'),
		'nombre_producto': (4, 'Descripción'),
		'id_marca': (4, 'Marca'),
		'precio': (2, 'Precio'),
	}
	
	table_data = [
		{'field_name': 'id_producto', 'date_format': None},
		{'field_name': 'medida', 'date_format': None},
		{'field_name': 'nombre_producto', 'date_format': None},
		{'field_name': 'id_marca', 'date_format': None},
		{'field_name': 'precio', 'date_format': None},
	]
	# table_headers.update({
	# 	"tipo_producto": (1, "Tipo Producto"),
	# 	"id_familia.nombre_producto_familia": (4, "Familia"),
	# 	"segmento": (1, "Segmento"),
	# 	"id_modelo.nombre_modelo": (4, "Modelo"),
	# 	"fecha_fabricacion": (1, "Fecha Fabricación"),
	# 	"costo": (2, "Costo"),
	# 	"id_alicuota_iva.alicuota_iva": (1, "Alícuota IVA"),
	# 	"cai": (1, "CAI"),
	# 	"stock": (1, "Stock"),
	# 	"minimo": (1, "Mínimo"),
	# 	"descuento": (1, "Descuento"),
	# 	"despacho_1": (4, "Despacho 1"),
	# 	"despacho_2": (4, "Despacho 2"),
	# 	"carrito": (1, "Carrito"),
	# })


class ProductoInformeListView(InformeListView):
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
		queryset = self.model.objects.none()
		form = self.form_class(self.request.GET)
		
		if form.is_valid():
			estatus = form.cleaned_data.get('estatus', 'activos')
			id_familia_desde = form.cleaned_data.get('id_familia_desde') or 0
			id_familia_hasta = form.cleaned_data.get('id_familia_hasta') or 0
			id_marca_desde = form.cleaned_data.get('id_marca_desde') or 0
			id_marca_hasta = form.cleaned_data.get('id_marca_hasta') or 0
			id_modelo_desde = form.cleaned_data.get('id_modelo_desde') or 0
			id_modelo_hasta = form.cleaned_data.get('id_modelo_hasta') or 0
			
			if estatus:
				match estatus:
					case "activos":
						queryset = self.model.objects.filter(estatus_producto=True)
					case "inactivos":
						queryset = self.model.objects.filter(estatus_producto=False)
					case "todos":
						queryset = self.model.objects.all()
			
			if id_familia_desde or id_familia_hasta:
				#-- Filtrar por rango de familias.
				familias_ids = range=(id_familia_desde, id_familia_hasta+1)
				queryset = queryset.filter(id_familia_id__in=familias_ids)
				
			if id_marca_desde or id_marca_hasta:
				#-- Filtrar por rango de marcas.
				marcas_ids = range=(id_marca_desde, id_marca_hasta+1)
				queryset = queryset.filter(id_marca_id__in=marcas_ids)
				
			if id_modelo_desde or id_modelo_hasta:
				#-- Filtrar por rango de modelos.
				modelos_ids = range=(id_modelo_desde, id_modelo_hasta+1)
				queryset = queryset.filter(id_modelo_id__in=modelos_ids)
			
		else:
			#-- Agregar clases css a los campos con errores.
			print("El form no es válido (desde la vista)")
			print(f"{form.errors = }")
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorProductoForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class ProductoInformesView(View):
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
		queryset_filtrado = ProductoInformeListView()
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
		
		table_headers = DataViewList.table_headers.copy()
		
		table_headers.update({
			"tipo_producto": (1, "Tipo Producto"),
			"id_familia.nombre_producto_familia": (4, "Familia"),
			"segmento": (1, "Segmento"),
			"id_modelo.nombre_modelo": (4, "Modelo"),
			"fecha_fabricacion": (1, "Fecha Fabricación"),
			"costo": (2, "Costo"),
			"id_alicuota_iva.alicuota_iva": (1, "Alícuota IVA"),
			"cai": (1, "CAI"),
			"stock": (1, "Stock"),
			"minimo": (1, "Mínimo"),
			"descuento": (1, "Descuento"),
			"despacho_1": (4, "Despacho 1"),
			"despacho_2": (4, "Despacho 2"),
			"carrito": (1, "Carrito"),
		})
		
		buffer = BytesIO()
		with ZipFile(buffer, "w") as zip_file:
			# helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
			helper = ExportHelper(queryset, table_headers, DataViewList.report_title)
			
			#-- Generar los formatos seleccionados.
			if "pdf" in formatos:
				pdf_content = helper.export_to_pdf()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.pdf", pdf_content)
			
			if "excel" in formatos:
				excel_content = helper.export_to_excel()
				zip_file.writestr(f"informe_{ConfigViews.model_string}.xlsx", excel_content)
			
			if "csv" in formatos:
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


class ProductoInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset (el listado de clientes) ya filtrado.
		queryset_filtrado = ProductoInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Generar el pdf.
		helper = ExportHelper(queryset, DataViewList.table_headers, DataViewList.report_title)
		buffer = helper.export_to_pdf(pagesize=portrait(A4))
		
		#-- Preparar la respuesta HTTP.
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="{ConfigViews.model_string}.pdf"'
		
		return response
