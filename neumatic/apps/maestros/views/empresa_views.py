# neumatic\apps\maestros\views\localidad_views.py
import os
import tempfile
# import subprocess
from cryptography import x509
from cryptography.hazmat.backends import default_backend
# from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from django.views import View
import json

from django.urls import reverse_lazy
from ..views.cruds_views_generics import *
from ..models.empresa_models import Empresa
from ..forms.empresa_forms import EmpresaForm


class ConfigViews():
	#-- Modelo.
	model = Empresa
	
	#-- Formulario asociado al modelo.
	form_class = EmpresaForm
	
	#-- Aplicación asociada al modelo.
	app_label = model._meta.app_label
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	model_string = model.__name__.lower()  #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	
	#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
	# model_string = "producto_estado"
	
	#-- Permisos.
	permission_add = f"{app_label}.add_{model.__name__.lower()}"
	permission_change = f"{app_label}.change_{model.__name__.lower()}"
	permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
	
	#-- Vistas del CRUD del modelo.
	list_view_name = f"{model_string}_list"
	create_view_name = f"{model_string}_create"
	update_view_name = f"{model_string}_update"
	delete_view_name = f"{model_string}_delete"
	
	#-- Plantilla para crear o actualizar el modelo.
	template_form = f"{app_label}/{model_string}_form.html"
	
	#-- Plantilla para confirmar eliminación de un registro.
	template_delete = "base_confirm_delete.html"
	
	#-- Plantilla de la lista del CRUD.
	template_list = f'{app_label}/maestro_list.html'
	
	#-- Contexto de los datos de la lista.
	context_object_name	= 'objetos'
	
	#-- Vista del home del proyecto.
	home_view_name = "home"
	
	#-- Nombre de la url.
	success_url = reverse_lazy(list_view_name)


class DataViewList():
	search_fields = [
		'nombre_fiscal',
		 'nombre_comercial'
	]
	
	ordering = ['nombre_fiscal']
	
	paginate_by = 8
	
	table_headers = {
		'estatus_empresa': (1, 'Estatus'),
		# 'id_empresa': (1, 'ID'),
		'nombre_fiscal': (4, 'Nombre Fiscal'),
		'cuit': (1, 'C.U.I.T.'),
		'id_localidad': (32, 'Localidad'),
		'telefono': (1, 'Teléfono'),
		
		'acciones': (2, 'Acciones'),
	}
	
	table_data = [
		{'field_name': 'estatus_empresa', 'date_format': None},
		# {'field_name': 'id_empresa', 'date_format': None},
		{'field_name': 'nombre_fiscal', 'date_format': None},
		{'field_name': 'cuit', 'date_format': None},
		{'field_name': 'id_localidad', 'date_format': None},
		{'field_name': 'telefono', 'date_format': None},
	]


class EmpresaListView(MaestroListView):
	model = ConfigViews.model
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	search_fields = DataViewList.search_fields
	ordering = DataViewList.ordering
	
	extra_context = {
		"master_title": ConfigViews.model._meta.verbose_name_plural,
		"home_view_name": ConfigViews.home_view_name,
		"list_view_name": ConfigViews.list_view_name,
		"create_view_name": ConfigViews.create_view_name,
		"update_view_name": ConfigViews.update_view_name,
		"delete_view_name": ConfigViews.delete_view_name,
		"table_headers": DataViewList.table_headers,
		"table_data": DataViewList.table_data,
	}


