# neumatic\apps\ventas\forms\compra_otros_forms.py
from django import forms
from .forms_generics import GenericForm
from ..models.compra_models import Compra

from datetime import date

from apps.maestros.models.base_models import ComprobanteCompra
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck, formclassdate)


class CompraOtrosForm(GenericForm):
	
	class Meta:
		model = Compra
		fields = '__all__'
		
		widgets = {
			'estatus_comprabante': 
				forms.Select(attrs={**formclassselect}),
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'id_punto_venta': 
				forms.Select(attrs={**formclassselect}),
			'id_deposito': 
				forms.Select(attrs={**formclassselect}),
			'id_comprobante_compra': 
				forms.Select(attrs={**formclassselect}),
			'compro': 
				forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'letra_comprobante': 
				forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'numero_comprobante': 
				forms.NumberInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'fecha_comprobante': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
			'id_proveedor': 
				forms.Select(attrs={**formclassselect}),
			'id_provincia': 
				forms.Select(attrs={**formclassselect}),
			'condicion_comprobante': 
				forms.Select(attrs={**formclassselect}),
			
			'id_comprobante_venta': 
				forms.Select(attrs={**formclassselect}),
			'numero_comprobante_venta': 
				forms.NumberInput(attrs={**formclasstext, 'min': 1, 'max': 99999999}),
			'total_comprobante_venta': 
				forms.NumberInput(attrs={**formclasstext}),
			
			'fecha_registro': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
			'fecha_vencimiento': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
			'gravado': 
				forms.NumberInput(attrs={**formclasstext}),
			'no_gravado': 
				forms.NumberInput(attrs={**formclasstext}),
			'no_inscripto': 
				forms.NumberInput(attrs={**formclasstext}),
			'exento': 
				forms.NumberInput(attrs={**formclasstext}),
			'retencion_iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'retencion_ganancia': 
				forms.NumberInput(attrs={**formclasstext}),
			'retencion_ingreso_bruto': 
				forms.NumberInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'sellado': 
				forms.NumberInput(attrs={**formclasstext}),
			'percepcion_iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'percepcion_ingreso_bruto': 
				forms.NumberInput(attrs={**formclasstext}),
			'iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'total': 
				forms.NumberInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'entrega': 
				forms.NumberInput(attrs={**formclasstext}),
			'alicuota_iva': 
				forms.NumberInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'documento_asociado': 
				forms.TextInput(attrs={**formclasstext}),
			'observa_comprobante': 
				forms.TextInput(attrs={**formclasstext}),
		}
		
		error_messages = {
			'codigo_comprobante_compra': {
				'unique': 'Este Código de Comprobante de Compra ya existe.',
				# 'required': 'Debe completar este campo.',
				# 'invalid': 'Ingrese un valor válido.'
			},
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		allowed_codes = ["IB", "RG", "RI"]
		base_queryset = ComprobanteCompra.objects.filter(codigo_comprobante_compra__in=allowed_codes)

		# Si es una instancia existente y su comprobante no está en la lista, incluirlo
		if self.instance and self.instance.pk and self.instance.id_comprobante_compra:
			current_comprobante = self.instance.id_comprobante_compra
			if current_comprobante.codigo_comprobante_compra not in allowed_codes:
				base_queryset = ComprobanteCompra.objects.filter(
					pk=current_comprobante.pk
				) | base_queryset

		self.fields['id_comprobante_compra'].queryset = base_queryset

		# --- Asignar fecha de hoy a fecha_comprobante solo en creación ---
		if not self.instance.pk:  # Es un registro nuevo
			self.initial['fecha_comprobante'] = date.today()
			self.initial['fecha_registro'] = date.today()
			self.initial['fecha_vencimiento'] = date.today()