# neumatic\apps\maestros\forms\moneda_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import Moneda
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class MonedaForm(CrudGenericForm):
	
	class Meta:
		model = Moneda
		fields = '__all__'
		
		widgets = {
			'estatus_moneda': 
				forms.Select(attrs={**formclassselect}),
			'nombre_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'cotizacion_moneda': 
				forms.NumberInput(attrs={**formclasstext,
							'min': 1,
							'max': 99999999999.9999}),
			'simbolo_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'ws_afip': 
				forms.TextInput(attrs={**formclasstext}),
			'predeterminada': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
