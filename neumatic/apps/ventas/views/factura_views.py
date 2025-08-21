# neumatic\apps\ventas\views\factura_views.py
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import transaction
from django.db.models import F
from django.db import DatabaseError
from django.utils import timezone
from django.utils.safestring import mark_safe

import json

from .msdt_views_generics import *
from ..models.factura_models import Factura
from ...maestros.models.numero_models import Numero
from ..forms.factura_forms import FacturaForm, DetalleFacturaFormSet
from ..forms.factura_forms import SerialFacturaFormSet
from ...maestros.models.base_models import ProductoStock, ComprobanteVenta, Operario
from ...maestros.models.valida_models import Valida
from ...maestros.models.cliente_models import Cliente

from entorno.constantes_base import TIPO_VENTA

modelo = Factura

#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
model_string = modelo.__name__.lower()   # Cuando el modelo es una sola palabra.

#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
#model_string = "color"

formulario = FacturaForm

template_form = f"{model_string}_form.html"
home_view_name = "home"
list_view_name = f"{model_string}_list"
create_view_name = f"{model_string}_create"
update_view_name = f"{model_string}_update"
delete_view_name = f"{model_string}_delete"

# @method_decorator(login_required, name='dispatch')
class FacturaListView(MaestroDetalleListView):
	model = modelo
	template_name = f"ventas/maestro_detalle_list.html"
	context_object_name = 'objetos'
	tipo_comprobante = 'electronico'  # Nuevo atributo de clase

	search_fields = [
	 'id_factura',
	 'compro',
	 'numero_comprobante',
	 'cuit',
	 'id_cliente__nombre_cliente' #separar por guión bajo doble "__"
	]

	ordering = ['-id_factura']

 	#-- Encabezado de la Tabla.
	table_headers = {
		'id_factura': (1, 'ID'),
		'compro': (1, 'Compro'),
		'letra_comprobante': (1, 'Letra'),
		'numero_comprobante': (1, 'Nro Comp'),
		'fecha_comprobante': (1, 'fecha'),
		'cuit': (1, 'CUIT'),
		'id_cliente': (3, 'Cliente'),
		'total': (2, 'Total'),
		'opciones': (1, 'Opciones'),
	}

	#-- Columnas de la Tabla.
	table_data = [
		{'field_name': 'id_factura', 'date_format': None},
		{'field_name': 'compro', 'date_format': None},
		{'field_name': 'letra_comprobante', 'date_format': None},
		{'field_name': 'numero_comprobante', 'date_format': None},
  		{'field_name': 'fecha_comprobante', 'date_format': 'd/m/Y'},
		{'field_name': 'cuit', 'date_format': None},
		{'field_name': 'id_cliente', 'date_format': None},
		{'field_name': 'total', 'date_format': None, 'decimal_places': 2},
	]

	#cadena_filtro = "Q(nombre_color__icontains=text)"
	extra_context = {
		#"master_title": model._meta.verbose_name_plural,
		"master_title": "Comprobantes Electrónicos",
		"home_view_name": home_view_name,
		"list_view_name": list_view_name,
		"create_view_name": create_view_name,
		"update_view_name": update_view_name,
		"delete_view_name": delete_view_name,
		"table_headers": table_headers,
		"table_data": table_data,
		"model_string_for_pdf": "factura",  # ¡Solución clave aquí!
		"model_string": model_string,
	}

	def get_queryset(self):
		# Obtener el queryset base
		queryset = super().get_queryset()

		# Obtener el usuario actual
		user = self.request.user

		# Si el usuario no es superusuario, filtrar por sucursal
		if not user.is_superuser:
				queryset = queryset.filter(id_sucursal=user.id_sucursal)
		
		# 2. NUEVO FILTRO: Comprobantes electrónicos o remitos
		queryset = queryset.filter(
			Q(id_comprobante_venta__electronica=True) |
			Q(id_comprobante_venta__remito=True),
			id_comprobante_venta__recibo=False,
			id_comprobante_venta__presupuesto=False
		)

		# Aplicar búsqueda y ordenación
		query = self.request.GET.get('busqueda', None)
		if query:
				search_conditions = Q()
				for field in self.search_fields:
						search_conditions |= Q(**{f"{field}__icontains": query})
				queryset = queryset.filter(search_conditions)

		return queryset.order_by(*self.ordering)
 

	def get_context_data(self, **kwargs):
		# Obtener el contexto base
		context = super().get_context_data(**kwargs)
		
		# Agregar model_string al contexto
		context['model_string'] = model_string  # Esto devolverá 'factura'
		
		# Mantener todos los valores de extra_context
		if hasattr(self, 'extra_context'):
				context.update(self.extra_context)
				
		return context

