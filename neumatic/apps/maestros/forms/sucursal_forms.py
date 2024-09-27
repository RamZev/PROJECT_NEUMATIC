# neumatic\apps\maestros\forms\sucursal_forms.py
from django import forms
from ..models.sucursal_models import Sucursal
from diseno_base.diseno_bootstrap import(
    formclasstext, formclassselect, formclassdate)

class SucursalForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- Agregar clases CSS a los campos con errores.
        for field in self.fields:
            if self[field].errors:
                self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
        
    class Meta:
        model = Sucursal
        fields = '__all__'

        widgets = {
            'estatus_sucursal': 
				forms.Select(attrs={**formclassselect}), 
			'nombre_sucursal': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Nombre Sucursal'}),
			'domicilio_sucursal': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Domicilio Sucursal'}),
			'id_localidad':
                forms.Select(attrs={**formclassselect}),
            'id_provincia':
                forms.Select(attrs={**formclassselect}),
            'telefono_sucursal': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Teléfono Sucursal'}),
            'email_sucursal': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Email Sucursal'}),
            'inicio_actividad': 
				forms.TextInput(attrs={**formclassdate,
										'type': 'date'}),
            'codigo_michelin': 
				forms.TextInput(attrs={**formclasstext,
										'placeholder': 'Código Michelin'}),
        }

