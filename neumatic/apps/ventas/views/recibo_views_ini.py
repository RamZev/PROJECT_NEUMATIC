# neumatic\apps\ventas\views\recibo_views.py
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import transaction
from django.db.models import F
from django.db import DatabaseError
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

from .msdt_views_generics import *

from ...maestros.models.numero_models import Numero
from ..models.factura_models import Factura
from ..models.caja_models import Caja, CajaDetalle
from ..models.recibo_models import (
	DetalleRecibo,
	RetencionRecibo,
	DepositoRecibo,
	TarjetaRecibo,
	ChequeRecibo
)
from ..forms.recibo_forms import (
	FacturaReciboForm,
	DetalleReciboFormSet,
	RetencionReciboFormSet,
	DepositoReciboFormSet,
	TarjetaReciboFormSet,
	ChequeReciboFormSet,
	RetencionReciboForm,
	RetencionReciboInputForm,
	DepositoReciboInputForm,
	TarjetaReciboInputForm,
	ChequeReciboInputForm
)

modelo = Factura
model_string = "recibo"  # Usamos "recibo" aunque el modelo sea Factura, para las URLs
formulario = FacturaReciboForm

template_form = f"{model_string}_form.html"
home_view_name = "home"
list_view_name = f"{model_string}_list"
create_view_name = f"{model_string}_create"
update_view_name = f"{model_string}_update"
delete_view_name = f"{model_string}_delete"

class ReciboListView(MaestroDetalleListView):
	model = modelo
	template_name = f"ventas/maestro_detalle_list.html"
	context_object_name = 'objetos'

	search_fields = [
		'id_factura',
		'numero_comprobante',
		'cuit',
		'id_cliente__nombre_cliente'
	]

	ordering = ['-id_factura']

	table_headers = {
		'id_factura': (1, 'ID'),
		'compro': (1, 'Compro'),
		'letra_comprobante': (1, 'Letra'),
		'numero_comprobante': (1, 'Nro Comp'),
		'fecha_comprobante': (1, 'Fecha'),
		'cuit': (1, 'CUIT'),
		'id_cliente': (3, 'Cliente'),
		'total': (2, 'Total'),
		'opciones': (1, 'Opciones'),
	}

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

	extra_context = {
		"master_title": "Recibos",
		"home_view_name": home_view_name,
		"list_view_name": list_view_name,
		"create_view_name": create_view_name,
		"update_view_name": update_view_name,
		"delete_view_name": delete_view_name,
		"table_headers": table_headers,
		"table_data": table_data,
		"model_string_for_pdf": "factura",  # ¡Solución clave aquí!,
		"model_string": model_string,
	}

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user

		if not user.is_superuser:
			queryset = queryset.filter(id_sucursal=user.id_sucursal)

		# Filtrar solo facturas con recibos asociados
		queryset = queryset.filter(
		id_comprobante_venta__recibo=True
		).distinct()

		query = self.request.GET.get('busqueda', None)
		if query:
			search_conditions = Q()
			for field in self.search_fields:
				search_conditions |= Q(**{f"{field}__icontains": query})
			queryset = queryset.filter(search_conditions)

		return queryset.order_by(*self.ordering)

