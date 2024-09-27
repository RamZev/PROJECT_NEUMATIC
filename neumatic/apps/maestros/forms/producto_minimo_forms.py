# neumatic\apps\maestros\forms\producto_minimo_forms.py
from django import forms
from ..models.base_models import ProductoMinimo
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProductoMinimoForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoMinimo
		fields = '__all__'
		
		widgets = {
			'cai': 
				forms.TextInput(attrs={**formclasstext}),
			'minimo': 
				forms.TextInput(attrs={**formclasstext}),
			'id_deposito': 
				forms.Select(attrs={**formclassselect}),
		}
