# neumatic\apps\ventas\forms\factura_forms.py
from django import forms
from django.forms import inlineformset_factory
from datetime import date

from ..models.factura_models import *
from ...maestros.models.base_models import ComprobanteVenta

from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate, formclasscheck)


class FacturaForm(forms.ModelForm):
    buscar_cliente = forms.CharField(required=False, 
                                     widget=forms.TextInput(attrs={**formclasstext, 'id': 'buscar_cliente'}))
    
    nombre_sucursal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )
    punto_venta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )
    
    vendedor_factura = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )
    
    cliente_vip = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )
    
    tipo_venta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'})
    )
    
    discrimina_iva = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'})
    )
    
    class Meta:
        model = Factura
        
        fields = "__all__"
        
        widgets = {
            "id_factura": forms.HiddenInput(),
            
            # "id_sucursal": forms.Select(attrs={**formclassselect}),
            # "id_punto_venta": forms.Select(attrs={**formclassselect}),
            "id_sucursal": forms.HiddenInput(),
            "id_punto_venta": forms.HiddenInput(),
            'jerarquia': forms.HiddenInput(),
            "id_deposito": forms.Select(attrs={**formclassselect}),
            
            "id_comprobante_venta": forms.Select(attrs={**formclassselect}),
            "compro": forms.TextInput(attrs={**formclasstext}),
            "letra_comprobante": forms.TextInput(attrs={**formclasstext}),
            "numero_comprobante": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'step': 'any'}),
            "remito": forms.TextInput(attrs={**formclasstext}),
            "fecha_comprobante": forms.TextInput(attrs={**formclassdate, 'type': 'date'}),
                        
            "cuit": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'step': '1'}),  # Sin decimales
            "condicion_comprobante": forms.Select(attrs={**formclassselect}),
            "no_estadist": forms.CheckboxInput(attrs={**formclasscheck}),
            # "id_vendedor": forms.Select(attrs={**formclassselect}),
            "id_vendedor": forms.HiddenInput(),
            
            "id_cliente": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'readonly': 'readonly'}),
            "cuit": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'readonly': 'readonly'}),
            "nombre_factura": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "domicilio_factura": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "movil_factura": forms.TextInput(attrs={**formclasstext}),
            "email_factura": forms.TextInput(attrs={**formclasstext}),
            "stock_clie": forms.CheckboxInput(attrs={**formclasscheck}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Pasar el usuario desde la vista
        
        super().__init__(*args, **kwargs)
        
        # Asignar valores iniciales para los campos personalizados
        if usuario:
            self.fields['nombre_sucursal'].initial = usuario.id_sucursal
            self.fields['punto_venta'].initial = usuario.id_punto_venta
            
            
        # Filtrar id_deposito según la sucursal del usuario
        if usuario and usuario.id_sucursal:
            self.fields['id_deposito'].queryset = ProductoDeposito.objects.filter(
                id_sucursal=usuario.id_sucursal
            )
        else:
            self.fields['id_deposito'].queryset = ProductoDeposito.objects.none()  # Sin opciones
        
        # Establecer la fecha actual si no se proporciona un valor inicial
        if not self.initial.get("fecha_comprobante"):
            self.initial["fecha_comprobante"] = date.today().isoformat()

       
class DetalleFacturaForm(forms.ModelForm):
    
    class Meta:
        model = DetalleFactura
        
        fields = "__all__"
        
        widgets = {
            'id_detalle_factura': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_producto': forms.HiddenInput(),
            
            'codigo': forms.TextInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
                }),
            
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary', 
                'step': '0.1',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
                }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary', 
                'step': '0.001',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
                }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary', 'step': '0.1',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
                }),
            'iva': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary', 'step': '0.1',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'
                }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary', 'step': '0.1',
                'style': 'font-size: 0.8rem; padding: 0.25rem; margin-left: 0px; margin-right: 0px;'}),
        }

DetalleFacturaFormSet = inlineformset_factory(Factura, DetalleFactura, form=DetalleFacturaForm, extra=0)
formset = DetalleFacturaFormSet(queryset=DetalleFactura.objects.none())
