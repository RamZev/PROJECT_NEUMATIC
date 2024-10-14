# neumatic\apps\maestros\forms\tipo_retencion_ib_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import TipoRetencionIb
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class TipoRetencionIbForm(CrudGenericForm):
	
	class Meta:
		model = TipoRetencionIb
		fields = '__all__'
		
		widgets = {
			'estatus_tipo_retencion_ib': 
				forms.Select(attrs={**formclassselect}),
			'descripcion_tipo_retencion_ib': 
				forms.TextInput(attrs={**formclasstext}),
			'alicuota_inscripto': 
				forms.NumberInput(attrs={**formclasstext,
										'min': 1,
										'max': 99.99}),
			'alicuota_no_inscripto': 
				forms.NumberInput(attrs={**formclasstext,
										'min': 1,
										'max': 99.99}),
			'monto': 
				forms.NumberInput(attrs={**formclasstext,
										'min': 1,
										'max': 9999999999999.99}),
			'minimo': 
				forms.NumberInput(attrs={**formclasstext,
										'min': 1,
										'max': 9999999999999.99}),
		}
