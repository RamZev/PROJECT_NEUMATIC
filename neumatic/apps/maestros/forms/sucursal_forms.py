# neumatic\apps\maestros\forms\sucursal_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import *
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
				forms.NumberInput(attrs={**formclasstext,
							 'min':1, 'max': 99999}),
			'domicilio_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'codigo_postal': 
				forms.TextInput(attrs={**formclasstext, 'readonly': True}),
			'id_provincia':
				forms.Select(attrs={**formclassselect}),
   			'id_localidad':
				forms.Select(attrs={**formclassselect}),
			'telefono_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'email_sucursal':
				forms.EmailInput(attrs={**formclasstext}),
			'inicio_actividad':
				forms.TextInput(attrs={**formclassdate,
										 'type': 'date'}),
		}
  
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Verifica si estamos editando un registro con provincia ya seleccionada
		if self.instance and self.instance.pk and self.instance.id_provincia:
			# self.fields['id_localidad'].queryset = Localidad.objects.filter(id_provincia=self.instance.id_provincia).order_by('nombre_localidad')
   
			localidades = Localidad.objects.filter(id_provincia=self.instance.id_provincia).order_by('nombre_localidad')

			# Configura el campo para mostrar 'nombre_localidad - codigo_postal'
			self.fields['id_localidad'].choices = [
				(loc.id_localidad, f"{loc.nombre_localidad} - {loc.codigo_postal}")
				for loc in localidades
			]
   
		else:
			# En caso de nuevo registro o provincia no seleccionada, muestra un queryset vacío
			# self.fields['id_localidad'].queryset = Localidad.objects.none()
			self.fields['id_localidad'].choices = []
			
		# Opcional: si quieres que se muestre un mensaje de "Seleccione una localidad"
		# self.fields['id_localidad'].empty_label = "Seleccione una localidad"
		self.fields['id_localidad'].empty_label = "Seleccione una localidad"