# neumatic\apps\datatools\urls.py
from django.urls import path
from .views.consulta_facturas_views import ConsultaFacturasClienteView
from .views.consulta_facturas_views import ConsultaProductosView
from .views.excel_views import ExcelUploadView, ExcelPreviewView

urlpatterns = [
    path('facturas-cliente/', ConsultaFacturasClienteView.as_view(), name='consulta_facturas_cliente'),
    path('productos/', ConsultaProductosView.as_view(), name='consulta_productos_stock'),
	
	path('cargar-excel/', ExcelUploadView.as_view(), name='cargar_excel'),
	path('previsualizar-excel/', ExcelPreviewView.as_view(), name='excel_preview'),
]