# neumatic\apps\maestros\forms\actividad_forms.py
from django import forms
from ..models.base_models import Actividad
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate)


class ActividadForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = Actividad
		fields = '__all__'

		widgets = {
			'estatus_actividad': 
				forms.Select(attrs={**formclassselect}), 
			'descripcion_actividad': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Descripción Actividad'}),
			'fecha_registro_actividad': 
<<<<<<< HEAD
				forms.TextInput(attrs={'type':'date', **formclassdate}),
=======
				forms.TextInput(attrs={**formclassdate,
										'type': 'date',
										'placeholder': 'Fecha de Registro' }),
>>>>>>> f71623c58ffe87c8f648350694c7b54122edf9f7
			
		}
