# apps\datatools\views\excel_views.py
import re
import pandas as pd
from django.core.paginator import Paginator
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError, FieldDoesNotExist
from decimal import Decimal, InvalidOperation
from django.db.models import (
	CharField, TextField, IntegerField, BigIntegerField, 
	DecimalField, FloatField, BooleanField, DateField, 
	DateTimeField, ForeignKey, AutoField, NOT_PROVIDED
)

from ..forms.excel_forms import ExcelUploadForm, CamposActualizacionForm
from apps.maestros.models.producto_models import Producto, ProductoCai


class ExcelUploadView(FormView):
	template_name = 'datatools/excel_upload.html'
	form_class = ExcelUploadForm
	success_url = reverse_lazy('excel_preview')
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['fecha'] = timezone.now()
		return context
	
	def form_valid(self, form):
		from apps.informes.views.vllista_list_views import ConfigViews
		
		archivo = form.cleaned_data['archivo_excel']
		
		try:
			if archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls'):
				#-- PRIMERO: Leer solo los nombres de columnas para identificar tipos.
				df_headers = pd.read_excel(archivo, nrows=0)
				columnas_excel = df_headers.columns.tolist()
				
				#-- Identificar qué columnas deben leerse como texto (strings)
				columnas_como_texto = []
				for key, value in ConfigViews.table_info.items():
					if value.get('excel') and value['label'] in columnas_excel:
						try:
							campo_obj = Producto._meta.get_field(key)
							if isinstance(campo_obj, (CharField, TextField)):
								columnas_como_texto.append(value['label'])
						except FieldDoesNotExist:
							continue
				
				#-- SEGUNDO: Leer Excel forzando las columnas string como texto.
				dtype_dict = {col: str for col in columnas_como_texto}
				df = pd.read_excel(archivo, na_filter=False, dtype=dtype_dict, 
								keep_default_na=False)
				
				#-- Verificar si el DataFrame está vacío.
				if df.empty:
					form.add_error('archivo_excel', 'El archivo Excel está vacío.')
					return self.form_invalid(form)
				
				#-- Verificar que las columnas coincidan con las esperadas.
				columnas_esperadas = [value['label'] for value in ConfigViews.table_info.values() if value['excel'] ]
				if set(columnas_esperadas) != set(columnas_excel):
					form.add_error('archivo_excel', f'Las columnas del archivo no coinciden con las esperadas. ')
					return self.form_invalid(form)
				
				#-- TERCERO: Asegurar que los campos string mantengan formato exacto.
				for columna in columnas_como_texto:
					if columna in df.columns:
						#-- Preservar strings exactos, incluyendo ceros iniciales.
						df[columna] = df[columna].apply(lambda x: self._preservar_formato_exacto(x))
				
				#-- Generar lista de campos protegidos y sus etiquetas.
				campos_portegidos = [campo for campo, info in ConfigViews.table_info.items() if info.get('protected', False)]
				etiquetas_portegidas = [info['label'] for info in ConfigViews.table_info.values() if info.get('protected', False)]
				
				#-- Mapear Columnas del Excel a nombres de campos {"label": producto.campo}.
				label_to_field_map = {value['label']: key for key, value in ConfigViews.table_info.items() if value['label'] in columnas_excel}
				
				#-- Limpiar datos (solo valores específicos, no formato).
				df = df.replace(['nan', 'NaN', 'NAN', 'NULL', 'null'], None)
				
				#-- Convertir a lista de diccionarios y guardar en sesión.
				todos_los_datos = df.to_dict('records')
				total_filas = len(todos_los_datos)
				
				#-- Guardar en sesión - optimizado para grandes volúmenes.
				self.request.session['excel_data'] = {
					'columnas': list(df.columns),
					'todos_los_datos': todos_los_datos,
					'total_filas': total_filas,
					'nombre_archivo': archivo.name,
					'campos_protegidos': campos_portegidos,
					'etiquetas_protegidas': etiquetas_portegidas,
					'etiquetas_a_campos_map': label_to_field_map
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
		
	def _preservar_formato_exacto(self, valor):
		"""
		Preserva el formato exacto del valor tal como está en Excel
		"""
		if valor is None or pd.isna(valor):
			return None
		
		#-- Si ya es string, devolver tal cual.
		if isinstance(valor, str):
			#-- Manejar casos especiales de pandas/Excel.
			if valor == 'nan' or valor == 'NaN' or valor == 'NAN':
				return None
			return valor
		
		#-- Para números, convertirlos a string sin perder formato.
		if isinstance(valor, (int, float)):
			#-- Para evitar notación científica y preservar ceros.
			if isinstance(valor, int):
				return str(valor)
			else:
				#-- Para floats, usar formato que preserve decimales.
				if valor.is_integer():
					return str(int(valor))
				else:
					return str(valor)
		
		#-- Para cualquier otro tipo, convertir a string.
		return str(valor)


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
		context['campos_protegidos'] = excel_data.get('campos_protegidos', [])
		context['etiquetas_protegidas'] = excel_data.get('etiquetas_protegidas', [])
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
		form_campos = CamposActualizacionForm(
			columnas=context['columnas'],
			etiquetas_protegidas=context['etiquetas_protegidas']
		)
		context['form_campos'] = form_campos
		
		return context


class ProcesarActualizacionView(TemplateView):
	template_name = 'datatools/procesar_actualizacion.html'
	
	def post(self, request, *args, **kwargs):
		#-- Obtener datos de la sesión.
		excel_data = request.session.get('excel_data', {})
		columnas_excel = excel_data.get('columnas', [])
		protected_fields = excel_data.get('campos_protegidos', [])
		protected_labels = excel_data.get('etiquetas_protegidas', [])
		label_to_field_map = excel_data.get('etiquetas_a_campos_map', {})
		
		campos_protegidos = protected_fields + protected_labels
		campos_protegidos = list(set(campos_protegidos))  # Eliminar duplicados.
		
		#-- Obtener campos seleccionados por el usuario
		campos_seleccionados = []
		for columna_label in columnas_excel:
			campo_post = f'actualizar_{columna_label}'
			if request.POST.get(campo_post) and columna_label in label_to_field_map:
				campo_modelo = label_to_field_map[columna_label]
				campos_seleccionados.append((columna_label, campo_modelo))
		
		if not campos_seleccionados:
			messages.error(request, 'Debe seleccionar al menos un campo para actualizar.')
			return redirect('excel_preview')
		
		#-- Obtener TODOS los datos de la sesión (ya procesados).
		todos_los_datos = excel_data.get('todos_los_datos', [])
		
		if not todos_los_datos:
			messages.error(request, 'No hay datos para procesar.')
			return redirect('cargar_excel')
		
		#-- Mapeo de tipos de datos para validación.
		tipo_validaciones = {
			'string': self._validar_string,
			'integer': self._validar_integer,
			'decimal': self._validar_decimal,
			'boolean': self._validar_boolean,
			'date': self._validar_date,
			'datetime': self._validar_datetime,
			'foreign_key': self._validar_foreign_key,
		}
		
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
					producto = Producto.objects.get(id_producto=codigo)
				except Producto.DoesNotExist:
					errores.append(f"Fila {index}: Producto con código '{codigo}' no existe")
					continue
				
				#-- Actualizar los campos seleccionados.
				cambios_realizados = False
				
				for columna_label, campo_modelo in campos_seleccionados:
					#-- Saltar campos protegidos
					if campo_modelo in campos_protegidos or columna_label in campos_protegidos:
						continue
					
					#-- Comprobar si la columna existe en la fila.
					if columna_label in fila:
						#-- Obtener el valor de la celda.
						valor = fila[columna_label]
						
						#----------------------------------------------------
						
						#-- MANEJO ESPECIAL PARA EL CAMPO CAI.
						if columna_label == "CAI":
							#-- Buscar el ProductoCai por el valor del campo cai.
							try:
								if valor in ['', None, 'NULL', 'null', 'NaN', 'nan']:
									#-- Si el valor está vacío, establecer id_cai como None.
									valor_final = None
								else:
									#-- Buscar el ProductoCai por el valor cai.
									productocai = ProductoCai.objects.get(cai=valor)
									valor_final = productocai.id_cai
								
								#-- Verificar si el valor cambió.
								if producto.id_cai_id != valor_final:
									producto.id_cai_id = valor_final
									cambios_realizados = True
								
								#-- Saltar el procesamiento normal para el campo CAI.
								continue
								
							except ProductoCai.DoesNotExist:
								errores.append(f"Fila {index}: CAI '{valor}' no existe en la base de datos")
								continue
							except Exception as e:
								errores.append(f"Fila {index}: Error al procesar CAI '{valor}' - {str(e)}")
								continue
						
						#----------------------------------------------------
						#-- Obtener el tipo de campo del modelo.
						campo_obj = Producto._meta.get_field(campo_modelo)
						# tipo_dato = campo_obj.get_internal_type()
						
						#-- Determinar tipo de dato dinámicamente.
						tipo_dato = self._obtener_tipo_campo_desde_modelo(campo_obj)
						especificaciones = self._obtener_especificaciones_campo(campo_obj)
						
						#-- USAR EL VALOR POR DEFECTO DEL MODELO PARA VALORES VACÍOS
						if valor in ['', None, 'NULL', 'null', 'NaN', 'nan']:
							if campo_obj.default is not NOT_PROVIDED:
								#-- Usar el valor por defecto definido en el modelo.
								valor = campo_obj.default
							elif isinstance(campo_obj, (DecimalField, FloatField, IntegerField)):
								#-- Si no hay valor por defecto definido, usar 0 para numéricos.
								valor = 0
							else:
								valor = None
						else:
							#-- VALIDAR Y CONVERTIR EL VALOR SEGÚN EL TIPO DE CAMPO.
							try:
								if tipo_dato in tipo_validaciones:
									valor = tipo_validaciones[tipo_dato](valor, campo_obj, especificaciones)
								else:
									valor = self._validar_generico(valor, campo_obj, especificaciones)
							except ValidationError as e:
								errores.append(f"Fila {index}: {columna_label} - {str(e)}")
								continue
						
						#-- Verificar si el valor realmente cambió.
						valor_actual = getattr(producto, campo_modelo)
						
						#-- Comparación segura para tipos numéricos.
						if isinstance(valor, (int, float, Decimal)) and isinstance(valor_actual, (int, float, Decimal)):
							valor_cambio = abs(float(valor) - float(valor_actual)) > 0.001
						else:
							valor_cambio = valor != valor_actual
						
						#-- Asignar el nuevo valor si cambió.
						if valor_cambio:
							setattr(producto, campo_modelo, valor)
							cambios_realizados = True
				
				if cambios_realizados:
					try:
						producto.save()
						actualizados += 1
					except Exception as e:
						errores.append(f"Fila {index}: Error al guardar cambios - {str(e)}")
				
			except Exception as e:
				errores.append(f"Fila {index}: Error al procesar - {str(e)}")
		
		#-- Preparar contexto para mostrar resultados.
		context = self.get_context_data()
		context['total_registros'] = len(todos_los_datos)
		context['actualizados'] = actualizados
		context['errores'] = errores
		context['campos_actualizados'] = [columna for columna, _ in campos_seleccionados]
		
		#-- Limpiar sesión.
		keys_to_remove = ['excel_data', 'pagina_actual']
		for key in keys_to_remove:
			if key in request.session:
				del request.session[key]
		
		return self.render_to_response(context)	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['fecha'] = timezone.now()
		return context
	
	def _obtener_tipo_campo_desde_modelo(self, campo_obj):
		"""Obtener el tipo de campo basado en la instancia del campo del modelo"""
		if isinstance(campo_obj, (CharField, TextField)):
			return 'string'
		elif isinstance(campo_obj, (IntegerField, BigIntegerField, AutoField)):
			return 'integer'
		elif isinstance(campo_obj, (DecimalField, FloatField)):
			return 'decimal'
		elif isinstance(campo_obj, BooleanField):
			return 'boolean'
		elif isinstance(campo_obj, DateField):
			return 'date'
		elif isinstance(campo_obj, DateTimeField):
			return 'datetime'
		elif isinstance(campo_obj, ForeignKey):
			return 'foreign_key'
		else:
			return 'string'
	
	def _obtener_especificaciones_campo(self, campo_obj):
		"""Obtener especificaciones de validación del campo"""
		especificaciones = {}
		
		if hasattr(campo_obj, 'max_length') and campo_obj.max_length:
			especificaciones['max_length'] = campo_obj.max_length
		
		if hasattr(campo_obj, 'max_digits') and campo_obj.max_digits:
			especificaciones['max_digits'] = campo_obj.max_digits
		
		if hasattr(campo_obj, 'decimal_places') and campo_obj.decimal_places:
			especificaciones['decimal_places'] = campo_obj.decimal_places
		
		#-- Validaciones específicas basadas en el nombre del campo.
		if campo_obj.name == 'fecha_fabricacion':
			especificaciones.update({
				'pattern': r'^$|^20\d{2}(0[1-9]|1[0-2])$',
				'mensaje': 'Formato AAAAMM (AAAA año, MM mes válido)'
			})
		elif campo_obj.name == 'unidad':
			especificaciones.update({
				'pattern': r'^[1-9]\d{0,2}$|^0$|^$',
				'mensaje': 'Número entero positivo de hasta 3 dígitos'
			})
		elif campo_obj.name in ['costo', 'descuento', 'precio']:
			especificaciones.update({
				'pattern': r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$',
				'mensaje': 'Número positivo con hasta 13 dígitos y 2 decimales'
			})
		
		return especificaciones
	
	#-- Métodos de validación según tipo de dato del campo.
	def _validar_string(self, valor, campo_obj, especificaciones):
		"""Validar campo string preservando formato exacto"""
		#-- El valor ya viene preservado desde la carga del Excel.
		#-- Solo necesitamos validar, no convertir.
		
		if valor is None:
			return None
		
		#-- Asegurar que es string (por si acaso).
		if not isinstance(valor, str):
			valor = str(valor)
		
		max_length = especificaciones.get('max_length')
		if max_length and len(valor) > max_length:
			raise ValidationError(f"Longitud máxima excedida ({max_length} caracteres)")
		
		#-- Validación específica por patrón si existe.
		pattern = especificaciones.get('pattern')
		if pattern and valor and not re.match(pattern, valor):
			raise ValidationError(especificaciones.get('mensaje', 'Formato inválido'))
		
		return valor
	
	def _validar_integer(self, valor, campo_obj, especificaciones):
		"""Validar campo integer"""
		try:
			int_val = int(valor)
			
			#-- Validación específica por patrón si existe.
			pattern = especificaciones.get('pattern')
			if pattern and not re.match(pattern, str(int_val)):
				raise ValidationError(especificaciones.get('mensaje', 'Formato inválido'))
			
			return int_val
		except (ValueError, TypeError):
			raise ValidationError("Valor entero inválido")
	
	def _validar_decimal(self, valor, campo_obj, especificaciones):
		"""Validar campo decimal"""
		try:
			#-- Convertir a Decimal.
			if isinstance(valor, str):
				#-- Reemplazar coma por punto para formato argentino.
				valor = valor.replace(',', '.')
				#-- Eliminar caracteres no numéricos excepto punto y signo.
				valor = re.sub(r'[^\d\.\-]', '', valor)
			
			decimal_val = Decimal(str(valor))
			
			#-- Validar máximo de dígitos.
			max_digits = especificaciones.get('max_digits')
			decimal_places = especificaciones.get('decimal_places')
			
			if max_digits:
				#-- Verificar que no exceda los dígitos permitidos.
				digits = len(str(decimal_val).replace('.', '').replace('-', ''))
				if digits > max_digits:
					raise ValidationError(f"Máximo {max_digits} dígitos permitidos")
			
			if decimal_places:
				#-- Verificar decimales.
				if decimal_val.as_tuple().exponent and abs(decimal_val.as_tuple().exponent) > decimal_places:
					raise ValidationError(f"Máximo {decimal_places} decimales permitidos")
			
			#-- Validación específica por patrón si existe.
			pattern = especificaciones.get('pattern')
			if pattern and not re.match(pattern, str(decimal_val)):
				raise ValidationError(especificaciones.get('mensaje', 'Formato inválido'))
			
			return decimal_val
			
		except (ValueError, InvalidOperation):
			raise ValidationError("Valor decimal inválido")
	
	def _validar_boolean(self, valor, campo_obj, especificaciones):
		"""Validar campo boolean"""
		if isinstance(valor, bool):
			return valor
		elif isinstance(valor, str):
			valor_lower = valor.lower().strip()
			true_values = ['true', '1', 'yes', 'sí', 'si', 'verdadero', 'x', '✔', 'verdad', 't', 'v']
			false_values = ['false', '0', 'no', 'not', 'falso', '', 'null', 'none', 'f', 'n']
			
			if valor_lower in true_values:
				return True
			elif valor_lower in false_values:
				return False
			else:
				raise ValidationError("Valor booleano inválido")
		else:
			return bool(valor)
	
	def _validar_foreign_key(self, valor, campo_obj, especificaciones):
		"""Validar campo foreign key"""
		try:
			#-- Para foreign keys, validamos que sea un entero válido.
			if valor in ['', None, 'NULL', 'null']:
				return None
			
			int_val = int(valor)
			
			#-- Verificar que exista en la tabla relacionada.
			related_model = campo_obj.related_model
			
			if not related_model.objects.filter(pk=int_val).exists():
				raise ValidationError(f"ID {int_val} no existe en {related_model._meta.verbose_name}")
			
			return int_val
		except (ValueError, TypeError):
			raise ValidationError("ID inválido para relación")
	
	def _validar_date(self, valor, campo_obj, especificaciones):
		"""Validar campo date"""
		try:
			if isinstance(valor, datetime):
				return valor.date()
			elif isinstance(valor, str):
				#-- Intentar varios formatos de fecha.
				formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y%m%d']
				for fmt in formats:
					try:
						return datetime.strptime(valor, fmt).date()
					except ValueError:
						continue
				raise ValidationError("Formato de fecha inválido")
			else:
				raise ValidationError("Tipo de fecha inválido")
		except Exception:
			raise ValidationError("Fecha inválida")
	
	def _validar_datetime(self, valor, campo_obj, especificaciones):
		"""Validar campo datetime"""
		try:
			if isinstance(valor, datetime):
				return valor
			elif isinstance(valor, str):
				#-- Intentar varios formatos de fecha/hora.
				formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y%m%d %H%M%S']
				for fmt in formats:
					try:
						return datetime.strptime(valor, fmt)
					except ValueError:
						continue
				raise ValidationError("Formato de fecha/hora inválido")
			else:
				raise ValidationError("Tipo de fecha/hora inválido")
		except Exception:
			raise ValidationError("Fecha/hora inválida")
	
	def _validar_generico(self, valor, campo_obj, especificaciones):
		"""Validación genérica para tipos no especificados"""
		try:
			#-- Intentar conversión básica a string.
			return str(valor)
		except Exception:
			raise ValidationError("Valor inválido para el campo")


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
