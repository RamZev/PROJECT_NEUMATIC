# \apps\maestros\urls.py
from django.urls import path

from .views.actividad_views import *

urlpatterns = [
    path('actividad/', ActividadListView.as_view(), name='actividad_list'),
    path('actividad/nueva/', ActividadCreateView.as_view(), name='actividad_create'),
    path('actividad/<int:pk>/editar/', ActividadUpdateView.as_view(), name='actividad_update'),
    path('actividad/<int:pk>/eliminar/', ActividadDeleteView.as_view(), name='actividad_delete'),
        
]