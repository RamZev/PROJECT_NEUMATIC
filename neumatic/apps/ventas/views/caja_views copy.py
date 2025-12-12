# neumatic\apps\ventas\views\caja_views.py
from django.urls import reverse_lazy
from django import forms
from django.db.models import Max

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
# neumatic\apps\ventas\views\caja_views.py
# CajaCreateView - con cálculo de saldoanterior visible al usuario
class CajaCreateView(MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    
    permission_required = ConfigViews.permission_add

    def get_context_data(self, **kwargs):
        """Agregar contexto adicional a la plantilla"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Información sobre caja anterior
        ultima_caja_cerrada = None
        saldo_anterior_calculado = 0
        
        if user.id_sucursal:
            # Verificar si hay caja abierta
            caja_abierta = Caja.objects.filter(
                id_sucursal=user.id_sucursal,
                caja_cerrada=False
            ).exists()
            context['caja_abierta'] = caja_abierta
            
            # Buscar última caja cerrada para mostrar información
            ultima_caja_cerrada = Caja.objects.filter(
                id_sucursal=user.id_sucursal,
                caja_cerrada=True
            ).order_by('-fecha_caja', '-id_caja').first()
            
            if ultima_caja_cerrada:
                saldo_anterior_calculado = ultima_caja_cerrada.saldo
        
        context['user'] = user
        context['ultima_caja_cerrada'] = ultima_caja_cerrada
        context['saldo_anterior_calculado'] = saldo_anterior_calculado
        
        return context

    def dispatch(self, request, *args, **kwargs):
        """Interceptar la solicitud antes de mostrar el formulario"""
        user = request.user
        
        # TODOS los usuarios deben tener sucursal asignada
        if not user.id_sucursal:
            messages.error(
                request,
                'No tiene una sucursal asignada. Contacte al administrador.'
            )
            return redirect(self.list_view_name)
        
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Valores iniciales para el formulario"""
        initial = super().get_initial()
        user = self.request.user
        
        if user.id_sucursal:
            initial['id_sucursal'] = user.id_sucursal
            initial['nombre_sucursal'] = user.id_sucursal.nombre_sucursal
            
            # Calcular saldoanterior basado en última caja cerrada
            ultima_caja_cerrada = Caja.objects.filter(
                id_sucursal=user.id_sucursal,
                caja_cerrada=True
            ).order_by('-fecha_caja', '-id_caja').first()
            
            if ultima_caja_cerrada:
                initial['saldoanterior'] = ultima_caja_cerrada.saldo
            else:
                initial['saldoanterior'] = 0
        
        # Establecer fecha actual por defecto
        fecha_actual = timezone.now().date()
        initial['fecha_caja'] = fecha_actual.strftime('%Y-%m-%d')
        
        # Para nuevas cajas, caja_cerrada debe ser False
        initial['caja_cerrada'] = False
        
        return initial
    
    def get_form(self, form_class=None):
        """Configurar el formulario"""
        form = super().get_form(form_class)
        user = self.request.user
        
        # Solo necesitamos limitar el queryset de id_sucursal
        if user.id_sucursal:
            form.fields['id_sucursal'].queryset = Caja._meta.get_field('id_sucursal').related_model.objects.filter(
                id_sucursal=user.id_sucursal.id_sucursal
            )
        
        return form
    
    def generar_numero_caja(self, sucursal):
        """
        GENERAR EL NÚMERO DE CAJA EN LA VISTA
        Lógica completa de generación
        """
        if not sucursal:
            raise forms.ValidationError('Debe proporcionar una sucursal para generar el número de caja')
        
        sucursal_id = sucursal.id_sucursal
        
        # Validar que id_sucursal tenga máximo 2 dígitos
        if sucursal_id > 99:
            raise forms.ValidationError('El ID de sucursal debe ser de máximo 2 dígitos')
        
        # Formatear id_sucursal a 2 dígitos
        sucursal_str = f"{sucursal_id:02d}"
        
        # Buscar el último numero_caja para esta sucursal
        rango_min = sucursal_id * 1000000
        rango_max = (sucursal_id + 1) * 1000000 - 1
        
        ultimo = Caja.objects.filter(
            numero_caja__gte=rango_min,
            numero_caja__lte=rango_max
        ).aggregate(Max('numero_caja'))
        
        if ultimo['numero_caja__max']:
            # Extraer correlativo actual
            correlativo_actual = ultimo['numero_caja__max'] % 1000000
            nuevo_correlativo = correlativo_actual + 1
        else:
            # Primera caja de esta sucursal
            nuevo_correlativo = 1
        
        # Formatear correlativo a 6 dígitos y combinar
        correlativo_str = f"{nuevo_correlativo:06d}"
        return int(f"{sucursal_str}{correlativo_str}")
    
    @transaction.atomic
    def form_valid(self, form):
        """
        CONTROL COMPLETO DE LA GRABACIÓN EN LA VISTA
        """
        user = self.request.user
        
        # 1. Validar que el usuario tenga sucursal
        sucursal = user.id_sucursal
        if not sucursal:
            form.add_error(None, 'No tiene una sucursal asignada')
            return self.form_invalid(form)
        
        # 2. Validar que no haya caja abierta en la sucursal
        caja_abierta = Caja.objects.filter(
            id_sucursal=sucursal,
            caja_cerrada=False
        ).select_for_update().exists()  # Bloquear para evitar concurrencia
        
        if caja_abierta:
            form.add_error(
                None,
                f'Existe una caja abierta en la sucursal {sucursal.nombre_sucursal}. '
                f'Debe cerrarla antes de crear una nueva.'
            )
            return self.form_invalid(form)
        
        # 3. FORZAR valores críticos
        form.instance.id_sucursal = sucursal
        form.instance.caja_cerrada = False  # Nueva caja siempre abierta
        
        # 4. GENERAR NÚMERO DE CAJA
        try:
            numero_generado = self.generar_numero_caja(sucursal)
            form.instance.numero_caja = numero_generado
        except forms.ValidationError as e:
            form.add_error('numero_caja', str(e))
            return self.form_invalid(form)
        
        # 5. CALCULAR SALDO ANTERIOR
        ultima_caja_cerrada = Caja.objects.filter(
            id_sucursal=sucursal,
            caja_cerrada=True
        ).order_by('-fecha_caja', '-id_caja').first()
        
        if ultima_caja_cerrada:
            form.instance.saldoanterior = ultima_caja_cerrada.saldo
        else:
            form.instance.saldoanterior = 0
        
        # 6. INICIALIZAR OTROS CAMPOS
        form.instance.ingresos = 0
        form.instance.egresos = 0
        form.instance.saldo = form.instance.saldoanterior
        form.instance.diferencia = 0
        form.instance.recuento = 0
        
        # 7. VALIDAR FECHA (no puede ser futura)
        fecha_caja = form.cleaned_data.get('fecha_caja')
        if fecha_caja and fecha_caja > timezone.now().date():
            form.add_error('fecha_caja', 'La fecha de la caja no puede ser futura')
            return self.form_invalid(form)
        
        # 8. GUARDAR
        try:
            # Llamar al padre para guardar
            response = super().form_valid(form)
            
            # Mensaje de éxito
            messages.success(
                self.request,
                f'Caja #{form.instance.numero_caja} creada exitosamente. '
                f'Saldo inicial: ${form.instance.saldoanterior:.2f}'
            )
            
            return response
            
        except Exception as e:
            # Manejar cualquier error durante el guardado
            form.add_error(None, f'Error al guardar la caja: {str(e)}')
            return self.form_invalid(form)


# Para CajaUpdateView (edición)
class CajaUpdateView(MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    
    permission_required = ConfigViews.permission_change
    
    def dispatch(self, request, *args, **kwargs):
        """Validar antes de mostrar el formulario"""
        # Primero obtener el objeto
        self.object = self.get_object()
        
        # Si la caja está cerrada, redirigir con mensaje de error
        if self.object.caja_cerrada:
            messages.error(
                request,
                f'No se puede modificar la caja #{self.object.numero_caja} porque está cerrada.'
            )
            return redirect(self.list_view_name)
        
        return super().dispatch(request, *args, **kwargs)
    
    @transaction.atomic
    def form_valid(self, form):
        """
        Control de grabación para edición - CIERRE DE CAJA
        """
        caja = self.get_object()
        
        # Validar que no se pueda editar una caja cerrada
        if caja.caja_cerrada:
            form.add_error(None, 'No se puede modificar una caja cerrada')
            return self.form_invalid(form)
        
        # Validaciones básicas
        if form.cleaned_data.get('numero_caja') != caja.numero_caja:
            form.add_error('numero_caja', 'No se puede modificar el número de caja')
            return self.form_invalid(form)
        
        if form.cleaned_data.get('id_sucursal') != caja.id_sucursal:
            form.add_error('id_sucursal', 'No se puede cambiar la sucursal de la caja')
            return self.form_invalid(form)
        
        # ========== PROCESO DE CIERRE DE CAJA ==========
        # Si el usuario está intentando CERRAR la caja
        if not caja.caja_cerrada and form.cleaned_data.get('caja_cerrada'):
            print(f"DEBUG: Cerrando caja #{caja.numero_caja}")
            
            # 1. Validar que se haya hecho recuento
            recuento = form.cleaned_data.get('recuento') or 0
            if recuento == 0:
                form.add_error('recuento', 'Debe realizar el recuento físico antes de cerrar la caja. Use el botón 🧮 para contar el efectivo.')
                return self.form_invalid(form)
            
            # 2. Asignar usuario actual automáticamente
            form.instance.id_usercierre = self.request.user
            print(f"DEBUG: Usuario de cierre asignado: {self.request.user}")
            
            # 3. Registrar fecha y hora actual automáticamente
            form.instance.hora_cierre = timezone.now()
            print(f"DEBUG: Hora de cierre asignada: {form.instance.hora_cierre}")
            
            # 4. Calcular diferencia automáticamente
            form.instance.diferencia = recuento - form.instance.saldo
            print(f"DEBUG: Diferencia calculada: {form.instance.diferencia}")
            
            # 5. Mensaje de éxito
            messages.success(
                self.request, 
                f'Caja #{caja.numero_caja} cerrada exitosamente. '
                f'Diferencia: ${form.instance.diferencia:.2f}'
            )
        
        # Si el usuario está intentando ABRIR una caja cerrada (no permitido)
        elif caja.caja_cerrada and not form.cleaned_data.get('caja_cerrada'):
            form.add_error('caja_cerrada', 'No se puede reabrir una caja cerrada')
            return self.form_invalid(form)
        
        # 6. GUARDAR LOS CAMBIOS
        try:
            response = super().form_valid(form)
            return response
        except Exception as e:
            form.add_error(None, f'Error al guardar los cambios: {str(e)}')
            return self.form_invalid(form)

# CajaDeleteView
class CajaDeleteView(MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    
    #-- Indicar el permiso que requiere para ejecutar la acción.
    permission_required = ConfigViews.permission_delete