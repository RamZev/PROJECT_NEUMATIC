# neumatic\apps\maestros\forms\producto_estado_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import ProductoEstado
from diseno_base.diseno_bootstrap import formclasstext


class ProductoEstadoForm(CrudGenericForm):
	
	class Meta:
		model = ProductoEstado
		fields = '__all__'
		
		widgets = {
			'estado_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_producto_estado': 
				forms.TextInput(attrs={**formclasstext}),
		}
