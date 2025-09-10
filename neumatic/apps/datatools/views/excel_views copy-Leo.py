# apps\datatools\views\excel_views.py
import pandas as pd
import numpy as np
from django.core.paginator import Paginator
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from ..forms.excel_forms import ExcelUploadForm, CamposActualizacionForm


class ExcelUploadView(FormView):
	template_name = 'datatools/excel_upload.html'
	form_class = ExcelUploadForm
	success_url = reverse_lazy('excel_preview')
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['fecha'] = timezone.now()
		return context
	
	def form_valid(self, form):
		archivo = form.cleaned_data['archivo_excel']
		
		try:
			if archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls'):
				#-- Leer el archivo directamente desde el upload (sin guardar temporalmente).
				df = pd.read_excel(archivo, na_filter=False)
				
				if df.empty:
					form.add_error('archivo_excel', 'El archivo Excel está vacío.')
					return self.form_invalid(form)
				
				#-- Limpiar datos.
				df = df.replace(['nan', 'NaN', 'NAN', '', 'NULL', 'null'], None)
				numeric_cols = df.select_dtypes(include=[np.number]).columns
				for col in numeric_cols:
					df[col] = df[col].where(df[col].notna(), None)
				
				#-- Convertir a lista de diccionarios y guardar en sesión.
				todos_los_datos = df.to_dict('records')
				total_filas = len(todos_los_datos)
				
				#-- Guardar en sesión - optimizado para grandes volúmenes.
				self.request.session['excel_data'] = {
					'columnas': list(df.columns),
					'todos_los_datos': todos_los_datos,
					'total_filas': total_filas,
					'nombre_archivo': archivo.name
				}
				
				#-- Guardar solo la primera página inicialmente.
				paginator = Paginator(todos_los_datos, 100)
				primera_pagina = paginator.page(1).object_list
				
				self.request.session['pagina_actual'] = {
					'numero': 1,
					'datos': primera_pagina,
					'total_paginas': paginator.num_pages
				}
				
				return super().form_valid(form)
			else:
				form.add_error('archivo_excel', 'El archivo debe ser en formato Excel (.xlsx o .xls)')
				return self.form_invalid(form)
				
		except Exception as e:
			form.add_error('archivo_excel', f'Error al procesar el archivo: {str(e)}')
			return self.form_invalid(form)


class ExcelPreviewView(TemplateView):
	template_name = 'datatools/excel_preview.html'
	
	def get(self, request, *args, **kwargs):
		#-- Verificar que hay datos en la sesión antes de mostrar la previsualización.
		if 'excel_data' not in request.session:
			messages.error(request, 'No hay datos para previsualizar. Por favor, cargue un archivo Excel primero.')
			return redirect('cargar_excel')
		
		#-- Verificar que los datos no estén vacíos.
		excel_data = request.session.get('excel_data', {})
		if not excel_data.get('todos_los_datos'):
			messages.error(request, 'El archivo cargado está vacío. Por favor, cargue un archivo con datos.')
			return redirect('cargar_excel')
		
		return super().get(request, *args, **kwargs)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Recuperar datos de la sesión.
		excel_data = self.request.session.get('excel_data', {})
		pagina_actual = self.request.session.get('pagina_actual', {})
		
		context['nombre_archivo'] = excel_data.get('nombre_archivo', '')
		context['columnas'] = excel_data.get('columnas', [])
		context['datos'] = pagina_actual.get('datos', [])
		context['total_filas'] = excel_data.get('total_filas', 0)
		context['fecha'] = timezone.now()
		context['pagina_actual'] = pagina_actual.get('numero', 1)
		context['total_paginas'] = pagina_actual.get('total_paginas', 1)
		
		#-- Calcular rango de páginas.
		pagina_actual_num = context['pagina_actual']
		total_paginas = context['total_paginas']
		start_page = max(1, pagina_actual_num - 2)
		end_page = min(total_paginas, start_page + 4)
		
		if end_page - start_page < 4:
			start_page = max(1, end_page - 4)
		
		context['page_range'] = range(start_page, end_page + 1)
		context['page_start'] = (pagina_actual_num - 1) * 100 + 1
		context['page_end'] = min(pagina_actual_num * 100, context['total_filas'])
		
		#-- Formulario para selección de campos.
		form_campos = CamposActualizacionForm(columnas=context['columnas'])
		context['form_campos'] = form_campos
		
		return context


