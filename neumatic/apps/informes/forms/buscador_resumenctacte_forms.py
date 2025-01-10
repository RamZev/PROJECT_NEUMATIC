# neumatic\apps\informes\forms\buscador_actividad_forms.py
from django import forms
from datetime import date

from .informes_generics_forms import InformesGenericForm
from diseno_base.diseno_bootstrap import formclassselect, formclassdate, formclasscheck, formclasstext
from apps.maestros.models.cliente_models import Cliente


class BuscadorResumenCtaCteForm(InformesGenericForm):
	
	CONDICION_VENTA = [
		('contado', 'Contado'),
		('cta_cte', 'Cuenta Corriente'),
		('ambos', 'Ambos'),
	]
	
	# FILTRO_CLIENTE = [
	# 	('todos', 'Todos'),
	# 	('seleccionar', 'Seleccionar'),
	# ]
	
	resumen_pendiente = forms.BooleanField(
		label="Resumen de Cuenta Pendiente",
		required=False,
		widget=forms.CheckboxInput(attrs={**formclasscheck})
	)
	condicion_venta = forms.ChoiceField(
		choices=CONDICION_VENTA, 
		label="Condición de Venta", 
		required=False,
		widget=forms.Select(attrs={**formclassselect})
	)
	fecha_desde = forms.DateField(
		required=False, 
		label="Desde Fecha",
		widget=forms.TextInput(attrs={'type':'date', **formclassdate})
	)
	fecha_hasta = forms.DateField(
		required=False, 
		label="Hasta Fecha",
		widget=forms.TextInput(attrs={'type':'date', **formclassdate})
	)
	# filtro_cliente = forms.ChoiceField(
	# 	choices=FILTRO_CLIENTE, 
	# 	label="Clientes a Listar", 
	# 	required=False,
	# 	widget=forms.Select(attrs={**formclassselect})
	# )
	cliente = forms.ModelChoiceField(
		queryset=Cliente.objects.all(), 
		required=False,
		label="Cliente",
		widget=forms.Select(attrs={**formclassselect})
	)
	observaciones = forms.CharField(	
		label="Leyenda",
		required=False,
		widget=forms.Textarea(attrs={'rows':2, **formclasstext})
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		if "fecha_desde" not in self.initial:
			fecha_inicial = date(date.today().year, 1, 1)
			self.fields["fecha_desde"].initial = fecha_inicial
			self.fields["fecha_desde"].widget.attrs["value"] = fecha_inicial
		if "fecha_hasta" not in self.initial:
			fecha_actual = date.today()
			self.fields["fecha_hasta"].initial = fecha_actual
			self.fields["fecha_hasta"].widget.attrs["value"] = fecha_actual