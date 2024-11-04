# neumatic\apps\maestros\forms\cliente_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import *
from ..models.cliente_models import Cliente
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck, formclassdate)

class ClienteForm(CrudGenericForm):
		
	class Meta:
		model = Cliente
		fields ='__all__'
		
		widgets = {
			'estatus_cliente': 
				forms.Select(attrs={**formclassselect}),
			'nombre_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'codigo_postal': 
				forms.TextInput(attrs={**formclasstext}),
			'id_provincia': 
				forms.Select(attrs={**formclassselect}),
			'id_localidad': 
				forms.Select(attrs={**formclassselect}),
			'tipo_persona': 
				forms.Select(attrs={**formclassselect}),
			'id_tipo_iva': 
				forms.Select(attrs={**formclassselect}),
			'id_tipo_documento_identidad': 
				forms.Select(attrs={**formclassselect}),
			'cuit': 
				forms.TextInput(attrs={**formclasstext}),
			'condicion_venta': 
				forms.Select(attrs={**formclassselect}),
			'telefono_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'fax_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'movil_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'email_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'email2_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'transporte_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'id_vendedor': 
				forms.Select(attrs={**formclassselect}),
			'fecha_nacimiento': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
			'fecha_alta': 
				forms.TextInput(attrs={'type':'date', **formclassdate, 'readonly': True}),
   			'sexo': 
				forms.Select(attrs={**formclassselect}),
			'id_actividad': 
				forms.Select(attrs={**formclassselect}),
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'id_percepcion_ib':
				forms.Select(attrs={**formclassselect}),
			'numero_ib': 
				forms.TextInput(attrs={**formclasstext}),
			'transporte_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'vip': 
				forms.Select(attrs={**formclassselect}),
			'mayorista': 
				forms.Select(attrs={**formclassselect}),
			'sub_cuenta': 
				forms.TextInput(attrs={**formclasstext}),
   			'observaciones_cliente': 
				forms.TextInput(attrs={**formclasstext}),
			'black_list': 
				forms.Select(attrs={**formclassselect}),
			'black_list_motivo': 
				forms.TextInput(attrs={**formclasstext}),
			'black_list_usuario': 
				forms.TextInput(attrs={**formclasstext}),
			'fecha_baja': 
				forms.TextInput(attrs={'type':'date', **formclassdate}),
	
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Verifica si estamos editando un registro con provincia ya seleccionada
		if self.instance and self.instance.pk and self.instance.id_provincia:
			self.fields['id_localidad'].queryset = Localidad.objects.filter(id_provincia=self.instance.id_provincia)
		else:
			# En caso de nuevo registro o provincia no seleccionada, muestra un queryset vacío
			self.fields['id_localidad'].queryset = Localidad.objects.none()
			
		# Opcional: si quieres que se muestre un mensaje de "Seleccione una localidad"
		self.fields['id_localidad'].empty_label = "Seleccione una localidad"
