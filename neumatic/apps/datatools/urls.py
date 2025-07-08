# neumatic\apps\datatools\urls.py
from django.urls import path
from .views.consulta_facturas_views import ConsultaFacturasClienteView
from .views.consulta_facturas_views import ConsultaProductosView


urlpatterns = [
    path('facturas-cliente/', ConsultaFacturasClienteView.as_view(), name='consulta_facturas_cliente'),
    path('productos/', ConsultaProductosView.as_view(), name='consulta_productos_stock'),
]