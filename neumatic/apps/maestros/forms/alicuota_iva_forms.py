# neumatic\apps\maestros\forms\punto_venta_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import AlicuotaIva
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class AlicuotaIvaForm(CrudGenericForm):
	
	class Meta:
		model = AlicuotaIva
		fields = '__all__'
		
		widgets = {
			'estatus_alicuota_iva': 
				forms.Select(attrs={**formclassselect}),
			'codigo_alicuota': 
				forms.TextInput(attrs={**formclasstext}),
			'alicuota_iva': 
				forms.NumberInput(attrs={**formclasstext}),
			'descripcion_alicuota_iva': 
				forms.TextInput(attrs={**formclasstext}),
		}
