# neumatic\apps\ventas\views\factura_views.py
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db import DatabaseError

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO

from .msdt_views_generics import *
from ..models.factura_models import Factura
from ...maestros.models.numero_models import Numero
from ..forms.factura_forms import FacturaForm, DetalleFacturaFormSet
from ...maestros.models.base_models import ProductoStock

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

			if not formset_detalle.is_valid():
					return self.form_invalid(form)

			try:
					with transaction.atomic():
							# 1. Validación mínima necesaria
							deposito = form.cleaned_data.get('id_deposito')
							if not deposito:
									form.add_error('id_deposito', 'Debe seleccionar un depósito')
									return self.form_invalid(form)

							# 2. Numeración (igual que en versión original)
							sucursal = form.cleaned_data['id_sucursal']
							punto_venta = form.cleaned_data['id_punto_venta']
							comprobante = form.cleaned_data['compro']
							letra = form.cleaned_data['letra_comprobante']
							fecha_comprobante = form.cleaned_data['fecha_comprobante']

							numero_obj, created = Numero.objects.select_for_update(
									nowait=True
							).get_or_create(
									id_sucursal=sucursal,
									id_punto_venta=punto_venta,
									comprobante=comprobante,
									letra=letra,
									defaults={'numero': 0}
							)

							nuevo_numero = numero_obj.numero + 1
							Numero.objects.filter(pk=numero_obj.pk).update(numero=F('numero') + 1)
							
							form.instance.numero_comprobante = nuevo_numero
							form.instance.full_clean()

							# 3. Guardado directo (como en versión original que funcionaba)
							self.object = form.save()
							formset_detalle.instance = self.object
							# formset_detalle.save()
							detalles = formset_detalle.save()
       
							# 4. Actualización de inventario (NUEVA SECCIÓN)
							for detalle in detalles:
								# Solo actualizamos si es producto físico (tipo_producto = "P")
								print("entró al bucle detalles!!!")
				
								if (hasattr(detalle.id_producto, 'tipo_producto') and 
										detalle.id_producto.tipo_producto == "P" and 
										detalle.cantidad):
										
										# Actualización segura con bloqueo
										print("mult_stock", self.object.id_comprobante_venta.mult_stock)
					
										ProductoStock.objects.select_for_update().filter(
												id_producto=detalle.id_producto,
												id_deposito=deposito
										).update(
												#stock=F('stock') - detalle.cantidad,
												stock=F('stock') + (detalle.cantidad * self.object.id_comprobante_venta.mult_stock),
												fecha_producto_stock=fecha_comprobante
										)
							
							# Mensaje de confirmación de la creación de la factura y redirección
							messages.success(self.request, f"Factura {nuevo_numero} creada correctamente")
							return redirect(self.get_success_url())

							
			except DatabaseError as e:
					messages.error(self.request, "Error de concurrencia: Intente nuevamente")
					return self.form_invalid(form)
			except Exception as e:
					messages.error(self.request, f"Error inesperado: {str(e)}")
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
