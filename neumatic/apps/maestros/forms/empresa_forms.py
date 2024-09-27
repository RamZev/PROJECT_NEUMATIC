# neumatic\apps\maestros\forms\empresa_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.empresa_models import Empresa
from diseno_base.diseno_bootstrap import(
    formclasstext, formclassselect, formclassdate)


class EmpresaForm(CrudGenericForm):
    
    class Meta:
        model = Empresa
        fields ='__all__'

        widgets = {
            'estatus_empresa':
                forms.Select(attrs={**formclassselect}),
            'nombre_fiscal':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Nombre Fiscal'}),
            'nombre_comercial':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Nombre Comercial'}),
            'domicilio_empresa':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Domicilio Empresa'}),                           
            'codigo_postal':
                forms.NumberInput(attrs={**formclasstext}),
            'id_localidad':
                forms.Select(attrs={**formclassselect}),
            'id_provincia':
                forms.Select(attrs={**formclassselect}),
            'iva':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'IVA'}),
            'cuit':
                forms.NumberInput(attrs={**formclasstext}),
            'ingresos_bruto':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Ingresos Bruto'}),
            'inicio_actividad': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),
            'cbu':
                forms.NumberInput(attrs={**formclasstext}),                  
            'cbu_alias':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Cbu Alias'}),
            'cbu_vence': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),                             
            'telefono':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Teléfono'}),                            
            'email_empresa':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Email Empresa'}),
            'web_empresa':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Web Empresa'}),                                                        
            'logo_empresa':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': 'Logo Empresa'}),
            'ws_archivo_crt':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': ' Ws Archivo Crt'}),
            'ws_archivo_key':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': ' Ws Archivo Key'}),                                                                                     
            'ws_token':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': ' Ws Token'}),                              
            'ws_sign':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': ' Ws Sign'}),
            'ws_expiracion': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),
            'ws_modo':
                forms.TextInput(attrs={**formclasstext,
                                        'placeholder': ' Ws Modo'}),
            'ws_vence': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date' }),                                                         
        }