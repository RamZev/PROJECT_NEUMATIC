# neumatic\apps\maestros\forms\operario_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.producto_models import Producto
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck, formclassdate)


class ProductoForm(CrudGenericForm):
	
	class Meta:
		model = Producto
		fields = '__all__'
		
		widgets = {
			'estatus_producto': 
				forms.Select(attrs={**formclassselect}),
			'codigo_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'tipo_producto': 
				forms.Select(attrs={**formclassselect}),
			'id_familia': 
				forms.Select(attrs={**formclassselect}),
			'id_marca': 
				forms.Select(attrs={**formclassselect}),
			'id_modelo': 
				forms.Select(attrs={**formclassselect}),
			'cai': 
				forms.TextInput(attrs={**formclasstext}),
			'medida': 
				forms.TextInput(attrs={**formclasstext}),
			'segmento': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'unidad': 
				forms.TextInput(attrs={**formclasstext}),
			'fecha_fabricacion': 
				forms.TextInput(attrs={**formclasstext}),
			'costo': 
				forms.TextInput(attrs={**formclasstext}),
			'alicuota_iva': 
				forms.TextInput(attrs={**formclasstext}),
			'precio': 
				forms.TextInput(attrs={**formclasstext}),
			'stock': 
				forms.TextInput(attrs={**formclasstext}),
			'minimo': 
				forms.TextInput(attrs={**formclasstext}),
			'descuento': 
				forms.TextInput(attrs={**formclasstext}),
			'despacho_1': 
				forms.TextInput(attrs={**formclasstext}),
			'despacho_2': 
				forms.TextInput(attrs={**formclasstext}),
			'descripcion_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'carrito': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}
