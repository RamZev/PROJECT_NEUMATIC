# neumatic\apps\maestros\forms\sucursal_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.sucursal_models import Sucursal
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate)


class SucursalForm(CrudGenericForm):
	
	class Meta:
		model = Sucursal
		fields = '__all__'
		
		widgets = {
			'estatus_sucursal':
				forms.Select(attrs={**formclassselect}),
			'nombre_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'codigo_michelin':
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'id_localidad':
				forms.Select(attrs={**formclassselect}),
			'id_provincia':
				forms.Select(attrs={**formclassselect}),
			'telefono_sucursal':
				forms.NumberInput(attrs={**formclasstext,
										 'min': 1, 'max': 999999999999999}),
			'email_sucursal':
				forms.EmailInput(attrs={**formclasstext}),
			'inicio_actividad':
				forms.TextInput(attrs={**formclassdate,
									   'type': 'date'}),
		}
