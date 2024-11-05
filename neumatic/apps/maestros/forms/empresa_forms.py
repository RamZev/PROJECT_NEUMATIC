# neumatic\apps\maestros\forms\empresa_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import *
from ..models.empresa_models import Empresa
from diseno_base.diseno_bootstrap import(
	formclasstext, formclassselect, formclassdate)


class EmpresaForm(CrudGenericForm):
	
	class Meta:
		model = Empresa
		fields ='__all__'
		
		widgets = {
			'estatus_empresa':
				forms.Select(attrs={**formclassselect}),
			'nombre_fiscal':
				forms.TextInput(attrs={**formclasstext}),
			'nombre_comercial':
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_empresa':
				forms.TextInput(attrs={**formclasstext}),
			'codigo_postal':
				forms.TextInput(attrs={**formclasstext, 'readonly': True}),
			'id_localidad':
				forms.Select(attrs={**formclassselect}),
			'id_provincia':
				forms.Select(attrs={**formclassselect}),
			'id_iva':
				forms.Select(attrs={**formclassselect}),
			'cuit':
				forms.TextInput(attrs={**formclasstext}),
			'ingresos_bruto':
				forms.TextInput(attrs={**formclasstext}),
			'inicio_actividad': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),
			'cbu':
				forms.TextInput(attrs={**formclasstext}),
			'cbu_alias':
				forms.TextInput(attrs={**formclasstext}),
			'cbu_vence': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),
			'telefono':
				forms.TextInput(attrs={**formclasstext}),
			'email_empresa':
				forms.EmailInput(attrs={**formclasstext}),
			'web_empresa':
				forms.TextInput(attrs={**formclasstext}),
			
			'logo_empresa':
				forms.TextInput(attrs={**formclasstext,}),
			
			'ws_archivo_crt':
				forms.TextInput(attrs={**formclasstext}),
			'ws_archivo_key':
				forms.TextInput(attrs={**formclasstext}),
			'ws_token':
				forms.Textarea(attrs={**formclasstext, 
							'rows': 3, 'readonly': True}),
			'ws_sign':
				forms.Textarea(attrs={**formclasstext, 
							'rows': 3, 'readonly': True}),
			'ws_expiracion':
				forms.TextInput(attrs={**formclassdate,
										'type': 'date', 
										'readonly': True}),
			'ws_modo':
				forms.Select(attrs={**formclassselect}),
			'ws_vence':
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),
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