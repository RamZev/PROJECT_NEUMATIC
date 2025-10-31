# neumatic\apps\menu\models.py
from django.db import models
from django.contrib.auth.models import Group
from django.utils.text import slugify

class MenuHeading(models.Model):
    id_menu_heading = models.AutoField(primary_key=True, verbose_name="ID Encabezado de Menú")
    name = models.CharField(max_length=100, verbose_name="Nombre del encabezado")
    order = models.IntegerField(default=0, verbose_name="Orden de aparición")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Encabezado de Menú"
        verbose_name_plural = "Encabezados de Menú"
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    id_menu_item = models.AutoField(primary_key=True, verbose_name="ID Item de Menú")
    heading = models.ForeignKey(MenuHeading, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Encabezado asociado")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name="Item padre")
    name = models.CharField(max_length=100, verbose_name="Nombre del item")
    url_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre de la URL (para {% url %})")
    query_params = models.CharField(max_length=200, blank=True, verbose_name="Parámetros de query (ej: ?proceso=actualizar)")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Clase del icono (ej: fas fa-book-open)")
    is_collapse = models.BooleanField(default=False, verbose_name="¿Es colapsable? (tiene subitems)")
    order = models.IntegerField(default=0, verbose_name="Orden de aparición")
    groups = models.ManyToManyField(Group, blank=True, verbose_name="Grupos permitidos")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Item de Menú"
        verbose_name_plural = "Items de Menú"
    
    def __str__(self):
        return self.name
    
    def get_collapse_id(self):
        return f"collapse{slugify(self.name).capitalize()}"
    
    def has_access(self, user, check_children=True):
        print(f"MODEL DEBUG: Checking access for user '{user}' on item '{self.name}' (ID: {self.id_menu_item})")
        print(f"MODEL DEBUG: Item groups: {[g.name for g in self.groups.all()]}")
        print(f"MODEL DEBUG: User groups: {[g.name for g in user.groups.all()]}")
        print(f"MODEL DEBUG: User is superuser: {user.is_superuser}")
        
        # Superusuarios tienen acceso completo
        if user.is_superuser:
            print(f"MODEL DEBUG: Superuser - Access: True")
            return True
        
        # Si el item tiene grupos asignados, verificar acceso directo
        if self.groups.exists():
            user_has_group = user.groups.filter(pk__in=self.groups.values_list('pk', flat=True)).exists()
            result = user_has_group
            print(f"MODEL DEBUG: Has groups - Access: {result}")
            return result
        
        # Si es un item final (no colapsible) y no tiene grupos, no es accesible
        if not self.is_collapse:
            print(f"MODEL DEBUG: Final item without groups - Access: False")
            return False
        
        # Si es un item colapsable (padre) y no tiene grupos, verificar si tiene hijos accesibles
        if check_children and self.is_collapse and self.children.exists():
            # Verificar recursivamente si algún hijo tiene acceso
            for child in self.children.all():
                if child.has_access(user, check_children=True):
                    print(f"MODEL DEBUG: Collapsable parent with accessible children - Access: True")
                    return True
        
        # Si no cumple ninguna condición, no es accesible
        print(f"MODEL DEBUG: No access conditions met - Access: False")
        return False