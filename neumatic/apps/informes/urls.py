# neumatic\apps\informes\urls.py
from django.urls import path

from .views.cliente_list_views import ClienteInformeListView

urlpatterns = [
  path('cliente_informe/', ClienteInformeListView.as_view(), name='cliente_informe_list'),

]