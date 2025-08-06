# neumatic\apps\maestros\forms\moneda_forms.py
from django import forms
from decimal import Decimal
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import Moneda
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck, formclassnumb)


class MonedaForm(CrudGenericForm):
	'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Formatear valor existente
		if self.instance and self.instance.pk:
			self.format_initial_value()
		
		# Asegurar que el widget muestre el valor formateado
		if 'cotizacion_moneda' in self.initial:
			self.fields['cotizacion_moneda'].widget.attrs['value'] = self.initial['cotizacion_moneda']
	
	def format_initial_value(self):
		"""Formatea el valor de cotización para visualización"""
		cotizacion = getattr(self.instance, 'cotizacion_moneda', None)
		if cotizacion is not None:
			try:
				# Convertir a Decimal para manejo preciso
				value = Decimal(str(cotizacion))
				# Formatear con separadores
				formatted_value = "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
				self.initial['cotizacion_moneda'] = formatted_value
			except (ValueError, TypeError, AttributeError) as e:
				print(f"Error formateando valor: {e}")
				self.initial['cotizacion_moneda'] = "0,00"
	'''
	class Meta:
		model = Moneda
		fields = '__all__'
		
		widgets = {
			'estatus_moneda': 
				forms.Select(attrs={**formclassselect}),
			'nombre_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'cotizacion_moneda': 
				forms.TextInput(attrs={**formclassnumb}),
			'simbolo_moneda': 
				forms.TextInput(attrs={**formclasstext}),
			'ws_afip': 
				forms.TextInput(attrs={**formclasstext}),
			'predeterminada': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
