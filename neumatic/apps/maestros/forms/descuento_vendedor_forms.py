# neumatic\apps\maestros\forms\descuento_vendedor_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.descuento_vendedor_models import DescuentoVendedor
from diseno_base.diseno_bootstrap import formclassselect, formclassnumb

	
class DescuentoVendedorForm(CrudGenericForm):
	
	class Meta:
		model = DescuentoVendedor
		fields = '__all__'
		
		widgets = {
			'estatus_descuento_vendedor': 
				forms.Select(attrs={**formclassselect}),
			'id_marca': 
				forms.Select(attrs={**formclassselect}),
			'id_familia': 
				forms.Select(attrs={**formclassselect}),
			'desc1': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc2': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc3': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc4': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc5': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc6': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc7': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc8': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc9': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc10': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc11': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc12': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc13': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc14': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc15': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc16': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc17': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc18': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc19': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc20': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc21': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc22': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc23': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc24': 
				forms.TextInput(attrs={**formclassnumb}),
			'desc25': 
				forms.TextInput(attrs={**formclassnumb}),
		}
		
		error_messages = {
			'descuento': {
				'max_digits': 'El descuento debe estar entre 0.00 y 99.99',
				'max_decimal_places': 'El descuento debe tener máximo 2 decimales',
				'min_value': 'El descuento debe ser mayor o igual a 0.00',
				'max_value': 'El descuento debe ser menor o igual a 99.99',
				'invalid': 'Ingrese un número válido',
			}
		}