# neumatic\apps\maestros\forms\producto_minimo_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import Provincia
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProvinciaForm(CrudGenericForm):
	
	class Meta:
		model = Provincia
		fields = '__all__'
		
		widgets = {
			'estatus_provincia': 
				forms.Select(attrs={**formclassselect}),
			'codigo_provincia': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_provincia': 
				forms.TextInput(attrs={**formclasstext}),
		}
