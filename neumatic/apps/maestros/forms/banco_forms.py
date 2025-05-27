# neumatic\apps\maestros\forms\banco_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import Banco
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class BancoForm(CrudGenericForm):
	
	class Meta:
		model = Banco
		fields = '__all__'
		
		widgets = {
			'estatus_banco': 
				forms.Select(attrs={**formclassselect}), 
			'cuenta_banco': 
				forms.NumberInput(attrs={**formclasstext, 'min': 0}),
			'nombre_banco': 
				forms.TextInput(attrs={**formclasstext}),
			'numero_cuenta': 
				forms.TextInput(attrs={**formclasstext}),
			'cbu': 
				forms.TextInput(attrs={**formclasstext}),
			'cod_bco': 
				forms.NumberInput(attrs={**formclasstext, 'min': 0}),
			'sucursal': 
				forms.NumberInput(attrs={**formclasstext, 'min': 0}),
			'codigo_postal': 
				forms.NumberInput(attrs={**formclasstext, 'min': 0}),
			'imputacion': 
				forms.NumberInput(attrs={**formclasstext, 'min': 0}),
			'cuit': 
				forms.TextInput(attrs={**formclasstext}),
			'tope': 
				forms.NumberInput(attrs={**formclasstext, 
							 	  'min': 0, 'max': 9999999999.99}),
			'reporte': 
				forms.TextInput(attrs={**formclasstext}),
			'id_proveedor': 
				forms.Select(attrs={**formclassselect}),
			'id_moneda': 
				forms.Select(attrs={**formclassselect}),
		}
