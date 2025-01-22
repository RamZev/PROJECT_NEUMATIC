# neumatic\apps\informes\views\cliente_list_views.py
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
from apps.informes.models import VLResumenCtaCte
from ..forms.buscador_resumenctacte_forms import BuscadorResumenCtaCteForm


class ConfigViews:
	# Modelo
	model = VLResumenCtaCte
	
	# Formulario asociado al modelo
	form_class = BuscadorResumenCtaCteForm
	
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
	js_file = "js/filtros_resumen_cta_cte.js"
	
	# URL de la vista que genera el .zip con los informes.
	url_zip = f"{model_string}_informe_generado"
	
	# URL de la vista que genera el .pdf.
	url_pdf = f"{model_string}_informe_pdf"


class DataViewList:
	# search_fields = ['nombre_cliente', 'cuit']
	
	# ordering = ['nombre_cliente']
	
	paginate_by = 8
	
	report_title = "Resumen Cta. Cte."
	
	table_headers = {
		'nombre_comprobante_venta': (2, 'Comprobante'),
		'numero': (2, 'Número'),
		'fecha_comprobante': (1, 'Fecha'),
		'remito': (1, 'Remito'),
		'condicion': (1, 'Cond. Venta'),
		# 'total': (1, 'Total Comp.'),
		# 'entrega': (1, 'Entrega'),
		'debe': (1, 'Debe'),
		'haber': (1, 'Haber'),
		'saldo_acumulado': (1, 'Saldo'),
		'intereses': (1, 'Intereses'),
	}
	
	table_data = [
		{'field_name': 'nombre_comprobante_venta', 'date_format': None},
		{'field_name': 'numero', 'date_format': None},
		{'field_name': 'fecha_comprobante', 'date_format': 'd/m/Y'},
		{'field_name': 'remito', 'date_format': None},
		{'field_name': 'condicion', 'date_format': None},
		# {'field_name': 'total', 'date_format': None},
		# {'field_name': 'entrega', 'date_format': None},
		{'field_name': 'debe', 'date_format': None},
		{'field_name': 'haber', 'date_format': None},
		{'field_name': 'saldo_acumulado', 'date_format': None},
		{'field_name': 'intereses', 'date_format': None},
	]
	
	#-- Texto de totalización y Columnas a totalizar.
	# total_columns = {"Total Pendiente: ": ['saldo']}


class VLResumenCtaCteInformeListView(InformeListView):
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
		# "buscador_template": f"{ConfigViews.app_label}/buscador_vlfactpendiente.html",
		"js_file": ConfigViews.js_file,
		"url_zip": ConfigViews.url_zip,
		"url_pdf": ConfigViews.url_pdf,
	}
	
	def get_queryset(self):
		# queryset = super().get_queryset()
		
		#-- Inicializa el queryset con un queryset vacío por defecto.
		queryset = VLResumenCtaCte.objects.none()		
		
		# form = self.form_class(self.request.GET)
		
		# Comprobamos si hay datos GET (parámetros de la URL)
		if any(value for key, value in self.request.GET.items() if value):
			form = BuscadorResumenCtaCteForm(self.request.GET)
			print("Entra al IF: Hay datos en el GET")
		else:
			form = BuscadorResumenCtaCteForm()  # Formulario vacío para la carga inicial
			print("Entra al ELSE: No hay datos útiles en el GET")	
		
		if form.is_valid():
			resumen_pendiente = form.cleaned_data.get('resumen_pendiente')
			condicion_venta = form.cleaned_data.get('condicion_venta')
			fecha_desde = form.cleaned_data.get('fecha_desde', date(date.today().year, 1, 1))
			fecha_hasta = form.cleaned_data.get('fecha_hasta', date.today())
			cliente = form.cleaned_data.get('cliente', None)
			
			if resumen_pendiente:
				queryset = VLResumenCtaCte.objects.obtener_fact_pendientes(cliente.id_cliente)
			else:
				if not fecha_desde:
					fecha_hasta = date(date.today().year, 1, 1)
				
				if not fecha_hasta:
					fecha_hasta = date.today()
				
				if condicion_venta == "0":
					queryset = VLResumenCtaCte.objects.obtener_resumen_cta_cte(cliente.id_cliente, fecha_desde, fecha_hasta, 1, 2)
				else:
					queryset = VLResumenCtaCte.objects.obtener_resumen_cta_cte(cliente.id_cliente, fecha_desde, fecha_hasta, condicion_venta, condicion_venta)
		
		else:
			#-- Agregar clases css a los campos con errores.
			# print("El form no es válido (desde la vista)")
			# print(f"{form.errors = }")
			form.add_error_classes()
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = BuscadorResumenCtaCteForm(self.request.GET or None)
		
		context["form"] = form
		
		#-- Si el formulario tiene errores, pasa los errores al contexto.
		if form.errors:
			context["data_has_errors"] = True
		
		return context