class ReciboCreateView(MaestroDetalleCreateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name)
	
	app_label = model._meta.app_label
	permission_required = f"{app_label}.add_{model.__name__.lower()}"

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		usuario = self.request.user

		if self.request.POST:
			data['formset_recibo'] = DetalleReciboFormSet(self.request.POST, prefix='detallerecibo_set')
			print(f"Prefijo de formset_recibo (POST): {data['formset_recibo'].prefix}")
			data['formset_retencion'] = RetencionReciboFormSet(self.request.POST)
			data['formset_deposito'] = DepositoReciboFormSet(self.request.POST)
			data['formset_tarjeta'] = TarjetaReciboFormSet(self.request.POST)
			data['formset_cheque'] = ChequeReciboFormSet(self.request.POST)
		else:
			data['formset_recibo'] = DetalleReciboFormSet(queryset=DetalleRecibo.objects.none(), prefix='detallerecibo_set')
			print(f"Prefijo de formset_recibo (GET): {data['formset_recibo'].prefix}")
			data['formset_retencion'] = RetencionReciboFormSet(queryset=RetencionRecibo.objects.none())
			data['formset_deposito'] = DepositoReciboFormSet(queryset=DepositoRecibo.objects.none())
			data['formset_tarjeta'] = TarjetaReciboFormSet(queryset=TarjetaRecibo.objects.none())
			data['formset_cheque'] = ChequeReciboFormSet(queryset=ChequeRecibo.objects.none())

		data['form_retencion_input'] = RetencionReciboForm()
		data['form_deposito_input'] = DepositoReciboInputForm()  # Nuevo
		data['form_tarjeta_input'] = TarjetaReciboInputForm()
		data['form_cheque_input'] = ChequeReciboInputForm()
		data['is_edit'] = False
		return data

	def form_valid_ini(self, form):
		context = self.get_context_data()
		formsets = [
			context['formset_recibo'],
			context['formset_retencion'],
			context['formset_deposito'],
			context['formset_tarjeta'],
			context['formset_cheque']
		]

		if not all([formset.is_valid() for formset in formsets]):
			return self.form_invalid(form)

		try:
			with transaction.atomic():
				self.object = form.save()
				
				# Guardar todos los formsets
				for formset in formsets:
					formset.instance = self.object
					formset.save()

				messages.success(self.request, "Recibo creado correctamente")
				return redirect(self.get_success_url())

		except DatabaseError as e:
			messages.error(self.request, "Error de concurrencia: Intente nuevamente")
			return self.form_invalid(form)
		except Exception as e:
			messages.error(self.request, f"Error inesperado: {str(e)}")
			return self.form_invalid(form)
	
	def form_valid(self, form):
		context = self.get_context_data()
		formsets = [
			context['formset_recibo'],
			context['formset_retencion'],
			context['formset_deposito'],
			context['formset_tarjeta'],
			context['formset_cheque']
		]

		for i, formset in enumerate(formsets):
			if not formset.is_valid():
				print(f"Formset {i} no es válido. Errores:", formset.errors)
				print(f"Management form errores:", formset.management_form.errors)
				return self.form_invalid(form)

		try:
			with transaction.atomic():
				# 1. Obtener datos para la numeración
				sucursal = form.cleaned_data['id_sucursal']
				punto_venta = form.cleaned_data['id_punto_venta']
				comprobante = form.cleaned_data['compro']
				letra = form.cleaned_data['letra_comprobante']

				# 2. Obtener o crear el número en el modelo Numero
				numero_obj, created = Numero.objects.select_for_update(
					nowait=True
				).get_or_create(
					id_sucursal=sucursal,
					id_punto_venta=punto_venta,
					comprobante=comprobante,
					letra=letra,
					defaults={'numero': 0}
				)

				# 3. Calcular el nuevo número y actualizar el modelo Numero
				nuevo_numero = numero_obj.numero + 1
				Numero.objects.filter(pk=numero_obj.pk).update(numero=F('numero') + 1)
				form.instance.numero_comprobante = nuevo_numero
				form.instance.full_clean()  # Validar el formulario con el nuevo número

				# Asignar total_cobrado a entrega
				total_cobrado = form.cleaned_data.get('total_cobrado', 0.0)
				print('total_cobrado:', total_cobrado)
				form.instance.entrega = total_cobrado
				
				# 4. Guardar el formulario principal (Factura/Recibo)
				self.object = form.save()
				
				# 5. Guardar los formsets
				for formset in formsets:
					formset.instance = self.object
					formset.save()
				
				# 6. Actualizar el campo entrega en Factura para los detalles con monto_cobrado > 0
				for detalle in self.object.detalles_recibo.filter(monto_cobrado__gt=0):
					factura = detalle.id_factura_cobrada
					if factura:
						print("actualizando monto de enterega en Factura")
						factura.entrega += detalle.monto_cobrado
						factura.save()
				
				messages.success(self.request, "Recibo creado correctamente")
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
		formset_recibo= context['formset_recibo']

		if formset_recibo:
			print("Errores del formset:", formset_recibo.errors)
			return super().form_invalid(form)

		if formset_recibo:
			print("Errores del formset:", formset_recibo.errors)

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


