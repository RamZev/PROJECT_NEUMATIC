from django import forms
from django.core.exceptions import ValidationError

from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdatetime)

from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from ..models.caja_models import CajaDetalle

class CajaDetalleForm(CrudGenericForm):

    class Meta:
        model = CajaDetalle
        fields = '__all__'

        widgets = {
            'id_caja': forms.HiddenInput(),  # Se mantiene oculto, relación real
            'caja': forms.NumberInput(attrs={
                **formclasstext,
                'readonly': 'readonly',
                'placeholder': 'Código de caja'
            }),
            'idventas': forms.NumberInput(attrs={
                **formclasstext,
                'placeholder': 'ID Venta (opcional)'
            }),
            'idcompras': forms.NumberInput(attrs={
                **formclasstext,
                'placeholder': 'ID Compra (opcional)'
            }),
            'idbancos': forms.NumberInput(attrs={
                **formclasstext,
                'placeholder': 'ID Banco (opcional)'
            }),
            'id_forma_pago': forms.Select(attrs={**formclassselect}),
            'importe': forms.NumberInput(attrs={
                **formclasstext,
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'observacion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Observaciones del movimiento'
            }),
            'fecha': forms.DateTimeInput(attrs={
                **formclassdatetime,
                'type': 'datetime-local',
                'readonly': 'readonly'  # Normalmente se asigna automáticamente
            }),
        }

        

    