class VLResumenCtaCteInformesView(View):
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
		queryset_filtrado = VLResumenCtaCteInformeListView()
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


class VLResumenCtaCteInformePDFView(View):
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el queryset ya filtrado.
		queryset_filtrado = VLResumenCtaCteInformeListView()
		queryset_filtrado.request = request
		queryset = queryset_filtrado.get_queryset()
		
		#-- Inicializar el formulario con los datos GET.
		form = BuscadorResumenCtaCteForm(request.GET or None)
		
		if form.is_valid():
			cliente = form.cleaned_data.get("cliente", None)
			
			resumen_pendiente = form.cleaned_data.get("resumen_pendiente", None)
			condicion_venta = form.cleaned_data.get("condicion_venta", None)
			fecha_desde = form.cleaned_data.get("fecha_desde", None)
			fecha_hasta = form.cleaned_data.get("fecha_hasta", None)
			observaciones = form.cleaned_data.get("observaciones", None)
			
			saldo_anterior = 0
			
			param = {}
			if resumen_pendiente:
				#-- Reporte Resumen de Cuenta Pendiente.
				reporte = 'informes/reportes/facturas_pendientes_pdf.html'
				param["Tipo"] = "Resumen de Cuenta Pendiente"
			else:
				#-- Reporte Resumen de Cuenta Cuenta Corriente.
				reporte = 'informes/reportes/resumen_cta_cte_pdf.html'
				param = {
					"Desde": fecha_desde,
					"Hasta": fecha_hasta,
				}
				
				match condicion_venta:
					case "1":
						param["Condición"] = "Contado"
					case "2":
						param["Condición"] = "Cuenta Corriente"
					case "0":
						param["Condición"] = "Ambos"
				
				#-- Determinar Saldo Anterior.
				saldo_anterior_queryset = VLResumenCtaCte.objects.obtener_saldo_anterior(cliente.id_cliente, fecha_desde)
				#-- Extraer el saldo desde el queryset.
				# saldo_anterior = saldo_anterior_queryset[0].saldo_anterior if saldo_anterior_queryset else 0.0
				saldo_anterior = next(iter(saldo_anterior_queryset), None).saldo_anterior if saldo_anterior_queryset else Decimal('0.0')
				saldo_anterior = Decimal(saldo_anterior or 0.0)  # Conversión explícita
			
			#-- Validar que el cliente exista antes de acceder a sus datos.
			cliente_data = {}
			if cliente:
				cliente_data = {
					"id_cliente": cliente.id_cliente,
					"nombre_cliente": cliente.nombre_cliente,
					"domicilio_cliente": cliente.domicilio_cliente,
					"telefono_cliente": cliente.telefono_cliente,
					"codigo_postal": cliente.codigo_postal,
					"localidad": cliente.id_localidad.nombre_localidad if cliente.id_localidad else "",
					"provincia": cliente.id_provincia.nombre_provincia if cliente.id_provincia else "",
					"nombre_vendedor": cliente.id_vendedor.nombre_vendedor if cliente.id_vendedor else "",
				}
			else:
				#-- Si el formulario no es válido, manejar errores o enviar respuesta.
				return HttpResponse(f"Error en el formulario: {form.errors}", status=400)
		
			#-- Obtener el saldo total desde el último registro del queryset.
			# saldo_total = queryset.last().saldo_acumulado if queryset.exists() else 0
			saldo_total = queryset[-1].saldo_acumulado if queryset else 0
			
			#-- Calcular la sumatoria de los intereses.
			intereses_total = sum(item.intereses for item in queryset)
			
		fecha_hora_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		
		#-- Renderizar la plantilla HTML con los datos.
		html_string = render_to_string(reporte, {
			'objetos': queryset,
			'cliente': cliente_data,
			'parametros': param,
			'fecha_hora_reporte': fecha_hora_reporte,
			'titulo': "Resumen de Cuenta Corriente",
			'observaciones': observaciones,
			'saldo_total': saldo_total,
			'intereses_total': intereses_total,
			'total_general': saldo_anterior + saldo_total + intereses_total,
			"saldo_anterior": saldo_anterior,
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
