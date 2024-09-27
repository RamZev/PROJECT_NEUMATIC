# D:\PROJECT_NEUMATIC\neumatic\apps\maestros\models\vendedor_models.py
from django import forms
from ..models.vendedor_models import Vendedor
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate)


class VendedorForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = Vendedor
		fields = '__all__'

		widgets = {
			'estatus_vendedor': 
				forms.Select(attrs={**formclassselect}), 
			'nombre_vendedor': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Nombre Vendedor'}),
			'domicilio_vendedor': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Domicilio Vendedor'}),
			'email_vendedor': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Email Vendedor'}),
			'telefono_vendedor': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Teléfono'}),
			'pje_auto': 
				forms.NumberInput(attrs={**formclasstext}),
			'pje_camion': 
				forms.NumberInput(attrs={**formclasstext}),			
			'vence_factura': 
				forms.NumberInput(attrs={**formclasstext}),	
			'vence_remito': 
				forms.NumberInput(attrs={**formclasstext}),	
			'id_sucursal': 
				forms.Select(attrs={**formclassselect,
										'placeholder': 'Sucursal'}),
			'tipo_venta': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Tipo Venta'}),
			'col_descuento': 
				forms.NumberInput(attrs={**formclasstext}),
			'email_venta': 
				forms.Select(attrs={**formclassselect,
										'placeholder': 'Tipo Venta'}),
			'info_saldo': 
				forms.Select(attrs={**formclassselect,
										'placeholder': 'Info. Saldo'}),
			'info_estadistica':
				forms.Select(attrs={**formclassselect,
										'placeholder': 'Info. Estadística'})															
		}
