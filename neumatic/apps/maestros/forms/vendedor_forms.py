# neumatic\apps\maestros\forms\vendedor_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.vendedor_models import Vendedor
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class VendedorForm(CrudGenericForm):
	
	class Meta:
		model = Vendedor
		fields = '__all__'

		widgets = {
			'estatus_vendedor': 
				forms.Select(attrs={**formclassselect}), 
			'nombre_vendedor': 
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_vendedor': 
				forms.TextInput(attrs={**formclasstext}),
			'email_vendedor': 
				forms.EmailInput(attrs={**formclasstext}),
			'telefono_vendedor': 
				forms.TextInput(attrs={**formclasstext}),
			'pje_auto': 
				forms.NumberInput(attrs={**formclasstext}),
			'pje_camion': 
				forms.NumberInput(attrs={**formclasstext}),			
			'vence_factura': 
				forms.NumberInput(attrs={**formclasstext}),	
			'vence_remito': 
				forms.NumberInput(attrs={**formclasstext}),	
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'tipo_venta': 
				forms.Select(attrs={**formclassselect}),
			'col_descuento': 
				forms.NumberInput(attrs={**formclasstext}),
			'email_venta': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'info_saldo': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'info_estadistica':
				forms.CheckboxInput(attrs={**formclasscheck})
		}
