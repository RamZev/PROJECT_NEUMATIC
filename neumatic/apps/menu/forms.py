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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Función para mostrar la ruta jerárquica completa
        def get_hierarchical_label(obj):
            if obj.heading and not obj.parent:
                # Item de nivel 2
                return f"{obj.heading.name} → {obj.name}"
            elif obj.parent:
                # Item de nivel 3 o 4
                path = obj.name
                current = obj
                while current.parent:
                    path = f"{current.parent.name} → {path}"
                    current = current.parent
                    if current.heading:
                        path = f"{current.heading.name} → {path}"
                        break
                return path
            else:
                # Item sin heading ni parent (raro caso)
                return obj.name
        
        self.fields['parent'].label_from_instance = get_hierarchical_label
        
        # Filtrar items padres para evitar referencias circulares
        if self.instance.pk:
            self.fields['parent'].queryset = MenuItem.objects.exclude(
                pk=self.instance.pk
            ).filter(parent__isnull=True)
        else:
            self.fields['parent'].queryset = MenuItem.objects.filter(parent__isnull=True)