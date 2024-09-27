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
				forms.TextInput(attrs={**formclasstext}),
			'mult_saldo': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_stock': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_comision': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_caja': 
				forms.TextInput(attrs={**formclasstext}),
			'mult_estadistica': 
				forms.TextInput(attrs={**formclasstext}),
			'libro_iva': 
				forms.TextInput(attrs={**formclasscheck}),
			'estadistica': 
				forms.TextInput(attrs={**formclasscheck}),
			'electronica': 
				forms.TextInput(attrs={**formclasscheck}),
			'presupuesto': 
				forms.TextInput(attrs={**formclasscheck}),
			'pendiente': 
				forms.TextInput(attrs={**formclasscheck}),
			'info_michelin_auto': 
				forms.TextInput(attrs={**formclasscheck}),
			'info_michelin_camion': 
				forms.TextInput(attrs={**formclasscheck}),
			'codigo_afip_a': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_afip_b': 
				forms.TextInput(attrs={**formclasstext}),
			'compro_asociado': 
				forms.TextInput(attrs={**formclasstext}),
		}
