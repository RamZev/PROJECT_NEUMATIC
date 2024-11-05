# neumatic\apps\maestros\forms\proveedor_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import *
from ..models.proveedor_models import Proveedor
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class ProveedorForm(CrudGenericForm):
	
	class Meta:
		model = Proveedor
		fields = '__all__'
		
		widgets = {
			'estatus_proveedor': 
				forms.Select(attrs={**formclassselect}),
			'nombre_proveedor': 
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_proveedor': 
				forms.TextInput(attrs={**formclasstext}),
			'id_provincia': 
				forms.Select(attrs={**formclassselect}),
			'id_localidad': 
				forms.Select(attrs={**formclassselect}),
			'codigo_postal': 
				forms.TextInput(attrs={**formclasstext, 'readonly': True}),
			'id_tipo_iva': 
				forms.Select(attrs={**formclassselect}),
			'cuit': 
				forms.TextInput(attrs={**formclasstext}),
			'id_tipo_retencion_ib': 
				forms.Select(attrs={**formclassselect}),
			'ib_numero': 
				forms.TextInput(attrs={**formclasstext}),
			'ib_exento': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'ib_alicuota': 
				forms.NumberInput(attrs={**formclasstext,
                           'min': 0, 'max': 99.99}),
			'multilateral': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'telefono_proveedor': 
				forms.TextInput(attrs={**formclasstext}),
			'movil_proveedor': 
				forms.TextInput(attrs={**formclasstext}),
			'email_proveedor': 
				forms.EmailInput(attrs={**formclasstext}),
			'observacion_proveedor': 
				forms.Textarea(attrs={**formclasstext, 'rows': '3'}),
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
  
  		