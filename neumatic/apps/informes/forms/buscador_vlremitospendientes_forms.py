# neumatic\apps\informes\forms\buscador_vlremitospendientes_forms.py

from django import forms
from datetime import date

from .informes_generics_forms import InformesGenericForm
from diseno_base.diseno_bootstrap import formclassselect, formclasstext
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.sucursal_models import Sucursal


class BuscadorRemitosPendientesForm(InformesGenericForm):
	
	FILTRAR_POR = [
		('vendedor', 'Vendedor'),
		('clientes', 'Clientes'),
		('sucursal_fac', 'Sucursal Facturación'),
		('sucursal_cli', 'Sucursal del Cliente'),
	]
	
	filtrar_por = forms.ChoiceField(
		choices=FILTRAR_POR, 
		label="Buscar por", 
		required=True,
		initial="vendedor",
		widget=forms.Select(attrs={**formclassselect})
	)
	vendedor = forms.ModelChoiceField(
		queryset=Vendedor.objects.filter(estatus_vendedor=True),
		required=False,
		initial=0,
		label="Vendedor",
		widget=forms.Select(attrs={**formclassselect})
	)
	sucursal = forms.ModelChoiceField(
		queryset=Sucursal.objects.filter(estatus_sucursal=True), 
		required=False,
		label="Sucursal",
		widget=forms.Select(attrs={**formclassselect})
	)
	id_cli_desde = forms.IntegerField(
		min_value=0,
		required=False, 
		label="Id Desde", 
		initial=0,
		widget=forms.NumberInput(attrs={**formclasstext})
	)
	id_cli_hasta = forms.IntegerField(
		min_value=0, 
		required=False,
		label="Id Hasta",
		initial=0,
		widget=forms.NumberInput(attrs={**formclasstext})
	)
	
	def __init__(self, *args, **kwargs):
		#-- Se espera que la vista pase el usuario autenticado con la clave 'user'.
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		
		#-- Si el usuario es vendedor (tiene un id_vendedor asociado).
		if user and getattr(user, 'id_vendedor', None):
			#-- Fijar el campo vendedor al id del vendedor asociado.
			self.fields['vendedor'].initial = user.id_vendedor
			#-- Establecer el filtro por defecto a "vendedor".
			self.fields['filtrar_por'].initial = 'vendedor'
			
			#-- Deshabilitar los campos de filtro que no corresponden.
			self.fields['filtrar_por'].disabled = True
			self.fields['vendedor'].disabled = True
			self.fields['sucursal'].disabled = True
			self.fields['id_cli_desde'].disabled = True
			self.fields['id_cli_hasta'].disabled = True