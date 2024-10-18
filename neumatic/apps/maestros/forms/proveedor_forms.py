# neumatic\apps\maestros\forms\proveedor_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
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
			'id_localidad': 
				forms.Select(attrs={**formclassselect}),
			'codigo_postal': 
				forms.TextInput(attrs={**formclasstext}),
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
                           'min': 0.01, 'max': 99.99}),
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
