# neumatic\apps\maestros\forms\empresa_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
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
				forms.TextInput(attrs={**formclasstext}),
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