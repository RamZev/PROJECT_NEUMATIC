# neumatic\apps\ventas\forms\recibo_forms.py
from django import forms
from django.forms import inlineformset_factory
from datetime import date
from django.db.models import Q

from ..models.factura_models import *
from ..models.recibo_models import (
    DetalleRecibo,
    RetencionRecibo,
    DepositoRecibo,
    TarjetaRecibo,
    ChequeRecibo
)
from ..models.factura_models import Factura

from diseno_base.diseno_bootstrap import (
    formclasstext, 
    formclassnumb,
    formclassselect, 
    formclassdate, 
    formclasscheck
)


# Encabezado de Recibo
class FacturaReciboForm(forms.ModelForm):
    buscar_cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            **formclasstext, 'id': 'buscar_cliente', 
            'readonly': 'readonly'
            }
                               )
        )
    
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
    
    es_remito = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'})
    )
    
    es_pendiente = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'})
    )
    
    es_presupuesto = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'})
    )
        
    
    saldo_pendiente = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            **formclassnumb, 
            'readonly': 'readonly'
        })
    )
    
    total_cobrado = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            **formclassnumb, 
            'readonly': 'readonly'
        })
    )

    class Meta:
        model = Factura
        fields = ['id_factura',
                  'id_valida',
                  'estatus_comprobante',
                  
                  "id_sucursal",
                  "id_punto_venta",
                  "jerarquia",
                  "id_deposito",
                  'id_comprobante_venta',

                  'id_cliente', 
                  'nombre_factura', 
                  'domicilio_factura',
                  'cuit', 

                  'fecha_comprobante',
                  'compro',
                  'letra_comprobante',
                  'numero_comprobante',
                  'comprobante_remito',
                  'remito',

                  'condicion_comprobante',
                  'no_estadist',
                  'id_vendedor',
                  'movil_factura',
                  'email_factura',
                  'stock_clie',

                  'total']
        
        widgets = {
            'id_factura': forms.HiddenInput(),
            "id_valida": forms.HiddenInput(),
            "estatus_comprobante": forms.Select(attrs={**formclassselect}),

            "id_sucursal": forms.HiddenInput(),
            "id_punto_venta": forms.HiddenInput(),
            "jerarquia": forms.HiddenInput(),
            "id_deposito": forms.Select(attrs={**formclassselect}),
            "id_comprobante_venta": forms.Select(attrs={**formclassselect}),

            "id_cliente": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'readonly': 'readonly'}),
            "cuit": forms.TextInput(attrs={**formclasstext, 'type': 'number', 'readonly': 'readonly'}),
            'nombre_factura': forms.TextInput(attrs={
                **formclasstext, 
                'readonly': 'readonly'
            }),
            "domicilio_factura": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),

            "fecha_comprobante": forms.TextInput(attrs={**formclassdate, 'type': 'date'}),
            "compro": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "letra_comprobante": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            "numero_comprobante": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly', 'type': 'number', 'step': 'any'}),
            "comprobante_remito": forms.Select(attrs={**formclassselect}),            
            "remito": forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
            
            "condicion_comprobante": forms.Select(attrs={**formclassselect}),
            "no_estadist": forms.CheckboxInput(attrs={**formclasscheck}),
            "id_vendedor": forms.HiddenInput(),
            "movil_factura": forms.TextInput(attrs={**formclasstext}),
            "stock_clie": forms.CheckboxInput(attrs={**formclasscheck}),
            "email_factura": forms.TextInput(attrs={**formclasstext}),
            

            'total': forms.NumberInput(attrs={
                **formclassnumb, 
                'readonly': 'readonly'
            }),
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
        
        # ← Agregar aquí la lógica para modo edición:
        if self.instance and self.instance.id_cliente and self.instance.id_cliente.id_vendedor:
            self.fields['vendedor_factura'].initial = self.instance.id_cliente.id_vendedor.nombre_vendedor

        if self.instance and self.instance.id_cliente and self.instance.id_cliente.id_vendedor:
            self.fields['vendedor_factura'].initial = self.instance.id_cliente.id_vendedor.nombre_vendedor
            self.fields['tipo_venta'].initial = self.instance.id_cliente.id_vendedor.tipo_venta
        
        # Filtrar los comprobantes electrónicos y de remito
        self.fields['id_comprobante_venta'].queryset = ComprobanteVenta.objects.filter(
            Q(recibo=True)
        )


