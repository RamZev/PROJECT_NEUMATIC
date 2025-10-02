from django import forms
from django.forms import inlineformset_factory
from datetime import date

from ..models.compra_models import Compra, DetalleCompra
from ...maestros.models.base_models import ComprobanteCompra, ProductoDeposito
from diseno_base.diseno_bootstrap import (
    formclasstext,
    formclassnumb,
    formclassselect,
    formclassdate,
    formclasscheck
)


class CompraForm(forms.ModelForm):
    buscar_proveedor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            **formclasstext,
            'id': 'buscar_proveedor',
            'readonly': 'readonly'
        })
    )

    nombre_sucursal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )

    punto_venta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )

    proveedor_nombre = forms.CharField(
        required=False,
        label="Nombre Proveedor",
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )

    condicion_compra_display = forms.CharField(
        required=False,
        label="Condición",
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )

    class Meta:
        model = Compra
        fields = "__all__"
        widgets = {
            # Campos ocultos
            "id_compra": forms.HiddenInput(),
            "estatus_comprabante": forms.Select(attrs={**formclassselect}),

            # Relaciones
            "id_sucursal": forms.HiddenInput(),
            "id_punto_venta": forms.HiddenInput(),
            "id_deposito": forms.Select(attrs={**formclassselect}),
            "id_comprobante_compra": forms.Select(attrs={**formclassselect}),
            "compro": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "letra_comprobante": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "numero_comprobante": forms.TextInput(attrs={
                **formclasstext,
                'readonly': 'readonly',
                'type': 'number',
                'autocomplete': "off",
                'required': 'required',
                'step': 'any'
            }),
            'id_proveedor': 
				forms.Select(attrs={**formclassselect}),

            # Fechas
            "fecha_comprobante": forms.TextInput(attrs={
                **formclassdate,
                'type': 'date',
                'readonly': 'readonly'
            }),
            "fecha_registro": forms.TextInput(attrs={
                **formclassdate,
                'type': 'date',
                'readonly': 'readonly'
            }),
            "fecha_vencimiento": forms.TextInput(attrs={
                **formclassdate,
                'type': 'date'
            }),

            # Proveedor y provincia
            "id_provincia": forms.Select(attrs={**formclassselect}),

            # Condición
            "condicion_comprobante": forms.Select(attrs={**formclassselect}),

            # Montos — todos de solo lectura (calculados)
            "gravado": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "no_gravado": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "no_inscripto": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "exento": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "retencion_iva": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "retencion_ganancia": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "retencion_ingreso_bruto": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "sellado": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "percepcion_iva": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "percepcion_ingreso_bruto": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "iva": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "total": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "entrega": forms.TextInput(attrs={**formclassnumb}),

            # Otros
            "documento_asociado": forms.Select(attrs={**formclassselect}),
            "alicuota_iva": forms.TextInput(attrs={**formclassnumb, 'readonly': 'readonly'}),
            "observa_comprobante": forms.Textarea(attrs={
                **formclasstext,
                'rows': 3,
                'cols': 40,
                'class': 'form-control',
                'style': 'resize: vertical;'
            }),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        # Asignar valores iniciales según usuario
        if usuario:
            self.fields['nombre_sucursal'].initial = usuario.id_sucursal
            self.fields['punto_venta'].initial = usuario.id_punto_venta

            # Filtrar depósitos por sucursal del usuario
            if usuario.id_sucursal:
                self.fields['id_deposito'].queryset = ProductoDeposito.objects.filter(
                    id_sucursal=usuario.id_sucursal
                )
            else:
                self.fields['id_deposito'].queryset = ProductoDeposito.objects.none()

        # Fecha actual por defecto si es nuevo
        if not self.instance.pk and not self.initial.get("fecha_comprobante"):
            self.initial["fecha_comprobante"] = date.today().isoformat()
            self.initial["fecha_registro"] = date.today().isoformat()

        # Si estamos editando, cargar datos del proveedor
        # if self.instance and self.instance.id_proveedor:
        #     self.fields['proveedor_nombre'].initial = self.instance.id_proveedor.nombre_proveedor
        #     self.fields['condicion_compra_display'].initial = dict(CONDICION_VENTA).get(
        #         self.instance.condicion_comprobante, "No definido"
        #     )

        # Filtrar comprobantes de compra (ajusta según tu lógica real)
        self.fields['id_comprobante_compra'].queryset = ComprobanteCompra.objects.filter(
            estatus_comprobante_compra=True
        ).order_by('nombre_comprobante_compra')


class DetalleCompraForm(forms.ModelForm):
    medida = forms.CharField(
        label="Medida",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control form-control-sm border border-primary',
            'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
        })
    )

    class Meta:
        model = DetalleCompra
        fields = "__all__"
        widgets = {
            'id_detalle_compra': forms.HiddenInput(),
            'id_compra': forms.HiddenInput(),
            'id_producto': forms.HiddenInput(),

            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end',
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end',
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
            }),
            'total': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control form-control-sm border border-primary text-end',
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
            }),
            'stock': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control form-control-sm border border-secondary text-end',
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
            }),
            'despacho': forms.TextInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id_producto:
            self.fields['medida'].initial = self.instance.id_producto.medida


# Formsets — listos para usar en vistas
DetalleCompraFormSet = inlineformset_factory(Compra,  DetalleCompra, form=DetalleCompraForm, extra=0)
formset_detalle = DetalleCompraFormSet(queryset=DetalleCompra.objects.none())