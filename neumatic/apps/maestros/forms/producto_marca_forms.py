# neumatic\apps\maestros\forms\producto_marca_forms.py
from django import forms
from ..models.base_models import ProductoMarca
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class ProductoMarcaForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoMarca
		fields = '__all__'
		
		widgets = {
			'estatus_producto_marca': 
				forms.Select(attrs={**formclassselect}),
			'nombre_producto_marca': 
				forms.TextInput(attrs={**formclasstext}),
			'principal': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'id_moneda': 
				forms.Select(attrs={**formclassselect}),
		}
