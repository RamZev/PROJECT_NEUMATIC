# neumatic\apps\maestros\forms\comprobante_venta_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import ComprobanteVenta
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class ComprobanteVentaForm(CrudGenericForm):
	
	class Meta:
		model = ComprobanteVenta
		fields = '__all__'
		
		widgets = {
			'estatus_comprobante_venta': 
				forms.Select(attrs={**formclassselect}),
			'codigo_comprobante_venta': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_comprobante_venta': 
				forms.TextInput(attrs={**formclasstext}),
			'impresion': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_venta': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'mult_saldo': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'mult_stock': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'mult_comision': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'mult_caja': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'mult_estadistica': 
				forms.NumberInput(attrs={**formclasstext, 'min': -1, 'max': 1}),
			'libro_iva': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'estadistica': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'electronica': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'presupuesto': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'pendiente': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'remito': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'info_michelin_auto': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'info_michelin_camion': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'codigo_afip_a': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_afip_b': 
				forms.TextInput(attrs={**formclasstext}),
			'compro_asociado': 
				forms.TextInput(attrs={**formclasstext}),
		}
		
		error_messages = {
			'codigo_comprobante_venta': {
				'unique': 'Este Código de Comprobante de Venta ya existe.',
				# 'required': 'Debe completar este campo.',
				# 'invalid': 'Ingrese un valor válido.'
			},
		}
