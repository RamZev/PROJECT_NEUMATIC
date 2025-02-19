# neumatic\apps\informes\forms\buscador_actividad_forms.py
from django import forms
from datetime import date

from .informes_generics_forms import InformesGenericForm
from diseno_base.diseno_bootstrap import formclassselect, formclassdate, formclasscheck, formclasstext
from apps.maestros.models.cliente_models import Cliente


class BuscadorResumenCtaCteForm(InformesGenericForm):
	
	CONDICION_VENTA = [
		(1, 'Contado'),
		(2, 'Cuenta Corriente'),
		(0, 'Ambos'),
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
		queryset=Cliente.objects.filter(estatus_cliente=True), 
		required=True,
		label="Cliente",
		widget=forms.Select(attrs={**formclassselect})
	)
	observaciones = forms.CharField(	
		label="Leyenda",
		required=False,
		widget=forms.Textarea(attrs={'rows':2, **formclasstext})
	)
	
	def __init__(self, *args, **kwargs):
		"""
		Inicializa el formulario con valores predeterminados:
		- `fecha_desde` se establece en el 1 de enero del año actual.
		- `fecha_hasta` se establece en la fecha actual.
		"""
		
		super().__init__(*args, **kwargs)
		
		if "fecha_desde" not in self.initial:
			fecha_inicial = date(date.today().year, 1, 1)
			self.fields["fecha_desde"].initial = fecha_inicial
			self.fields["fecha_desde"].widget.attrs["value"] = fecha_inicial
		if "fecha_hasta" not in self.initial:
			fecha_actual = date.today()
			self.fields["fecha_hasta"].initial = fecha_actual
			self.fields["fecha_hasta"].widget.attrs["value"] = fecha_actual
	
	def clean(self):
		cleaned_data = super().clean()
		
		#-- Verificar si hay datos enviados (para evitar errores al cargar la página).
		#-- Evitar validaciones si el formulario no tiene datos enviados (primera carga).
		#-- Evitar validaciones si el formulario no tiene datos significativos.
		if not self.data.get('condicion_venta') and not self.data.get('cliente') and not self.data.get('fecha_desde') and not self.data.get('fecha_hasta') and not self.data.get('resumen_pendiente'):
			return cleaned_data
		else:
			print("No para bolas")
		
		cliente = cleaned_data.get("cliente")
		fecha_desde = cleaned_data.get("fecha_desde")
		fecha_hasta = cleaned_data.get("fecha_hasta")
		
		#-- Validar que se haya indicado un cliente solo si hay datos enviados.
		if not cliente:
			self.add_error("cliente", "Debe indicar un cliente.")
		
		#-- Validar rango de fechas.
		if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
			self.add_error("fecha_hasta", "La fecha hasta no puede ser anterior a la fecha desde.")
		
		return cleaned_data
	