# neumatic\apps\maestros\forms\producto_modelo_forms.py
from django import forms
from ..models.base_models import ProductoModelo
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProductoModeloForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoModelo
		fields = '__all__'
		
		widgets = {
			'estatus_modelo': 
				forms.Select(attrs={**formclassselect}),
			'nombre_modelo': 
				forms.TextInput(attrs={**formclasstext}),
		}
