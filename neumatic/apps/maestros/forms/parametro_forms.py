# neumatic\apps\maestros\forms\parametro_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.parametro_models import Parametro
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect)


class ParametroForm(CrudGenericForm):
	
    class Meta:
        model = Parametro
        fields = '__all__'
		
        widgets = {
            'estatus_parametro':
                forms.Select(attrs={**formclassselect}),
            'id_empresa':
                forms.Select(attrs={**formclassselect}),
            'interes':
                forms.NumberInput(
                    attrs={**formclasstext,
                           'min': 0, 'max': 99, 'step': '0.01'}),
            'interes_dolar':
                forms.NumberInput(
                    attrs={**formclasstext, 
                           'min': 0, 'max': 99, 'step': '0.01'}),
            'cotizacion_dolar':
                forms.NumberInput(
                    attrs={**formclasstext, 
                           'min': 0, 'max': 9999999999999999, 'step': '0.01'}),
            'dias_vencimiento':
                forms.NumberInput(
                    attrs={**formclasstext, 
                           'min': 0, 'max': 99}),
            'descuento_maximo':
                forms.NumberInput(
                    attrs={**formclasstext, 
                           'min': 0, 'max': 99, 'step': '0.01'}),
        }
