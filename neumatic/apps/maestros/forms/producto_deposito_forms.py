# neumatic\apps\maestros\forms\producto_stock_forms.py
from django import forms
from ..models.base_models import ProductoDeposito
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class ProductoDepositoForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoDeposito
		fields = '__all__'

		widgets = {
			'estatus_producto_deposito': 
				forms.Select(attrs={**formclassselect}),
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'nombre_producto_deposito': 
				forms.TextInput(attrs={**formclasstext}),
		}
