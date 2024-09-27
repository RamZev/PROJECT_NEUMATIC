# neumatic\apps\maestros\forms\producto_familia_forms.py
from django import forms
from ..models.base_models import ProductoFamilia
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProductoFamiliaForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoFamilia
		fields = '__all__'

		widgets = {
			'estatus_producto_familia': 
				forms.Select(attrs={**formclassselect}),
			'nombre_producto_familia': 
				forms.TextInput(attrs={**formclasstext}),
			'comision_operario': 
				forms.TextInput(attrs={**formclasstext}),
		}
