# neumatic\apps\informes\forms\buscador_chequerecibo_forms.py
from django import forms

from .informes_generics_forms import InformesGenericForm
from apps.ventas.models.caja_models import Caja
from diseno_base.diseno_bootstrap import (formclasstext)


class BuscadorChequeReciboForm(InformesGenericForm):
	
	caja = forms.IntegerField(
		min_value=0,
		required=False, 
		label="Número de Caja",
		widget=forms.NumberInput(attrs={**formclasstext})
	)
	
	def clean(self):
		cleaned_data = super().clean()
		
		caja = cleaned_data.get('caja') or 0
		
		#-- Validaciones.
		if caja and caja < 1:
			self.add_error("caja", "Debe indicar un Número de Caja")
		
		if caja:
			existe_caja = Caja.objects.filter(
				numero_caja=caja
			).exists()
			if not existe_caja:
				self.add_error("caja", "El Número de Caja indicado no existe")
		
		return cleaned_data