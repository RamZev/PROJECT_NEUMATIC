from django import forms
from ..models.base_models import ComprobanteCompra
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate)


# Este es un comentario por Leoncio.
class ActividadForm(forms.ModelForm):
    
    class Meta:
        model = ComprobanteCompra
        fields = '__all__'

        widgets = {}