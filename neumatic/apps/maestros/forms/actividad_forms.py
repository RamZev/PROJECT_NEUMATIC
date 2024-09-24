# neumatic\apps\maestros\forms\actividad_forms.py
from django import forms
from ..models.base_models import Actividad
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate)


class ActividadForm(forms.ModelForm):
    
    class Meta:
        model = Actividad
        fields = '__all__'

        widgets = {
                
                'estatus_actividad': 
                    forms.Select(attrs={**formclassselect}), 
                'descripcion_actividad': 
                    forms.TextInput(attrs={**formclasstext,
                                           'placeholder': 'Descripción Actividad'}),
                'fecha_registro_actividad': 
                    forms.TextInput(attrs={**formclassdate,
                                           'placeholder': 'Fecha de Registro' }),
            
        }