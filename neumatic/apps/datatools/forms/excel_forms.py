# apps\datatools\forms\excel_forms.py
from django import forms
from .forms_generics import GenericForm

class ExcelUploadForm(GenericForm):
	archivo_excel = forms.FileField(
		label="Seleccione el archivo Excel",
		help_text="El archivo debe tener las mismas columnas que el exportado previamente",
		widget=forms.FileInput(attrs={'accept': '.xlsx, .xls'}),
		error_messages = {
			'required': 'Debe seleccionar un archivo Excel.',
			'invalid': 'El archivo seleccionado no es válido.',
		}
	)
	
class CamposActualizacionForm(forms.Form):
	def __init__(self, *args, **kwargs):
		columnas = kwargs.pop('columnas', [])
		super().__init__(*args, **kwargs)
		
		#-- Crear un campo checkbox para cada columna.
		for columna in columnas:
			self.fields[f'actualizar_{columna}'] = forms.BooleanField(
				required=False,
				initial=False,
				label=columna,
				widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
			)