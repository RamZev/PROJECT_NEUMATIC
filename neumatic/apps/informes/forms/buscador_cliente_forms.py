# neumatic\apps\informes\forms\buscador_cliente_forms.py
from django import forms
from django.core.exceptions import ValidationError

from .informes_generics_forms import InformesGenericForm
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.base_models import Provincia
from apps.maestros.models.base_models import Localidad
from diseno_base.diseno_bootstrap import (formclasstext, formclassselect)


class BuscadorClienteForm(InformesGenericForm):
	
	ORDEN_CHOICES = [ 
		('nombre_cliente', 'Nombre'),
		('id_cliente', 'Código'), 
	]
	
	orden = forms.ChoiceField(
		choices=ORDEN_CHOICES, 
		label="Ordenar por", 
		required=False,
		widget=forms.Select(attrs={**formclassselect})
	)
	desde = forms.CharField(
		max_length=20,
		required=False, 
		label="Desde", 
		widget=forms.TextInput(attrs={**formclasstext})
	)
	hasta = forms.CharField(
		max_length=20, 
		required=False,
		label="Hasta",
		widget=forms.TextInput(attrs={**formclasstext})
	)
	vendedor = forms.ModelChoiceField(
		queryset=Vendedor.objects.all(), 
		required=False,
		label="Vendedor", 
		widget=forms.Select(attrs={**formclassselect})
	)
	provincia = forms.ModelChoiceField(
		queryset=Provincia.objects.all(), 
		required=False,
		label="Provincia",
		widget=forms.Select(attrs={**formclassselect})
	)
	localidad = forms.ModelChoiceField(
		queryset=Localidad.objects.filter(id_provincia=1), 
		required=False,
		label="Localidad",
		widget=forms.Select(attrs={**formclassselect})
	)
	
	def clean(self):
		"""
		Validaciones generales entre los campos 'desde', 'hasta' y el campo 'orden'.
		"""
		cleaned_data = super().clean()
		
		orden = cleaned_data.get('orden')
		desde = cleaned_data.get('desde')
		hasta = cleaned_data.get('hasta')
		
		if orden == "id_cliente":
			if desde and not desde.isdigit():
				raise ValidationError({"desde": "El campo debe ser un número entero positivo cuando se ordena por código."})
			
			if hasta and not hasta.isdigit():
				raise ValidationError({"hasta": "El campo debe ser un número entero positivo cuando se ordena por código."})
			
			if desde and not desde.isdigit() and int(desde) < 0:
				raise ValidationError({"desde": "El campo 'Desde' debe ser un número entero positivo cuando se ordena por código."})
			
			if hasta and not hasta.isdigit() and int(hasta) < 0:
				raise ValidationError({"hasta": "El campo 'Hasta' debe ser un número entero positivo cuando se ordena por código."})
		
		if desde and hasta and desde > hasta:
			raise ValidationError({"desde": "El campo Desde no puede ser mayor que Hasta."})
		
		return cleaned_data