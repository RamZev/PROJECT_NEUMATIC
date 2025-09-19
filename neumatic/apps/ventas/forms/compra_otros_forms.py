# neumatic\apps\ventas\forms\compra_otros_forms.py
from django import forms
from .forms_generics import GenericForm
from ..models.compra_models import Compra
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
				forms.TextInput(attrs={**formclasstext, 'oninput': 'this.value = this.value.toUpperCase()'}),
			'letra_comprobante': 
				forms.TextInput(attrs={**formclasstext, 'oninput': 'this.value = this.value.toUpperCase()'}),
			'numero_comprobante': 
				forms.NumberInput(attrs={**formclasstext, 'min': 1, 'max': 99999999}),
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
			'fecha_comprobante_venta': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
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
				forms.NumberInput(attrs={**formclasstext}),
			'sellado': 
				forms.NumberInput(attrs={**formclasstext}),
			'percepcion_iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'percepcion_ingreso_bruto': 
				forms.NumberInput(attrs={**formclasstext}),
			'iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'total': 
				forms.NumberInput(attrs={**formclasstext}),
			'entrega': 
				forms.NumberInput(attrs={**formclasstext}),
			'alicuota_iva': 
				forms.NumberInput(attrs={**formclasstext}),
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
