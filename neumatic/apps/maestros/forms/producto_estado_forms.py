# neumatic\apps\maestros\forms\producto_estado_forms.py
from django import forms
from ..models.base_models import ProductoEstado
from diseno_base.diseno_bootstrap import formclasstext


class ProductoEstadoForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Agregar clases CSS a los campos con errores.
		for field in self.fields:
			if self[field].errors:
				self.fields[field].widget.attrs['class'] += ' border-danger is-invalid'
	
	class Meta:
		model = ProductoEstado
		fields = '__all__'
		
		widgets = {
			'estado_producto': 
				forms.TextInput(attrs={**formclasstext}),
			'nombre_producto_estado': 
				forms.TextInput(attrs={**formclasstext}),
		}