# @method_decorator(login_required, name='dispatch')
class FacturaCreateView(MaestroDetalleCreateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name) # Nombre de la url.
	tipo_comprobante = 'electronico'  # Nuevo atributo de clase

	#-- Indicar el permiso que requiere para ejecutar la acción:
	# Obtener el nombre de la aplicación a la que pertenece el modelo.
	app_label = model._meta.app_label
	# Indicar el permiso eN el formato: <app_name>.<permiso>_<modelo>
	permission_required = f"{app_label}.add_{model.__name__.lower()}"

	# print("Entro a la vista")

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)

		# print("Entro a get_context_data")

		# Pasar variables adicionales al contexto
		usuario = self.request.user
		data['cambia_precio_descripcion'] = usuario.cambia_precio_descripcion
		data['tipo_venta'] = TIPO_VENTA

		if self.request.POST:
			data['formset_detalle'] = DetalleFacturaFormSet(self.request.POST)
			data['formset_serial'] = SerialFacturaFormSet(self.request.POST)
		else:
			data['formset_detalle'] = DetalleFacturaFormSet(instance=self.object)
			data['formset_serial'] = SerialFacturaFormSet(instance=self.object)

		data['is_edit'] = False  # Indicar que es una edición

		# Obtener todos los comprobantes con sus valores libro_iva
		libro_iva_dict = {str(c.id_comprobante_venta): c.libro_iva for c in ComprobanteVenta.objects.all()}
		data['libro_iva_dict'] = json.dumps(libro_iva_dict)

		# Obtener todos los comprobantes con sus valores mult_venta
		mult_venta_dict = {str(c.id_comprobante_venta): c.mult_venta for c in ComprobanteVenta.objects.all()}
		data['mult_venta_dict'] = json.dumps(mult_venta_dict)

		# Obtener todos los comprobantes con sus valores electronica
		electronica_dict = {str(c.id_comprobante_venta): c.electronica for c in ComprobanteVenta.objects.all()}
		data['electronica_dict'] = json.dumps(electronica_dict)

		# Obtener todos los comprobantes con sus valores tipo_comprobante
		tipo_comprobante_dict = {str(c.id_comprobante_venta): c.tipo_comprobante for c in ComprobanteVenta.objects.all()}
		data['tipo_comprobante_dict'] = mark_safe(json.dumps(tipo_comprobante_dict, ensure_ascii=False))

		# Obtener todos los operarios con sus id
		operario_dict = {str(o.id_operario): o.nombre_operario for o in Operario.objects.all()}
		data['operario_dict'] = json.dumps(operario_dict)

		# Tipo de Comprobante
		data['tipo_comprobante'] = self.tipo_comprobante

		return data

	def form_valid(self, form):
		context = self.get_context_data()
		formset_detalle = context['formset_detalle']
		formset_serial = context['formset_serial']

		if not all([formset_detalle.is_valid(), formset_serial.is_valid()]):
			return self.form_invalid(form)

		try:
			with transaction.atomic():
				# 0. REGLA: Validación y actualización de datos del cliente
				cliente_obj = form.cleaned_data['id_cliente']  # Esto es un objeto Cliente
				cliente_id = cliente_obj.id_cliente  # Accede al campo id_cliente del modelo
				
				if cliente_id:
					try:
						cliente = Cliente.objects.get(id_cliente=cliente_id)
						movil_factura = form.cleaned_data.get('movil_factura', '').strip()
						email_factura = form.cleaned_data.get('email_factura', '').strip()
						
						updates = {}
						
						# Lógica para el teléfono móvil
						if movil_factura:  # Solo si se ingresó un valor en el formulario
							if not cliente.movil_cliente:
								# Caso 1: No tiene móvil registrado -> actualizar movil_cliente
								updates['movil_cliente'] = movil_factura
								form.instance.movil_factura = movil_factura
							elif cliente.movil_cliente != movil_factura:
								# Caso 2: Tiene móvil diferente -> guardar en telefono_cliente
								updates['telefono_cliente'] = movil_factura
								form.instance.movil_factura = movil_factura
						
						# Lógica para el email
						if email_factura:  # Solo si se ingresó un email en el formulario
							if not cliente.email_cliente:
								# Caso 1: No tiene email registrado -> actualizar email_cliente
								updates['email_cliente'] = email_factura
								form.instance.email_factura = email_factura
							elif cliente.email_cliente != email_factura:
								# Caso 2: Tiene email diferente -> guardar en email2_cliente
								updates['email2_cliente'] = email_factura
								form.instance.email_factura = email_factura
						
						# Aplicar actualizaciones si hay cambios
						if updates:
							Cliente.objects.filter(id_cliente=cliente_id).update(**updates)
					
					except Cliente.DoesNotExist:
						pass
				
				# 1. Validación mínima necesaria
				deposito = form.cleaned_data.get('id_deposito')
				if not deposito:
					form.add_error('id_deposito', 'Debe seleccionar un depósito')
					return self.form_invalid(form)

				# 2. Validación para documentos pendientes
				comprobante_venta = form.cleaned_data['id_comprobante_venta']
				if comprobante_venta.pendiente:
					comprobante_remito = form.cleaned_data.get('comprobante_remito')
					remito = form.cleaned_data.get('remito')
					
					if not all([comprobante_remito, remito]):
							form.add_error(None, 'Para este tipo de comprobante debe especificar el documento asociado')
							return self.form_invalid(form)

				# 3. Numeración (nueva versión)
				sucursal = form.cleaned_data['id_sucursal']
				punto_venta = form.cleaned_data['id_punto_venta']
				comprobante = form.cleaned_data['compro']
				fecha_comprobante = form.cleaned_data['fecha_comprobante']
				
				# Determinamos id_discrimina_iva basado en el tipo de IVA (Regla: True solo si id_tipo_iva == 4)
				cliente = form.cleaned_data['id_cliente']
				id_discrimina_iva = (cliente.id_tipo_iva.discrimina_iva)
				
				# Obtener configuración AFIP del comprobante
				comprobante_data = ComprobanteVenta.objects.filter(
					codigo_comprobante_venta=comprobante
				).first()

				if not comprobante_data:
					form.add_error(None, 'No se encontró la configuración AFIP para este comprobante')
					return self.form_invalid(form)

				# Determinar el tipo de numeración basado en comprobante_data
				if comprobante_data.electronica:
					tipo_numeracion = 'eletronica'
				elif comprobante_data.tipo_documento == "FACTURA" and not comprobante_data.electronica:
					tipo_numeracion = 'manual'
				else:
					tipo_numeracion = 'automatica'

				
				# Manejar la numeración según el tipo
				if tipo_numeracion == 'automatica':
					resultado = self._asignar_numeracion_automatica(
						sucursal, punto_venta, comprobante_afip, letra, form
					)
					
				elif tipo_numeracion == 'manual':
					resultado = self._asignar_numeracion_manual(
						sucursal, punto_venta, comprobante_afip, letra, form
					)
					
				elif tipo_numeracion == 'electronica':
					print("tipo_numeracion", tipo_numeracion)
					resultado = self._asignar_numeracion_electronica(
						sucursal, punto_venta, comprobante_afip, letra, fecha_comprobante, form
					)
					
				else:
					form.add_error(None, 'Tipo de numeración no válido')
					return self.form_invalid(form)
				
				

				# Determinar comprobante AFIP y letra
				codigo_afip_a = comprobante_data.codigo_afip_a
				codigo_afip_b = comprobante_data.codigo_afip_b

				if codigo_afip_a != codigo_afip_b:
					if id_discrimina_iva:
						comprobante_afip = codigo_afip_a
						letra = 'A'
					else:
						comprobante_afip = codigo_afip_b
						letra = 'B'
				else:
					comprobante_afip = codigo_afip_a
					# Buscar si ya existe un número para esta combinación
					numero_existente = Numero.objects.filter(
						id_sucursal=sucursal,
						id_punto_venta=punto_venta,
						comprobante=comprobante_afip
					).first()
					
					if numero_existente:
						letra = numero_existente.letra
						print("if numero_existente", letra)
					else:
						letra = "X"

				# Manejar la numeración según el tipo - Inicio

				# Manejar la numeración según el tipo - Fin
				
				# Bloquear y obtener/crear el número
				numero_obj, created = Numero.objects.select_for_update(nowait=True).get_or_create(
					id_sucursal=sucursal,
					id_punto_venta=punto_venta,
					comprobante=comprobante_afip,
					letra=letra,
					defaults={'numero': 0}
				)

				nuevo_numero = numero_obj.numero + 1
				Numero.objects.filter(pk=numero_obj.pk).update(numero=F('numero') + 1)

				form.instance.numero_comprobante = nuevo_numero
				form.instance.letra_comprobante = letra
				form.instance.compro = comprobante
				form.instance.full_clean()

				messages.success(self.request, f"Parte final de la asignación del documento")
				# Final 3. Numeración (nueva versión)

				# Condición de Venta
				condicion_comprobante = form.cleaned_data['condicion_comprobante']
				if condicion_comprobante == 1:
					# Venta de contado
					form.instance.entrega = form.instance.total  # Asignar el total a entrega
					form.instance.estado = "C"  # Marcar como cobrado ("C")

				# Verificación de Nota de Crédito
				comprobante_venta = form.cleaned_data['id_comprobante_venta']
				if comprobante_venta.libro_iva and comprobante_venta.mult_venta < 0:
					try:
						# 1. Obtener el documento asociado
						id_comprobante_asociado = form.cleaned_data['id_comprobante_asociado']
						documento_asociado = Factura.objects.select_for_update().get(id_factura=id_comprobante_asociado)
						
						# 2. Sumar el total de la NC al campo entrega del documento asociado
						nuevo_entrega = documento_asociado.entrega + form.instance.total
						actualizaciones = {'entrega': nuevo_entrega}
						
						# 3. Verificar si se completó el pago
						if nuevo_entrega >= documento_asociado.total:
							actualizaciones['estado'] = 'C'  # Marcamos como cobrado
						
						# 4. Actualizar el documento asociado
						Factura.objects.filter(id_factura=id_comprobante_asociado).update(**actualizaciones)
						
						# 5. Cerrar la Nota de Crédito
						form.instance.entrega = form.instance.total  # Asignar el total a entrega
						form.instance.estado = "C"  # Marcar como cobrado ("C")
						
					except Factura.DoesNotExist:
						form.add_error('id_comprobante_asociado', 'El documento asociado no existe')
						return self.form_invalid(form)
					except Exception as e:
						form.add_error(None, f'Error al procesar nota de crédito: {str(e)}')
						return self.form_invalid(form)

				# 4. Guardado en el modelo Factura
				self.object = form.save()

				# 5. ACTUALIZACIÓN DEL DOCUMENTO ASOCIADO (PARTE CLAVE)
				if comprobante_venta.pendiente:
					try:
						# Buscar el documento asociado (remito) con estado NULL o vacío
						documento_asociado = Factura.objects.filter(
								Q(compro=form.cleaned_data['comprobante_remito']) &
								Q(numero_comprobante=form.cleaned_data['remito']) &
								(Q(estado="") | Q(estado__isnull=True))
						).select_for_update().first()
						
						if documento_asociado:
								# Actualización directa y eficiente
								Factura.objects.filter(pk=documento_asociado.pk).update(
										estado="F"
								)
								print(f"Documento {documento_asociado.compro}-{documento_asociado.numero_comprobante} actualizado a estado 'F'")
						else:
								print("Advertencia: No se encontró el documento asociado para actualizar")
					except Exception as e:
						print(f"Error al actualizar documento asociado: {str(e)}")
						# No hacemos return para no impedir la creación de la factura principal

				# 6. ACTUALIZACIÓN DE LA AUTORIZACIÓN (NUEVO)
				if form.cleaned_data.get('id_valida'):  # Si tiene autorización asociada
					autorizacion = form.cleaned_data['id_valida']
					Valida.objects.filter(pk=autorizacion.pk).update(
							hs=timezone.now().time(),
							estatus_valida=False,
							# fecha_uso=timezone.now().date()  # Campo adicional para auditoría
					)
					print(f"Autorización {autorizacion.id_valida} marcada como utilizada")

				# 7. Guardado en el modelo Detallefactura y DetalleSerial
				formset_detalle.instance = self.object
				detalles = formset_detalle.save()
				
				formset_serial.instance = self.object 
				formset_serial.save() 						

				# 8. Actualización de inventario
				for detalle in detalles:
					# Solo actualizamos si es producto físico (tipo_producto = "P")
					# print("entró al bucle detalles!!!")
	
					if (hasattr(detalle.id_producto, 'tipo_producto') and 
						detalle.id_producto.tipo_producto == "P" and 
						detalle.cantidad):
						
						# Actualización segura con bloqueo
						# print("mult_stock", self.object.id_comprobante_venta.mult_stock)
	
						ProductoStock.objects.select_for_update().filter(
								id_producto=detalle.id_producto,
								id_deposito=deposito
						).update(
								#stock=F('stock') - detalle.cantidad,
								stock=F('stock') + (detalle.cantidad * self.object.id_comprobante_venta.mult_stock),
								fecha_producto_stock=fecha_comprobante
						)
				
				# Mensaje de confirmación de la creación de la factura y redirección
				messages.success(self.request, f"Documento {nuevo_numero} creado correctamente")
				return redirect(self.get_success_url())

						
		except DatabaseError as e:
			messages.error(self.request, "Error de concurrencia: Intente nuevamente")
			return self.form_invalid(form)
		except Exception as e:
			messages.error(self.request, f"Error inesperado: {str(e)}")
			return self.form_invalid(form)
		
	def form_invalid(self, form):
		print("Entro a form_invalid***")
		print("Errores del formulario principal:", form.errors)

		context = self.get_context_data()
		formset_detalle = context['formset_detalle']
		formset_serial = context['formset_serial']

		if formset_detalle:
			print("Errores del formset detalle:")
			for i, form_d in enumerate(formset_detalle):
				print(f"Form {i}:", form_d.errors)
				print("Non field errors:", form_d.non_field_errors())

		if formset_serial:
			print("Errores del formset serial:")
			for i, form_s in enumerate(formset_serial):
				print(f"Form {i}:", form_s.errors)

		return super().form_invalid(form)


	def get_success_url(self):
		return reverse(list_view_name)

	def get_initial(self):
		initial = super().get_initial()
		usuario = self.request.user  # Obtener el usuario autenticado

		# Establecer valores iniciales basados en el usuario
		initial['id_sucursal'] = usuario.id_sucursal
		initial['id_punto_venta'] = usuario.id_punto_venta
		initial['cambia_precio_descripcion'] = usuario.cambia_precio_descripcion
		#initial['jerarquia'] = usuario.jerarquia

		return initial

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['tipo_comprobante'] = self.tipo_comprobante  # Pasar tipo al formulario
		kwargs['usuario'] = self.request.user  # Pasar el usuario autenticado

		return kwargs

	def _asignar_numeracion_automatica(self, sucursal, punto_venta, comprobante_afip, letra, form):
		pass

	def _asignar_numeracion_manual(self, sucursal, punto_venta, comprobante_afip, letra, form):
		pass

	def _asignar_numeracion_electronica(self, sucursal, punto_venta, comprobante_afip, letra, fecha_comprobante, form):
		pass


