# neumatic\apps\maestros\forms\tipo_iva_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import TipoIva
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class TipoIvaForm(CrudGenericForm):
	
	class Meta:
		model = TipoIva
		fields = '__all__'
		
		widgets = {
			'estatus_tipo_iva': 
				forms.Select(attrs={**formclassselect}),
			'codigo_iva': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_iva': 
				forms.TextInput(attrs={**formclasstext}),
			'discrimina_iva': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
		
		error_messages = {
			'codigo_iva': {
				'unique': 'Ya existe un tipo de IVA con el mismo código.',
				# 'required': 'Debe completar este campo.',
				# 'invalid': 'Ingrese un valor válido.'
			},
		}
