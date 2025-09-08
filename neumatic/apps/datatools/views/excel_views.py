# apps\datatools\views\excel_views.py
import pandas as pd
# import numpy as np
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from ..forms.excel_forms import ExcelUploadForm


class ExcelUploadView(FormView):
	template_name = 'datatools/excel_upload.html'
	form_class = ExcelUploadForm
	success_url = reverse_lazy('excel_preview')
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['fecha'] = timezone.now()
		return context
	
	def form_valid(self, form):
		#-- Guardar el archivo en sesión para procesarlo en la siguiente vista.
		archivo = form.cleaned_data['archivo_excel']
		
		#-- Leer el archivo Excel.
		try:
			if archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls'):
				df = pd.read_excel(archivo)
				
				# #-- Validar que el archivo no esté vacío.
				if df.empty or len(df) == 0:
					form.add_error('archivo_excel', 'El archivo Excel está vacío. Debe contener al menos una fila de datos.')
					return self.form_invalid(form)
				
				#-- Reemplazar valores NaN/NaT de pandas por None de Python.
				df = df.where(pd.notnull(df), None)
				
				#-- Convertir el DataFrame a formato que pueda ser serializado en sesión.
				datos_excel = {
					'columnas': list(df.columns),
					'datos': df.to_dict('records')
				}
				
				#-- Guardar en sesión.
				self.request.session['datos_excel'] = datos_excel
				self.request.session['nombre_archivo'] = archivo.name
				
				return super().form_valid(form)
			else:
				form.add_error('archivo_excel', 'El archivo debe ser en formato Excel (.xlsx o .xls)')
				return self.form_invalid(form)
				
		except Exception as e:
			form.add_error('archivo_excel', f'Error al procesar el archivo: {str(e)}')
			return self.form_invalid(form)

class ExcelPreviewView(TemplateView):
	template_name = 'datatools/excel_preview.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Recuperar datos de la sesión.
		datos_excel = self.request.session.get('datos_excel', {})
		nombre_archivo = self.request.session.get('nombre_archivo', '')
		
		context['nombre_archivo'] = nombre_archivo
		context['columnas'] = datos_excel.get('columnas', [])
		context['datos'] = datos_excel.get('datos', [])
		context['fecha'] = timezone.now()
		
		return context
	
	def get(self, request, *args, **kwargs):
		#-- Verificar que hay datos en la sesión antes de mostrar la previsualización.
		if 'datos_excel' not in request.session:
			messages.error(request, 'No hay datos para previsualizar. Por favor, cargue un archivo Excel primero.')
			return redirect('cargar_excel')
		
		#-- Verificar que los datos no estén vacíos.
		datos_excel = request.session.get('datos_excel', {})
		if not datos_excel.get('datos'):
			messages.error(request, 'El archivo cargado está vacío. Por favor, cargue un archivo con datos.')
			return redirect('cargar_excel')
		
		return super().get(request, *args, **kwargs)
