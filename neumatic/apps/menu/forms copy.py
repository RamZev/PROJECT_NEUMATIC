# neumatic\apps\menu\forms.py
from django import forms
from .models import MenuHeading, MenuItem

class MenuHeadingForm(forms.ModelForm):
    class Meta:
        model = MenuHeading
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre del Encabezado',
            'order': 'Orden de Aparición',
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'heading', 'parent', 'name', 'url_name', 
            'query_params', 'icon', 'is_collapse', 'order', 'groups'
        ]
        widgets = {
            'heading': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre_url'}),
            'query_params': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '?parametro=valor'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-home'}),
            'is_collapse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'heading': 'Encabezado Asociado',
            'parent': 'Item Padre',
            'name': 'Nombre del Item',
            'url_name': 'Nombre de la URL',
            'query_params': 'Parámetros de Query',
            'icon': 'Clase del Icono',
            'is_collapse': '¿Es Colapsable?',
            'order': 'Orden de Aparición',
            'groups': 'Grupos Permitidos',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar items padres para evitar referencias circulares
        if self.instance.pk:
            self.fields['parent'].queryset = MenuItem.objects.exclude(
                pk=self.instance.pk
            ).filter(parent__isnull=True)
        else:
            self.fields['parent'].queryset = MenuItem.objects.filter(parent__isnull=True)