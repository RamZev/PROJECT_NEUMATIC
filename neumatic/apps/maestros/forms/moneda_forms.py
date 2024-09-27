# neumatic\apps\maestros\forms\producto_familia_forms.py
from django import forms
from ..models.base_models import Moneda
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class MonedaForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = Moneda
		fields = '__all__'

		widgets = {
			'estatus_moneda': 
				forms.Select(attrs={**formclassselect}),
			'nombre_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'cotizacion_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'simbolo_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'ws_afip': 
				forms.TextInput(attrs={**formclasstext}),
			'predeterminada': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
