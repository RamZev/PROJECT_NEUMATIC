# neumatic\apps\maestros\forms\localidad_forms.py
from django import forms
from ..models.base_models import Localidad
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class LocalidadForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = Localidad
		fields = '__all__'
		
		widgets = {
			'estatus_localidad': 
				forms.Select(attrs={**formclassselect}),
			'id_provincia': 
				forms.Select(attrs={**formclassselect}),
			'codigo_postal': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_localidad': 
				forms.TextInput(attrs={**formclasstext}),
		}
