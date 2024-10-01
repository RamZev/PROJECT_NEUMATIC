# neumatic\apps\maestros\forms\parametro_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.parametro_models import Parametro
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ParametroForm(CrudGenericForm):
	
	class Meta:
		model = Parametro
		fields = '__all__'
		
		widgets = {
			'estatus_parametro': 
				forms.Select(attrs={**formclassselect}),
			'id_empresa': 
				forms.Select(attrs={**formclassselect}),
			'interes': 
				forms.TextInput(attrs={**formclasstext}),
			'interes_dolar': 
				forms.TextInput(attrs={**formclasstext}),
			'cotizacion_dolar': 
				forms.TextInput(attrs={**formclasstext}),
			'dias_vencimiento': 
				forms.TextInput(attrs={**formclasstext}),
			'descuento_maximo': 
				forms.TextInput(attrs={**formclasstext}),
		}