class ProcesarActualizacionView(TemplateView):
	template_name = 'datatools/procesar_actualizacion.html'
	
	def post(self, request, *args, **kwargs):
		from apps.maestros.models.producto_models import Producto
		from apps.informes.views.vllista_list_views import ConfigViews
		
		#-- Obtener campos seleccionados del formulario.
		campos_seleccionados = []
		excel_data = request.session.get('excel_data', {})
		columnas_excel = excel_data.get('columnas', [])
		
		#-- Mapear etiquetas a nombres de campos (producto.campo: "Label").
		columns_dict = {key: value['label'] for key, value in ConfigViews.table_info.items() if value['label'] in columnas_excel}
		# print("columns_dict:", columns_dict)
		
		for columna in columns_dict.values():
			if request.POST.get(f'actualizar_{columna}'):
				campos_seleccionados.append(columna)
		print("campos_seleccionados:", campos_seleccionados)
		
		if not campos_seleccionados:
			messages.error(request, 'Debe seleccionar al menos un campo para actualizar.')
			return redirect('excel_preview')
		
		#-- Obtener TODOS los datos de la sesión (ya procesados).
		todos_los_datos = excel_data.get('todos_los_datos', [])
		
		if not todos_los_datos:
			messages.error(request, 'No hay datos para procesar.')
			return redirect('cargar_excel')
		
		#-- Procesar los datos.
		actualizados = 0
		errores = []
		
		for index, fila in enumerate(todos_los_datos, 1):
			try:
				codigo = fila.get('Código')
				if not codigo:
					errores.append(f"Fila {index}: No se especificó código de producto")
					continue
				
				#-- Buscar el producto por código.
				try:
					producto = Producto.objects.get(codigo=codigo)
				except Producto.DoesNotExist:
					errores.append(f"Fila {index}: Producto con código '{codigo}' no existe")
					continue
				
				#-- Actualizar los campos seleccionados.
				for campo in campos_seleccionados:
					if campo in fila and campo != 'Código':
						valor = fila[campo]
						if hasattr(producto, campo):
							if valor in ['', None]:
								valor = None
							setattr(producto, campo, valor)
				
				producto.save()
				actualizados += 1
				
			except Exception as e:
				errores.append(f"Fila {index}: Error al procesar - {str(e)}")
		
		#-- Preparar contexto para mostrar resultados.
		context = self.get_context_data()
		context['total_registros'] = len(todos_los_datos)
		context['actualizados'] = actualizados
		context['errores'] = errores
		context['campos_actualizados'] = campos_seleccionados
		
		#-- Limpiar sesión.
		keys_to_remove = ['excel_data', 'pagina_actual']
		for key in keys_to_remove:
			request.session.pop(key, None)
		
		return self.render_to_response(context)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['fecha'] = timezone.now()
		return context


def cargar_pagina_excel(request):
	"""Vista AJAX para cargar páginas específicas - OPTIMIZADA"""
	if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		pagina = int(request.GET.get('pagina', 1))
		
		#-- Obtener todos los datos de la sesión (ya procesados).
		excel_data = request.session.get('excel_data', {})
		todos_los_datos = excel_data.get('todos_los_datos', [])
		
		if not todos_los_datos:
			return JsonResponse({'error': 'Datos no disponibles'}, status=400)
		
		#-- Paginar los datos que ya están en memoria.
		paginator = Paginator(todos_los_datos, 100)
		
		try:
			pagina_datos = paginator.page(pagina).object_list
			
			#-- Actualizar solo la página actual en sesión.
			request.session['pagina_actual'] = {
				'numero': pagina,
				'datos': pagina_datos,
				'total_paginas': paginator.num_pages
			}
			
			return JsonResponse({
				'success': True,
				'pagina_actual': pagina,
				'total_paginas': paginator.num_pages,
				'total_filas': len(todos_los_datos)
			})
			
		except Exception as e:
			return JsonResponse({'error': str(e)}, status=500)
	
	return JsonResponse({'error': 'Método no permitido'}, status=405)
