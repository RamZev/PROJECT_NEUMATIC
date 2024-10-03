# neumatic\apps\maestros\forms\numero_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.numero_models import Numero
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class NumeroForm(CrudGenericForm):
	
	class Meta:
		model = Numero
		fields = '__all__'
		
		widgets = {
			'estatus_numero': 
				forms.Select(attrs={**formclassselect}),
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'punto_venta': 
				forms.TextInput(attrs={**formclasstext}),
			'comprobante': 
				forms.TextInput(attrs={**formclasstext}),
			'letra': 
				forms.TextInput(attrs={**formclasstext}),
			'numero': 
				forms.TextInput(attrs={**formclasstext}),
			'lineas': 
				forms.TextInput(attrs={**formclasstext}),
			'copias': 
				forms.TextInput(attrs={**formclasstext}),
		}
