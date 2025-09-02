# apps\maestros\forms\medidas_estados_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.base_models import MedidasEstados, ProductoEstado, ProductoCai
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class MedidasEstadosForm(CrudGenericForm):
	
	#-- Campo oculto para el estado (siempre será POCAS).
	id_estado = forms.ModelChoiceField(
		queryset=ProductoEstado.objects.filter(nombre_producto_estado="POCAS"),
		widget=forms.HiddenInput(),
		initial=3,  #-- ID del estado "POCAS"
	)
	
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
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#-- Filtrar CAIs que NO están registrados en medidas_estados.
		cais_registrados = MedidasEstados.objects.values_list('id_cai_id', flat=True)
		
		#-- Si estamos en modo edición, excluir el CAI actual.
		if self.instance and self.instance.pk:
			cais_registrados = cais_registrados.exclude(id_cai_id=self.instance.id_cai_id)
		
		#-- Filtrar queryset.
		self.fields['id_cai'].queryset = ProductoCai.objects.exclude(
			id_cai__in=cais_registrados
		)