class ReciboUpdateView(MaestroDetalleUpdateView):
	model = modelo
	list_view_name = list_view_name
	form_class = formulario
	template_name = f"ventas/{template_form}"
	success_url = reverse_lazy(list_view_name)
	
	app_label = model._meta.app_label
	permission_required = f"{app_label}.change_{model.__name__.lower()}"

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		
		if self.request.POST:
			data['formset_recibo'] = DetalleReciboFormSet(self.request.POST, instance=self.object)
			data['formset_retencion'] = RetencionReciboFormSet(self.request.POST, instance=self.object)
			data['formset_deposito'] = DepositoReciboFormSet(self.request.POST, instance=self.object)
			data['formset_tarjeta'] = TarjetaReciboFormSet(self.request.POST, instance=self.object)
			data['formset_cheque'] = ChequeReciboFormSet(self.request.POST, instance=self.object)
		else:
			data['formset_recibo'] = DetalleReciboFormSet(
				instance=self.object,
				initial=[
					{
						'id_detalle_recibo': detalle.id_detalle_recibo,
						'id_factura': detalle.id_factura,
						'id_factura_cobrada': detalle.id_factura_cobrada_id,
						'monto_cobrado': detalle.monto_cobrado,
						'comprobante': detalle.id_factura_cobrada.id_comprobante_venta.nombre_comprobante_venta,
						'letra_comprobante': detalle.id_factura_cobrada.letra_comprobante,
						'numero_comprobante': detalle.id_factura_cobrada.numero_comprobante,
						'fecha_comprobante': detalle.id_factura_cobrada.fecha_comprobante.strftime('%d/%m/%Y'),
						'total': detalle.id_factura_cobrada.total,
						'entrega': detalle.id_factura_cobrada.entrega,
						'saldo': detalle.id_factura_cobrada.total - detalle.id_factura_cobrada.entrega,
					} for detalle in DetalleRecibo.objects.filter(id_factura=self.object).select_related('id_factura_cobrada__id_comprobante_venta')
				]
			)
			data['formset_retencion'] = RetencionReciboFormSet(instance=self.object)
			data['formset_deposito'] = DepositoReciboFormSet(instance=self.object)
			data['formset_tarjeta'] = TarjetaReciboFormSet(instance=self.object)
			data['formset_cheque'] = ChequeReciboFormSet(instance=self.object)

		# Usar RetencionReciboInputForm para la fila de inserción
		data['form_retencion_input'] = RetencionReciboInputForm()
		data['form_deposito_input'] = DepositoReciboInputForm()
		data['form_tarjeta_input'] = TarjetaReciboInputForm()
		data['form_cheque_input'] = ChequeReciboInputForm()
		data['is_edit'] = True
		return data

	def form_valid(self, form):
		context = self.get_context_data()
		formsets = [
			context['formset_recibo'],
			context['formset_retencion'],
			context['formset_deposito'],
			context['formset_tarjeta'],
			context['formset_cheque']
		]

		if not all([formset.is_valid() for formset in formsets]):
			return self.form_invalid(form)

		try:
			with transaction.atomic():
				self.object = form.save()
				
				for formset in formsets:
					formset.instance = self.object
					formset.save()

				messages.success(self.request, "Recibo actualizado correctamente")
				return redirect(self.get_success_url())

		except Exception as e:
			messages.error(self.request, f"Error al actualizar: {str(e)}")
			return self.form_invalid(form)
		
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['usuario'] = self.request.user  # Pasar el usuario autenticado

		return kwargs

class ReciboDeleteView(MaestroDetalleDeleteView):
	model = modelo
	list_view_name = list_view_name
	template_name = "base_confirm_delete.html"
	success_url = reverse_lazy(list_view_name)
	
	app_label = model._meta.app_label
	permission_required = f"{app_label}.delete_{model.__name__.lower()}"

	extra_context = {
		"accion": "Eliminar Recibo",
		"list_view_name": list_view_name,
		"mensaje": "¿Estás seguro que deseas eliminar este Recibo?"
	}