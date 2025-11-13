# neumatic\apps\ventas\forms\caja_forms.py
from django import forms
from ..models.caja_models import Caja
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate, formclassdatetime)

class CajaForm(forms.ModelForm):
    
    # Campo de solo lectura para mostrar el nombre de la sucursal
    nombre_sucursal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm border border-secondary bg-light',
            'readonly': 'readonly',
            'placeholder': 'Sucursal del usuario'
        }),
        label="Sucursal")
    
    class Meta:
        model = Caja
        fields = '__all__'

        widgets = {
            'estatus_caja': 
                forms.Select(attrs={**formclassselect}),
            'numero_caja': 
                forms.NumberInput(attrs={**formclasstext}),
            'fecha_caja': 
                forms.DateInput(attrs={**formclassdate, 'type': 'date'}),
            'saldoanterior': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'ingresos': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'egresos': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'saldo': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'caja_cerrada': 
                forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recuento': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'diferencia': 
                forms.NumberInput(attrs={**formclasstext, 'step': '0.01'}),
            'id_sucursal': forms.HiddenInput(),
            'hora_cierre': 
                forms.DateTimeInput(attrs={**formclassdatetime, 'type': 'datetime-local'}),
            'observacion_caja': 
                forms.TextInput(attrs={**formclasstext}),
            'id_usercierre': 
                forms.Select(attrs={**formclassselect}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es una instancia existente, mostrar el nombre de la sucursal
        if self.instance and self.instance.pk and self.instance.id_sucursal:
            self.fields['nombre_sucursal'].initial = self.instance.id_sucursal.nombre_sucursal