class EmpresaCreateView(MaestroCreateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_add


class EmpresaUpdateView(MaestroUpdateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_change


class EmpresaDeleteView (MaestroDeleteView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	template_name = ConfigViews.template_delete
	success_url = ConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = ConfigViews.permission_delete


@method_decorator(login_required, name='dispatch')
class CargarCertificadoView(View):
	"""
	Vista para cargar certificados y extraer su fecha de vencimiento
	"""
	
	def post(self, request, *args, **kwargs):
		try:
			#-- Obtener datos del request.
			data = json.loads(request.body)
			certificado_content = data.get('certificado', '')
			tipo = data.get('tipo', 'homologacion')  #-- 'homologacion' o 'produccion'.
			
			if not certificado_content:
				return JsonResponse({
					'success': False,
					'error': 'No se proporcionó contenido del certificado'
				})
			
			#-- Validar formato del certificado.
			if not self.validar_certificado(certificado_content):
				return JsonResponse({
					'success': False,
					'error': 'El formato del certificado no es válido. Debe ser un certificado X.509 en formato PEM.'
				})
			
			else:
				#-- Extraer fecha de vencimiento del certificado.
				fecha_vencimiento = self.extraer_fecha_vencimiento(certificado_content)
				
				if fecha_vencimiento:
					return JsonResponse({
						'success': True,
						'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y %H:%M:%S'),
						'mensaje': 'Certificado cargado correctamente'
					})
				else:
					return JsonResponse({
						'success': False,
						'error': 'No se pudo extraer la fecha de vencimiento del certificado'
					})
		
		except json.JSONDecodeError:
			return JsonResponse({
				'success': False,
				'error': 'Formato de datos inválido'
			})
		except Exception as e:
			return JsonResponse({
				'success': False,
				'error': f'Error al procesar el certificado: {str(e)}'
			})
	
	def validar_certificado(self, certificado_content):
		"""
		Valida que el contenido sea un certificado X.509 válido en formato PEM
		"""
		#-- Verificar que tenga los marcadores de certificado.
		if 'BEGIN CERTIFICATE' not in certificado_content or 'END CERTIFICATE' not in certificado_content:
			return False
		
		#-- Verificar que tenga la estructura básica de un certificado.
		try:
			#-- Intentar parsear el certificado.
			if isinstance(certificado_content, str):
				cert_data = certificado_content.encode('utf-8')
			else:
				cert_data = certificado_content
			
			#-- Intentar cargar el certificado.
			cert = x509.load_pem_x509_certificate(cert_data, default_backend())
			
			#-- Verificar que tenga fecha de emisión y vencimiento.
			if not cert.not_valid_before or not cert.not_valid_after:
				return False
			
			#-- Verificar que tenga un número de serie.
			if not cert.serial_number:
				return False
			
			return True
			
		except Exception as e:
			print(f"Error al validar certificado: {e}")
			return False
	
	def extraer_fecha_vencimiento(self, certificado_content):
		"""
		Extrae la fecha de vencimiento del certificado usando cryptography
		"""
		
		temp_file = None
		temp_file_path = None
		
		try:
			#-- Crear archivo temporal con el contenido del certificado.
			#-- Usamos modo 'wb' para escribir bytes.
			with tempfile.NamedTemporaryFile(mode='wb', suffix='.crt', delete=False) as temp_file:
				#-- Convertir el contenido a bytes si es string.
				if isinstance(certificado_content, str):
					certificado_content = certificado_content.encode('utf-8')
				temp_file.write(certificado_content)
				temp_file_path = temp_file.name
			
			#-- Leer y parsear el certificado.
			with open(temp_file_path, 'rb') as f:
				cert_data = f.read()
			
			#-- Intentar cargar el certificado en formato PEM.
			try:
				cert = x509.load_pem_x509_certificate(cert_data, default_backend())
				print("**-- Certificado cargado en formato PEM.")
			except Exception as e:
				#-- Si falla, intentar con DER.
				try:
					cert = x509.load_der_x509_certificate(cert_data, default_backend())
					print("**-- Certificado cargado en formato DER.")
				except:
					raise Exception(f"No se pudo parsear el certificado: {e}")
			
			#-- Obtener fecha de vencimiento.
			fecha_vencimiento = cert.not_valid_after
			
			#-- Convertir a datetime de Python (ya que not_valid_after es datetime).
			#-- Asegurarse de que sea timezone-naive para guardar en DB.
			if fecha_vencimiento.tzinfo is not None:
				#-- Si tiene timezone, convertirlo a naive.
				fecha_vencimiento = fecha_vencimiento.replace(tzinfo=None)
			
			return fecha_vencimiento
			
		except Exception as e:
			print(f"Error al extraer fecha de vencimiento: {e}")
			return None
			
		finally:
			#-- Limpiar archivo temporal.
			if temp_file_path and os.path.exists(temp_file_path):
				try:
					os.unlink(temp_file_path)
				except:
					pass


@method_decorator(login_required, name='dispatch')
class CargarClaveView(View):
	"""
	Vista para cargar claves privadas
	"""
	
	def post(self, request, *args, **kwargs):
		try:
			data = json.loads(request.body)
			clave_content = data.get('clave', '')
			tipo = data.get('tipo', 'homologacion')
			
			if not clave_content:
				return JsonResponse({
					'success': False,
					'error': 'No se proporcionó contenido de la clave'
				})
			
			#-- Validar formato de clave privada (básico).
			if not self.validar_clave_privada(clave_content):
				return JsonResponse({
					'success': False,
					'error': 'El formato de la clave privada no es válido'
				})
			
			return JsonResponse({
				'success': True,
				'mensaje': 'Clave cargada correctamente'
			})
		
		except json.JSONDecodeError:
			return JsonResponse({
				'success': False,
				'error': 'Formato de datos inválido'
			})
		except Exception as e:
			return JsonResponse({
				'success': False,
				'error': f'Error al procesar la clave: {str(e)}'
			})
	
	'''
	def validar_clave_privada(self, clave_content):
		"""
		Valida que el contenido sea una clave privada válida
		"""
		
		#-- Verificar que tenga los marcadores de clave privada.
		if 'BEGIN PRIVATE KEY' in clave_content and 'END PRIVATE KEY' in clave_content:
			return True
		if 'BEGIN RSA PRIVATE KEY' in clave_content and 'END RSA PRIVATE KEY' in clave_content:
			return True
		if 'BEGIN ENCRYPTED PRIVATE KEY' in clave_content and 'END ENCRYPTED PRIVATE KEY' in clave_content:
			return True
		
		return False
	'''
	def validar_clave_privada(self, clave_content):
		"""
		Valida que el contenido sea una clave privada válida
		"""
		#-- Verificar que tenga los marcadores de clave privada.
		if not any([
			'BEGIN PRIVATE KEY' in clave_content and 'END PRIVATE KEY' in clave_content,
			'BEGIN RSA PRIVATE KEY' in clave_content and 'END RSA PRIVATE KEY' in clave_content,
			'BEGIN ENCRYPTED PRIVATE KEY' in clave_content and 'END ENCRYPTED PRIVATE KEY' in clave_content
		]):
			return False
		
		#-- Intentar parsear la clave (validación más profunda).
		try:
			from cryptography.hazmat.primitives import serialization
			from cryptography.hazmat.backends import default_backend
			
			if isinstance(clave_content, str):
				clave_bytes = clave_content.encode('utf-8')
			else:
				clave_bytes = clave_content
			
			#-- Intentar cargar la clave privada.
			#-- Nota: Esto puede fallar si la clave tiene contraseña, pero al menos validamos formato.
			serialization.load_pem_private_key(
				clave_bytes,
				password=None,
				backend=default_backend()
			)
			return True
		except Exception as e:
			#-- Si falla, podría ser porque tiene contraseña, pero al menos el formato es válido.
			#-- Si tiene BEGIN/END, consideramos válido.
			print(f"Advertencia: No se pudo cargar la clave privada completamente: {e}")
			return True  #-- Retornamos True porque tiene la estructura correcta.

