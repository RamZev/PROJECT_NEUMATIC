# apps\datatools\forms\excel_forms.py
from django import forms
from .forms_generics import GenericForm

class ExcelUploadForm(GenericForm):
    archivo_excel = forms.FileField(
        label="Seleccione el archivo Excel",
        help_text="El archivo debe tener las mismas columnas que el exportado previamente",
        widget=forms.FileInput(attrs={'accept': '.xlsx, .xls'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #-- Aplicar las clases CSS personalizadas,
        if self.errors and 'archivo_excel' in self.errors:
            self.fields['archivo_excel'].widget.attrs['class'] += ' border-danger is-invalid'