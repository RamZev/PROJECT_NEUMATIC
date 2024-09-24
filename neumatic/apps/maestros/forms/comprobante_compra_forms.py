# neumatic\apps\maestros\forms\comprobante_compra_forms.py
from django import forms
from ..models.base_models import ComprobanteCompra
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate)


# Este es un comentario por Leoncio.
# Esta es otra línea de comentario.
class ActividadForm(forms.ModelForm):
    
    class Meta:
        model = ComprobanteCompra
        fields = '__all__'

        widgets = {}