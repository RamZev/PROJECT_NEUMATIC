# neumatic\apps\ventas\views\factura_views.py
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F  

from .msdt_views_generics import *
from ..models.factura_models import Factura
from ...maestros.models.numero_models import Numero
from ..forms.factura_forms import FacturaForm, DetalleFacturaFormSet
from ...maestros.models.base_models import TipoDocumentoIdentidad

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
 
	search_fields = [
	 'id_factura',
	 'numero_comprobante',
	 'cuit',
	 'id_cliente__nombre_cliente' #separar por guión bajo doble "__"
	]

	ordering = ['-fecha_comprobante']
	
 	#-- Encabezado de la Tabla.
	table_headers = {
		'id_factura': (1, 'ID'),
		'compro': (1, 'Compro'),
		'letra_comprobante': (1, 'Letra'),
		'numero_comprobante': (1, 'Nro Comp'),
		'fecha_comprobante': (1, 'fecha'),
		'cuit': (1, 'CUIT'),
		'id_cliente': (3, 'Cliente'),
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
	]
	
	#cadena_filtro = "Q(nombre_color__icontains=text)"
	extra_context = {
		"master_title": model._meta.verbose_name_plural,
		"home_view_name": home_view_name,
		"list_view_name": list_view_name,
		"create_view_name": create_view_name,
		"update_view_name": update_view_name,
		"delete_view_name": delete_view_name,
		"table_headers": table_headers,
		"table_data": table_data,
	}
 
	def get_queryset(self):
			# Obtener el queryset base
			queryset = super().get_queryset()

			# Obtener el usuario actual
			user = self.request.user

			# Si el usuario no es superusuario, filtrar por sucursal
			if not user.is_superuser:
					queryset = queryset.filter(id_sucursal=user.id_sucursal)

			# Aplicar búsqueda y ordenación
			query = self.request.GET.get('busqueda', None)
			if query:
					search_conditions = Q()
					for field in self.search_fields:
							search_conditions |= Q(**{f"{field}__icontains": query})
					queryset = queryset.filter(search_conditions)

			return queryset.order_by(*self.ordering)

