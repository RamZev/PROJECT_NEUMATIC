# neumatic\apps\maestros\forms\producto_estado_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import ProductoEstado
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class ProductoEstadoForm(CrudGenericForm):
	
	class Meta:
		model = ProductoEstado
		fields = '__all__'
		
		widgets = {
			'estatus_producto_estado':
				forms.Select(attrs={**formclassselect}),
			'estado_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_producto_estado': 
				forms.TextInput(attrs={**formclasstext}),
		}
		
		error_messages = {
			'estado_producto': {
				'unique': 'Ya existe un Estado de Producto con ese Estado.',
				# 'required': 'Debe completar este campo.',
				# 'invalid': 'Ingrese un valor válido.'
			},
		}
