# neumatic\apps\maestros\forms\tipo_iva_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import TipoPercepcionIb
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class TipoPercepcionIbForm(CrudGenericForm):
	
	class Meta:
		model = TipoPercepcionIb
		fields = '__all__'
		
		widgets = {
			'estatus_tipo_percepcion_ib': 
				forms.Select(attrs={**formclassselect}),
			'descripcion_tipo_percepcion_ib': 
				forms.TextInput(attrs={**formclasstext}),
			'alicuota': 
				forms.TextInput(attrs={**formclasstext}),
			'monto': 
				forms.TextInput(attrs={**formclasstext}),
			'minimo': 
				forms.TextInput(attrs={**formclasstext}),
			'neto_total': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
