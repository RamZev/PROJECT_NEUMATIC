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
			'interes':
				forms.NumberInput(
					attrs={**formclasstext,
						   'min': -99.99, 'max': 99.99}),
			'interes_dolar':
				forms.NumberInput(
					attrs={**formclasstext, 
						   'min': -99.99, 'max': 99.99}),
			'cotizacion_dolar':
				forms.NumberInput(
					attrs={**formclasstext, 
						   'min': 0, 'max': 9999999999999.99}),
			'dias_vencimiento':
				forms.NumberInput(
					attrs={**formclasstext, 
						   'min': 0, 'max': 999}),
			'descuento_maximo':
				forms.NumberInput(
					attrs={**formclasstext, 
						   'min': -99.99, 'max': 99.99}),
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.fields['id_localidad'].choices = []
		
		#-- Verificar si el formulario se llama con datos (POST).
		if self.is_bound:
			#-- Obtener el valor enviado de id_provincia_tarjeta.
			provincia_id = self.data.get('id_provincia')
			localidad_id = self.data.get('id_localidad', '')
			
			if provincia_id:
				#-- Filtrar localidades según la provincia enviada.
				localidades = Localidad.objects.filter(id_provincia=provincia_id).order_by('nombre_localidad')
				self.fields['id_localidad'].choices = [("", "Seleccione una localidad")] + [
					(loc.id_localidad, f"{loc.nombre_localidad} - {loc.codigo_postal}") for loc in localidades
				]
				self.initial['id_localidad'] = localidad_id
			else:
				self.fields['id_localidad'].choices = [("", "Seleccione una localidad")]
			
		#-- Si se está editando un registro existente.
		elif self.instance and self.instance.pk and self.instance.id_provincia:
			localidades = Localidad.objects.filter(id_provincia=self.instance.id_provincia).order_by('nombre_localidad')
			self.fields['id_localidad'].choices = [
				(loc.id_localidad, f"{loc.nombre_localidad} - {loc.codigo_postal}")
				for loc in localidades
			]
			
			#-- Establecer localidad seleccionada inicialmente.
			if self.instance.id_localidad:
				self.initial['id_localidad'] = self.instance.id_localidad.id_localidad
		
		#-- Asegurar que exista una opción inicial en cualquier caso.
		self.fields['id_localidad'].choices.insert(0, ("", "Seleccione una localidad"))
