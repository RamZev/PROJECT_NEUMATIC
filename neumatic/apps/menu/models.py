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
    
    def has_access(self, user):
        if not self.groups.exists():
            return True
        return user.groups.filter(pk__in=self.groups.values_list('pk', flat=True)).exists()