# @method_decorator(login_required, name='dispatch')
class FacturaUpdateView(MaestroDetalleUpdateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name) # Nombre de la url.
	tipo_comprobante = 'electronico'  # Nuevo atributo de clase

	#-- Indicar el permiso que requiere para ejecutar la acción:
	# Obtener el nombre de la aplicación a la que pertenece el modelo.
	app_label = model._meta.app_label
	# Indicar el permiso eN el formato: <app_name>.<permiso>_<modelo>
	permission_required = f"{app_label}.change_{model.__name__.lower()}"

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		data['request'] = self.request  # Asegura que el token CSRF esté disponible 11/07/2025
		usuario = self.request.user
		data['cambia_precio_descripcion'] = usuario.cambia_precio_descripcion
		data['tipo_venta'] = TIPO_VENTA
		# data['tipo_doc_ident'] = TipoDocumentoIdentidad.objects.filter(estatus_tipo_documento=True)

		if self.request.POST:
			data['formset_detalle'] = DetalleFacturaFormSet(self.request.POST, instance=self.object)
			data['formset_serial'] = SerialFacturaFormSet(self.request.POST, instance=self.object)
		else:
			data['formset_detalle'] = DetalleFacturaFormSet(instance=self.object)
			data['formset_serial'] = SerialFacturaFormSet(instance=self.object)

		data['is_edit'] = True  # Indicar que es una edición

		# Obtener todos los comprobantes con sus valores libro_iva
		libro_iva_dict = {str(c.id_comprobante_venta): c.libro_iva for c in ComprobanteVenta.objects.all()}
		data['libro_iva_dict'] = json.dumps(libro_iva_dict)

		# Obtener todos los comprobantes con sus valores mult_venta
		mult_venta_dict = {str(c.id_comprobante_venta): c.mult_venta for c in ComprobanteVenta.objects.all()}
		data['mult_venta_dict'] = json.dumps(mult_venta_dict)

		# Obtener todos los comprobantes con sus valores electronica
		electronica_dict = {str(c.id_comprobante_venta): c.electronica for c in ComprobanteVenta.objects.all()}
		data['electronica_dict'] = json.dumps(electronica_dict)

		# Obtener todos los operarios con sus id
		operario_dict = {str(o.id_operario): o.nombre_operario for o in Operario.objects.all()}
		data['operario_dict'] = json.dumps(operario_dict)

		# Tipo de Comprobante
		data['tipo_comprobante'] = self.tipo_comprobante

		return data

	def form_valid(self, form):
		context = self.get_context_data()
		formset_detalle = context['formset_detalle']
		formset_serial = context['formset_serial']

		if formset_detalle.is_valid():
			try:
				with transaction.atomic():
					self.object = form.save()
					formset_detalle.instance = self.object
					formset_detalle.save()

				messages.success(self.request, "El Documento se ha actualizado correctamente.")
				return super().form_valid(form)
			except Exception as e:
				messages.error(self.request, f"Error al actualizar la factura: {str(e)}")
				return self.form_invalid(form)
		else:
			messages.error(self.request, "Error en el detalle de la factura. Revise los datos.")
			return self.form_invalid(form)

	def form_invalid(self, form):
		print("Entro a form_invalid$$$")
		print("Errores del formulario principal:", form.errors)

		context = self.get_context_data()
		formset_detalle = context['formset_detalle']

		if formset_detalle:
			print("Errores del formset:", formset_detalle.errors)

		return super().form_invalid(form)

	def get_success_url(self):
		return self.success_url

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['tipo_comprobante'] = self.tipo_comprobante  # Pasar tipo al formulario
		kwargs['usuario'] = self.request.user  # Pasar el usuario autenticado

		return kwargs


