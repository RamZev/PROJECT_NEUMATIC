# neumatic\apps\maestros\forms\producto_minimo_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import ProductoMinimo
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProductoMinimoForm(CrudGenericForm):
	
	class Meta:
		model = ProductoMinimo
		fields = '__all__'
		
		widgets = {
			'cai': 
				forms.TextInput(attrs={**formclasstext}),
			'minimo': 
				forms.NumberInput(attrs={**formclasstext, 
							 	  'min': 1, 'max': 99}),
			'id_deposito': 
				forms.Select(attrs={**formclassselect}),
		}