# @method_decorator(login_required, name='dispatch')
class FacturaCreateView(MaestroDetalleCreateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name) # Nombre de la url.
 
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
			# print("Entro self.request.POST")
			data['formset_detalle'] = DetalleFacturaFormSet(self.request.POST)
		else:
			print("NO Entro self.request.POST")
			data['formset_detalle'] = DetalleFacturaFormSet(instance=self.object)
   
		data['is_edit'] = False  # Indicar que es una creación
   
		return data

 
	def form_valid(self, form):
		context = self.get_context_data()
		formset_detalle = context['formset_detalle']
  
		print("Entro a form_valid")

		if not formset_detalle.is_valid():
			return self.form_invalid(form)

		try:
				with transaction.atomic():
						# 1. Validación de campos obligatorios para numeración
						required_fields = {
								'id_sucursal': form.cleaned_data.get('id_sucursal'),
								'id_punto_venta': form.cleaned_data.get('id_punto_venta'),
								'compro': form.cleaned_data.get('compro'),
								'letra_comprobante': form.cleaned_data.get('letra_comprobante')
						}
      
						print("required_fields", required_fields)

						if None in required_fields.values():
								missing = [k for k, v in required_fields.items() if v is None]
								raise ValidationError(f"Campos requeridos faltantes: {', '.join(missing)}")

						# 2. Bloqueo y actualización atómica del número
						numero_obj, created = Numero.objects.select_for_update(
								nowait=True  # Opcional: evita espera indefinida
						).get_or_create(
								id_sucursal=required_fields['id_sucursal'],
								id_punto_venta=required_fields['id_punto_venta'],
								comprobante=required_fields['compro'],
								letra=required_fields['letra_comprobante'],
								defaults={'numero': 0, 'lineas': 1, 'copias': 1}
						)

						# 3. Incremento seguro del número
						nuevo_numero = numero_obj.numero + 1
						
						# Verificación de unicidad adicional (protección contra duplicados)
						if Factura.objects.filter(
								id_sucursal=required_fields['id_sucursal'],
								id_punto_venta=required_fields['id_punto_venta'],
								compro=required_fields['compro'],
								letra_comprobante=required_fields['letra_comprobante'],
								numero_comprobante=nuevo_numero
						).exists():
								raise ValidationError("El número de comprobante ya está en uso")

						# 4. Actualización del número
						Numero.objects.filter(pk=numero_obj.pk).update(numero=F('numero') + 1)
						numero_obj.refresh_from_db()  # Obtenemos el valor actualizado

						# 5. Asignación a la factura
						form.instance.numero_comprobante = numero_obj.numero

						# 6. Validación adicional del modelo
						form.instance.full_clean()

						# 7. Guardado del encabezado
						self.object = form.save()

						# 8. Guardado del detalle
						formset_detalle.instance = self.object
						formset_detalle.save()

						messages.success(self.request, "Factura creada correctamente")
						return redirect(self.get_success_url())

		except ValidationError as e:
				messages.error(self.request, f"Error de validación: {e}")
				return self.form_invalid(form)
		except Exception as e:
				messages.error(self.request, f"Error inesperado: {str(e)}")
				return self.form_invalid(form)

		# if formset_detalle.is_valid():
		# 	try:
		# 		with transaction.atomic():
		# 			# Guardar el encabezado de la factura
		# 			self.object = form.save()

		# 			# Asociar el detalle a la factura recién creada
		# 			formset_detalle.instance = self.object

		# 			# Guardar el detalle de la factura
		# 			formset_detalle.save()

		# 		# Mostrar mensaje de éxito
		# 		messages.success(self.request, "La factura se ha guardado correctamente.")

		# 		# Redirigir a la lista de facturas después de guardar
		# 		return super().form_valid(form)

		# 	except Exception as e:
		# 		# Manejar cualquier error durante el guardado
		# 		messages.error(self.request, f"Error al guardar la factura: {str(e)}")
		# 		return self.form_invalid(form)
		# else:
		# 	# Si el formset no es válido, mostrar errores
		# 	messages.error(self.request, "Error en el detalle de la factura. Revise los datos.")
		# 	return self.form_invalid(form)

	def form_invalid(self, form):
		print("Entro a form_invalid")
		print("Errores del formulario principal:", form.errors)
		
		context = self.get_context_data()
		formset_detalle = context['formset_detalle']
		
		if formset_detalle:
			print("Errores del formset:", formset_detalle.errors)

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
		kwargs['usuario'] = self.request.user  # Pasar el usuario autenticado

		return kwargs

# @method_decorator(login_required, name='dispatch')
class FacturaUpdateView(MaestroDetalleUpdateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name) # Nombre de la url.
 
	#-- Indicar el permiso que requiere para ejecutar la acción:
	# Obtener el nombre de la aplicación a la que pertenece el modelo.
	app_label = model._meta.app_label
	# Indicar el permiso eN el formato: <app_name>.<permiso>_<modelo>
	permission_required = f"{app_label}.change_{model.__name__.lower()}"

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		usuario = self.request.user
		data['cambia_precio_descripcion'] = usuario.cambia_precio_descripcion
		data['tipo_venta'] = TIPO_VENTA
		# data['tipo_doc_ident'] = TipoDocumentoIdentidad.objects.filter(estatus_tipo_documento=True)
		
		if self.request.POST:
			data['formset_detalle'] = DetalleFacturaFormSet(self.request.POST, instance=self.object)
		else:
			data['formset_detalle'] = DetalleFacturaFormSet(instance=self.object)
		
		data['is_edit'] = True  # Indicar que es una edición
		return data
 
	def form_valid(self, form):
		context = self.get_context_data()
		formset_detalle = context['formset_detalle']

		if formset_detalle.is_valid():
			try:
				with transaction.atomic():
					self.object = form.save()
					formset_detalle.instance = self.object
					formset_detalle.save()
				
				messages.success(self.request, "La factura se ha actualizado correctamente.")
				return super().form_valid(form)
			except Exception as e:
				messages.error(self.request, f"Error al actualizar la factura: {str(e)}")
				return self.form_invalid(form)
		else:
			messages.error(self.request, "Error en el detalle de la factura. Revise los datos.")
			return self.form_invalid(form)

	def form_invalid(self, form):
		print("Entro a form_invalid")
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
# ------------------------------------------------------------------------------