# @method_decorator(login_required, name='dispatch')
class FacturaDeleteView(MaestroDetalleDeleteView):
	model = modelo
	list_view_name = list_view_name
	template_name = "base_confirm_delete.html"
	success_url = reverse_lazy(list_view_name) # Nombre de la url.

	#-- Indicar el permiso que requiere para ejecutar la acción:
	# Obtener el nombre de la aplicación a la que pertenece el modelo.
	app_label = model._meta.app_label
	# Indicar el permiso en el formato: <app_name>.<permiso>_<modelo>
	permission_required = f"{app_label}.delete_{model.__name__.lower()}"

	extra_context = {
		"accion": f"Eliminar {model._meta.verbose_name}",
		"list_view_name" : list_view_name,
		"mensaje": "Estás seguro que deseas eliminar el Registro"
	}

	# Sobrescritura del método Post
	def post(self, request, *args, **kwargs):
		"""
		Sobrescribe el método post para añadir validación específica
		sin afectar el flujo general de otras vistas
		"""
		self.object = self.get_object()
		
		# Validación exclusiva para Factura (no afecta otros modelos)
		if hasattr(self.object, 'id_comprobante_venta') and self.object.id_comprobante_venta.electronica:
			messages.error(
				request,
				f"No se puede eliminar {self.object}: Comprobante electrónico",
				extra_tags='modal_error'  # Etiqueta para identificación en JS
			)
			return redirect(self.success_url)
			
		# Comportamiento normal para otros casos
		try:
			with transaction.atomic():
				return super().post(request, *args, **kwargs)
				
		except ProtectedError:
			messages.error(request, "No se puede eliminar (existen relaciones asociadas)")
			return redirect(self.success_url)
			
		except Exception as e:
			messages.error(request, f"Error inesperado: {str(e)}")
			return redirect(self.success_url)

# ------------------------------------------------------------------------------
