# neumatic\apps\menu\views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect

from .models import MenuHeading, MenuItem
from .forms import MenuHeadingForm, MenuItemForm

class MenuHeadingListView(LoginRequiredMixin, ListView):
    model = MenuHeading
    template_name = 'menu/menuheading_list.html'
    context_object_name = 'headings'
    paginate_by = 20

class MenuHeadingCreateView(LoginRequiredMixin, CreateView):
    model = MenuHeading
    form_class = MenuHeadingForm
    template_name = 'menu/menuheading_form.html'
    success_url = reverse_lazy('menu:heading_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Encabezado de Menú'
        return context

class MenuHeadingUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuHeading
    form_class = MenuHeadingForm
    template_name = 'menu/menuheading_form.html'
    success_url = reverse_lazy('menu:heading_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Encabezado de Menú'
        return context

class MenuHeadingDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuHeading
    template_name = 'menu/menuheading_confirm_delete.html'
    success_url = reverse_lazy('menu:heading_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información sobre items asociados
        context['has_items'] = self.object.menuitem_set.exists()
        context['item_count'] = self.object.menuitem_set.count()
        return context
    
    def form_valid(self, form):
        # Validar si tiene items asociados
        if self.object.menuitem_set.exists():
            # No eliminar, redirigir con mensaje de error
            from django.contrib import messages
            messages.error(self.request, f'No se puede eliminar el encabezado "{self.object.name}" porque tiene {self.object.menuitem_set.count()} item(s) asociado(s). Elimine primero los items.')
            return redirect('menu:heading_list')
        
        # Proceder con eliminación si no tiene items
        return super().form_valid(form)


class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'menu/menuitem_list.html'
    context_object_name = 'items'
    paginate_by = None  # Show all items without pagination
    
    def get_queryset(self):
        # return MenuItem.objects.select_related('heading', 'parent').prefetch_related('groups')
        
        # return MenuItem.objects.select_related('heading', 'parent').prefetch_related('groups').order_by(
        #     'heading__order',        # Primero por heading (Archivos, Ventas, etc.)
        #     'heading__name',         # Luego por nombre del heading
        #     'parent__order',         # Luego por orden del padre
        #     'parent__name',          # Luego por nombre del padre  
        #     'order',                 # Luego por orden del item
        #     'name'                   # Finalmente por nombre del item
        # )
        
        # return MenuItem.objects.select_related('heading', 'parent').prefetch_related('groups').order_by(
        #     'heading__order',
        #     'parent__order',         # Orden del padre
        #     'parent__name',          # Nombre del padre para desempatar
        #     'order',
        #     'name'
        # )

        # Obtener todos los items organizados por heading y parent
        headings = MenuHeading.objects.order_by('order')
        items_by_heading = {}
        
        # Organizar items por heading
        for heading in headings:
            # Items de nivel 1 (sin parent) de este heading, ordenados por order
            level1_items = MenuItem.objects.filter(
                heading=heading, 
                parent=None
            ).order_by('order')
            
            items_list = []
            for item in level1_items:
                # Agregar el item de nivel 1
                items_list.append(item)
                
                # Agregar sus hijos (nivel 2) ordenados por order
                level2_items = item.children.all().order_by('order')
                for child in level2_items:
                    items_list.append(child)
                    
                    # Agregar sus nietos (nivel 3) ordenados por order
                    level3_items = child.children.all().order_by('order')
                    for grandchild in level3_items:
                        items_list.append(grandchild)
            
            items_by_heading[heading] = items_list
        
        # Aplanar la lista en el orden correcto
        sorted_items = []
        for heading in headings:
            sorted_items.extend(items_by_heading.get(heading, []))
        
        return sorted_items
        
class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu/menuitem_form.html'
    success_url = reverse_lazy('menu:item_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Item de Menú'
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Obtener el orden deseado
            desired_order = form.cleaned_data.get('order', 0)
            
            # Reordenar los items existentes
            MenuItem.objects.filter(
                heading=form.cleaned_data['heading'],
                parent=form.cleaned_data.get('parent')
            ).filter(order__gte=desired_order).update(order=F('order') + 1)
            
            # Guardar el nuevo item
            return super().form_valid(form)

class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu/menuitem_form.html'
    success_url = reverse_lazy('menu:item_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Item de Menú'
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            old_order = self.object.order
            new_order = form.cleaned_data.get('order', 0)
            old_heading = self.object.heading
            old_parent = self.object.parent
            new_heading = form.cleaned_data['heading']
            new_parent = form.cleaned_data.get('parent')
            
            # Si cambió el heading o parent, tratamos como nuevo item
            if old_heading != new_heading or old_parent != new_parent:
                # Remover del grupo antiguo
                MenuItem.objects.filter(
                    heading=old_heading,
                    parent=old_parent
                ).filter(order__gt=old_order).update(order=F('order') - 1)
                
                # Insertar en el nuevo grupo
                MenuItem.objects.filter(
                    heading=new_heading,
                    parent=new_parent
                ).filter(order__gte=new_order).update(order=F('order') + 1)
            else:
                # Mismo grupo, solo reordenar
                if new_order > old_order:
                    MenuItem.objects.filter(
                        heading=new_heading,
                        parent=new_parent
                    ).filter(order__gt=old_order, order__lte=new_order).update(order=F('order') - 1)
                elif new_order < old_order:
                    MenuItem.objects.filter(
                        heading=new_heading,
                        parent=new_parent
                    ).filter(order__lt=old_order, order__gte=new_order).update(order=F('order') + 1)
            
            return super().form_valid(form)


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'menu/menuitem_confirm_delete.html'
    success_url = reverse_lazy('menu:item_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información sobre hijos al contexto
        context['has_children'] = self.object.children.exists()
        context['child_count'] = self.object.children.count()
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            heading = self.object.heading
            parent = self.object.parent
            
            # Eliminar el objeto
            response = super().form_valid(form)
            
            # Reordenar TODOS los items del mismo grupo desde 0
            items_to_reorder = MenuItem.objects.filter(
                heading=heading,
                parent=parent
            ).order_by('order')
            
            # Debug: ver qué items se van a reordenar
            print(f"Reordenando {items_to_reorder.count()} items")
            for item in items_to_reorder:
                print(f" - {item.name} (order={item.order})")
            
            # Renumerar secuencialmente desde 0
            for index, item in enumerate(items_to_reorder):
                item.order = index
                item.save()
                print(f"Actualizado: {item.name} -> order={index}")
            
            return response
        
class MenuTreeView(LoginRequiredMixin, TemplateView):
    template_name = 'menu/menu_tree.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headings = MenuHeading.objects.prefetch_related(
            'menuitem_set__children__children'
        ).all()
        context['headings'] = headings
        return context