# neumatic\apps\maestros\forms\operario_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.producto_models import Producto
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class ProductoForm(CrudGenericForm):
	
		
	class Meta:
		model = Producto
		fields = '__all__'
		
		widgets = {
			'estatus_producto': 
				forms.Select(attrs={**formclassselect}),
			'codigo_producto': 
				forms.NumberInput(attrs={**formclasstext,
							'readonly': True}),
			'tipo_producto': 
				forms.Select(attrs={**formclassselect}),
			'id_familia': 
				forms.Select(attrs={**formclassselect}),
			'id_marca': 
				forms.Select(attrs={**formclassselect}),
			'id_modelo': 
				forms.Select(attrs={**formclassselect}),
			'id_cai': 
				forms.Select(attrs={**formclassselect}),
			'medida': 
				forms.TextInput(attrs={**formclasstext}),
			'segmento': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'unidad': 
				forms.NumberInput(attrs={**formclasstext, 
							'min': 0, 'max': 999}),
			'fecha_fabricacion': 
				forms.TextInput(attrs={**formclasstext}),
			'costo': 
				forms.NumberInput(attrs={**formclasstext,
							'min':0.01, 'max': 9999999999999.99}),
			'alicuota_iva': 
				forms.NumberInput(attrs={**formclasstext,
							'min': 0, 'max': 99.99}),
			'precio': 
				forms.NumberInput(attrs={**formclasstext,
							'min':0.01, 'max': 9999999999999.99}),
			'stock': 
				forms.NumberInput(attrs={**formclasstext,
							'readonly': True}),
			'minimo': 
				forms.NumberInput(attrs={**formclasstext,
							'min': 0, 'max': 99999}),
			'descuento': 
				forms.NumberInput(attrs={**formclasstext,
							'min': 0.01, 'max': 99.99}),
			'despacho_1': 
				forms.TextInput(attrs={**formclasstext}),
			'despacho_2': 
				forms.TextInput(attrs={**formclasstext}),
			'descripcion_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'carrito': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
