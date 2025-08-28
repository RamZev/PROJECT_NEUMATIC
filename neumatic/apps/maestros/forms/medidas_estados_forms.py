# apps\maestros\forms\medidas_estados_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import MedidasEstados
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class MedidasEstadosForm(CrudGenericForm):
	
	class Meta:
		model = MedidasEstados
		# fields = '__all__'
		exclude = ['estatus_medida_estado']
		
		widgets = {
			'estatus_medida_estado': 
				forms.Select(attrs={**formclassselect}),
			'id_cai': 
				forms.Select(attrs={**formclassselect}),
			'id_estado': 
				forms.Select(attrs={**formclassselect}),
			'stock_desde': 
				forms.NumberInput(attrs={**formclasstext}),
			'stock_hasta': 
				forms.NumberInput(attrs={**formclasstext}),
		}
		
		# error_messages = {
		# 	'codigo_comprobante_venta': {
		# 		'unique': 'Este Código de Comprobante de Venta ya existe.',
		# 		# 'required': 'Debe completar este campo.',
		# 		# 'invalid': 'Ingrese un valor válido.'
		# 	},
		# }
