# neumatic\apps\maestros\forms\producto_stock_forms.py
from django import forms
from ..models.base_models import ProductoStock
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate)


class ProductoStockForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoStock
		fields = '__all__'

		widgets = {
			'id_producto': 
				forms.Select(attrs={**formclassselect}),
			'id_deposito': 
				forms.Select(attrs={**formclassselect}),
			'stock': 
				forms.TextInput(attrs={**formclasstext}),
			'minimo': 
				forms.TextInput(attrs={**formclasstext}),
			'fecha_producto_stock': 
				forms.TextInput(attrs={**formclassdate, 'type': 'date'}),
		}
