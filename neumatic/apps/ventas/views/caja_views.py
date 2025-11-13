# neumatic\apps\ventas\views\caja_views.py
from django.urls import reverse_lazy
from apps.maestros.views.cruds_views_generics import *
from ..models.caja_models import Caja
from ..forms.caja_forms import CajaForm


class ConfigViews():
    # Modelo
    model = Caja
    
    # Formulario asociado al modelo
    form_class = CajaForm
    
    # Aplicación asociada al modelo
    app_label = model._meta.app_label
    
    #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
    model_string = model.__name__.lower()  # "caja"
    
    # Permisos
    permission_add = f"{app_label}.add_{model.__name__.lower()}"
    permission_change = f"{app_label}.change_{model.__name__.lower()}"
    permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
    
    # Vistas del CRUD del modelo
    list_view_name = f"{model_string}_list"
    create_view_name = f"{model_string}_create"
    update_view_name = f"{model_string}_update"
    delete_view_name = f"{model_string}_delete"
    
    # Plantilla para crear o actualizar el modelo
    template_form = f"{app_label}/{model_string}_form.html"
    
    # Plantilla para confirmar eliminación de un registro
    template_delete = "base_confirm_delete.html"
    
    # Plantilla de la lista del CRUD
    template_list = f'{app_label}/maestro_list.html'
    
    # Contexto de los datos de la lista
    context_object_name = 'objetos'
    
    # Vista del home del proyecto
    home_view_name = "home"
    
    # Nombre de la url 
    success_url = reverse_lazy(list_view_name)


class DataViewList():
    search_fields = ['numero_caja', 'observacion_caja']
    
    ordering = ['-fecha_caja', '-numero_caja']
    
    paginate_by = 10
      
    table_headers = {
        'numero_caja': (1, 'Número'),
        'fecha_caja': (1, 'Fecha'),
        'id_sucursal': (1, 'Sucursal'),
        'ingresos': (1, 'Ingresos'),
        'egresos': (1, 'Egresos'),
        'saldo': (1, 'Saldo'),
        'diferencia': (1, 'Diferencia'),
        'observacion_caja': (2, 'Observaciones'),
        'caja_cerrada': (1, 'Cerrada'),
        'acciones': (2, 'Acciones'),
    }
    
    table_data = [
        {'field_name': 'numero_caja', 'date_format': None},
        {'field_name': 'fecha_caja', 'date_format': 'd/m/Y'},
        {'field_name': 'id_sucursal', 'date_format': None},
        {'field_name': 'ingresos', 'date_format': None},
        {'field_name': 'egresos', 'date_format': None},
        {'field_name': 'saldo', 'date_format': None},
        {'field_name': 'diferencia', 'date_format': None},
        {'field_name': 'observacion_caja', 'date_format': None},
        {'field_name': 'caja_cerrada', 'date_format': None},
    ]


# CajaListView - Inicio
class CajaListView(MaestroListView):
    model = ConfigViews.model
    template_name = ConfigViews.template_list
    context_object_name = ConfigViews.context_object_name
    
    search_fields = DataViewList.search_fields
    ordering = DataViewList.ordering
    paginate_by = DataViewList.paginate_by
    
    extra_context = {
        "master_title": ConfigViews.model._meta.verbose_name_plural,
        "home_view_name": ConfigViews.home_view_name,
        "list_view_name": ConfigViews.list_view_name,
        "create_view_name": ConfigViews.create_view_name,
        "update_view_name": ConfigViews.update_view_name,
        "delete_view_name": ConfigViews.delete_view_name,
        "table_headers": DataViewList.table_headers,
        "table_data": DataViewList.table_data,
    }


# CajaCreateView - Inicio
class CajaCreateView(MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    
    #-- Indicar el permiso que requiere para ejecutar la acción.
    permission_required = ConfigViews.permission_add

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        
        # Asignar automáticamente la sucursal del usuario
        initial['id_sucursal'] = user.id_sucursal
        
        # Mostrar el nombre de la sucursal inmediatamente
        if user.id_sucursal:
            initial['nombre_sucursal'] = user.id_sucursal.nombre_sucursal
        
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Forzar la inicialización del campo nombre_sucursal
        if not form.initial.get('nombre_sucursal') and user.id_sucursal:
            form.initial['nombre_sucursal'] = user.id_sucursal.nombre_sucursal
        
        # Limitar las opciones de sucursal a solo la del usuario
        if not user.is_superuser:
            form.fields['id_sucursal'].queryset = ConfigViews.model.id_sucursal.field.related_model.objects.filter(
                id_sucursal=user.id_sucursal.id_sucursal
            )
        
        return form


# CajaUpdateView
class CajaUpdateView(MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    
    #-- Indicar el permiso que requiere para ejecutar la acción.
    permission_required = ConfigViews.permission_change


# CajaDeleteView
class CajaDeleteView(MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    
    #-- Indicar el permiso que requiere para ejecutar la acción.
    permission_required = ConfigViews.permission_delete