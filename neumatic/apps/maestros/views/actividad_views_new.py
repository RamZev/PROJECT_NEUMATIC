# neumatic\apps\maestros\views\actividad_views.py
from ..forms.actividad_forms import ActividadForm
from ..models.base_models import Actividad
from .cruds_views_intemediate import (BaseConfigViews, 
                               BaseDataViewList, 
                               BaseListView, 
                               BaseCreateView, BaseUpdateView, 
                               BaseDeleteView)


# Clase de configuración específica para el modelo
class ConfigViews(BaseConfigViews):
    model = Actividad
    form_class = ActividadForm


# Configuración específica para listar el modelo
class DataViewList(BaseDataViewList):
    search_fields = ['descripcion_actividad']
    ordering = ['descripcion_actividad']
    
    # Definición de los encabezados de la tabla
    table_headers = {
        'descripcion_actividad': (2, 'Descripción'),
        'fecha_registro_actividad': (2, 'Fecha Registro'),
        'acciones': (2, 'Acciones'),
    }

    # Definición de los datos a mostrar en la tabla
    table_data = [
        {'field_name': 'descripcion_actividad', 'date_format': None},
        {'field_name': 'fecha_registro_actividad', 'date_format': 'd/m/Y'},
    ]


# Vista para listar los registrs del modelo
class ActividadListView(BaseListView):
    model = Actividad  # Definir el modelo aquí


# Vista para crear un registro del modelo
class ActividadCreateView(BaseCreateView):
    pass


# Vista para actualizar un registro del modelo
class ActividadUpdateView(BaseUpdateView):
    pass


# Vista para eliminar un registro del modelo
class ActividadDeleteView(BaseDeleteView):
    pass