# Detalle de Recibo
class DetalleReciboForm(forms.ModelForm):
    # Campos no guardados en el modelo
    comprobante = forms.CharField(max_length=100, required=False, disabled=True,
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control form-control-sm border border-primary small-font readonly-select',
                                     'readonly': 'readonly'
                                 }))
    letra_comprobante = forms.CharField(max_length=1, required=False, disabled=True,
                                       widget=forms.TextInput(attrs={
                                           'class': 'form-control form-control-sm border border-primary small-font readonly-select',
                                           'readonly': 'readonly'
                                       }))
    fecha_comprobante = forms.CharField(max_length=10, required=False, disabled=True,
                                       widget=forms.TextInput(attrs={
                                           'class': 'form-control form-control-sm border border-primary small-font readonly-select',
                                           'readonly': 'readonly'
                                       }))
    total = forms.DecimalField(max_digits=12, decimal_places=2, required=False, disabled=True,
                              widget=forms.NumberInput(attrs={
                                  'class': 'form-control form-control-sm border border-primary text-end small-font readonly-select',
                                  'readonly': 'readonly'
                              }))
    entrega = forms.DecimalField(max_digits=12, decimal_places=2, required=False, disabled=True,
                                widget=forms.NumberInput(attrs={
                                    'class': 'form-control form-control-sm border border-primary text-end small-font readonly-select',
                                    'readonly': 'readonly'
                                }))
    saldo = forms.DecimalField(max_digits=12, decimal_places=2, required=False, disabled=True,
                              widget=forms.NumberInput(attrs={
                                  'class': 'form-control form-control-sm border border-primary text-end small-font readonly-select',
                                  'readonly': 'readonly'
                              }))

    class Meta:
        model = DetalleRecibo
        fields = ['id_detalle_recibo', 'id_factura', 'id_factura_cobrada', 'monto_cobrado']
        widgets = {
            'id_detalle_recibo': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_factura_cobrada': forms.HiddenInput(),
            'monto_cobrado': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end', 
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
        }

class RetencionReciboForm(forms.ModelForm):
    class Meta:
        model = RetencionRecibo
        fields = ['id_retencion_recibo', 'id_factura', 'id_codigo_retencion', 
                 'certificado', 'importe_retencion', 'fecha_retencion']
        
        widgets = {
            'id_retencion_recibo': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_codigo_retencion': forms.Select(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'certificado': forms.TextInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'importe_retencion': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end', 
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'fecha_retencion': forms.DateInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'type': 'date',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
        }

class DepositoReciboForm(forms.ModelForm):
    class Meta:
        model = DepositoRecibo
        fields = ['id_deposito_recibo', 'id_factura', 'id_banco', 'id_concepto_banco',
                 'fecha_deposito', 'importe_deposito', 'detalle_deposito']
        
        widgets = {
            'id_deposito_recibo': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_banco': forms.Select(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'id_concepto_banco': forms.Select(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'fecha_deposito': forms.DateInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'type': 'date',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'importe_deposito': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end', 
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'detalle_deposito': forms.TextInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
        }

class TarjetaReciboForm(forms.ModelForm):
    class Meta:
        model = TarjetaRecibo
        fields = ['id_tarjeta_recibo', 'id_factura', 'id_tarjeta', 'cupon',
                 'lote', 'cuotas', 'importe_tarjeta']
        
        widgets = {
            'id_tarjeta_recibo': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_tarjeta': forms.Select(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'cupon': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'lote': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'cuotas': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'importe_tarjeta': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end', 
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
        }

class ChequeReciboForm(forms.ModelForm):
    class Meta:
        model = ChequeRecibo
        fields = ['id_cheque_recibo', 'id_factura', 'id_banco', 'sucursal',
                 'codigo_postal', 'numero_cheque_recibo', 'cuenta_cheque_recibo',
                 'cuit_cheque_recibo', 'fecha_cheque1', 'fecha_cheque2',
                 'importe_cheque_recibo']
        
        widgets = {
            'id_cheque_recibo': forms.HiddenInput(),
            'id_factura': forms.HiddenInput(),
            'id_banco': forms.Select(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'sucursal': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'codigo_postal': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'numero_cheque_recibo': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'cuenta_cheque_recibo': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'cuit_cheque_recibo': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'fecha_cheque1': forms.DateInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'type': 'date',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'fecha_cheque2': forms.DateInput(attrs={
                'class': 'form-control form-control-sm border border-primary',
                'type': 'date',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
            'importe_cheque_recibo': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm border border-primary text-end', 
                'step': '0.01',
                'style': 'font-size: 0.8rem; padding: 0.25rem;'
            }),
        }

# Creamos los formsets para cada tipo de detalle
DetalleReciboFormSet = inlineformset_factory(
    Factura, 
    DetalleRecibo, 
    form=DetalleReciboForm, 
    extra=0,
    fk_name='id_factura'
)
formset_recibo = DetalleReciboFormSet(queryset=DetalleRecibo.objects.none())

RetencionReciboFormSet = inlineformset_factory(
    Factura, 
    RetencionRecibo, 
    form=RetencionReciboForm, 
    extra=0,
)
formset_retencion = RetencionReciboFormSet(queryset=RetencionRecibo.objects.none())

DepositoReciboFormSet = inlineformset_factory(
    Factura, 
    DepositoRecibo, 
    form=DepositoReciboForm, 
    extra=0,
)
formset_deposito = DepositoReciboFormSet(queryset=DepositoRecibo.objects.none())

TarjetaReciboFormSet = inlineformset_factory(
    Factura, 
    TarjetaRecibo, 
    form=TarjetaReciboForm, 
    extra=0,
)
formset_tarjeta = TarjetaReciboFormSet(queryset=TarjetaRecibo.objects.none())

ChequeReciboFormSet = inlineformset_factory(
    Factura, 
    ChequeRecibo, 
    form=ChequeReciboForm, 
    extra=0,
)
formset_cheque = ChequeReciboFormSet(queryset=ChequeRecibo.objects.none())