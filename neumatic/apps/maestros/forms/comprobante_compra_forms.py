# neumatic\apps\maestros\forms\comprobante_venta_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import ComprobanteCompra
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class ComprobanteCompraForm(CrudGenericForm):
	
	class Meta:
		model = ComprobanteCompra
		fields = '__all__'
		
		widgets = {
			'estatus_comprobante_compra': 
				forms.Select(attrs={**formclassselect}),
			'codigo_comprobante_compra': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_comprobante_compra': 
				forms.TextInput(attrs={**formclasstext}),
			
			'mult_compra': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_saldo': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_stock': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_caja': 
				forms.TextInput(attrs={**formclasstext}),
			
			'libro_iva': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			
			'codigo_afip_a': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_afip_b': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_afip_c': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_afip_m': 
				forms.TextInput(attrs={**formclasstext}),
		}
