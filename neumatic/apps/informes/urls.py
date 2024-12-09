# neumatic\apps\informes\urls.py
from django.urls import path

from .views.cliente_list_views import *
from .views.proveedor_list_views import *

urlpatterns = [
	#-- Clientes.
	path('cliente_informe/', ClienteInformeListView.as_view(),
		 name='cliente_informe_list'),
	
	path('cliente_generado/', ClienteInformesView.as_view(),
		 name='cliente_informe_generado'),
	path('cliente_vista_pdf/', ClienteInformePDFView.as_view(),
		 name='cliente_informe_pdf'),
	
	#-- Proveedores.
	path('proveedor_informe/', ProveedorInformeListView.as_view(),
		 name='proveedor_informe_list'),
	
	path('proveedor_generado/', ProveedorInformesView.as_view(),
		 name='proveedor_informe_generado'),
	path('proveedor_vista_pdf/', ProveedorInformePDFView.as_view(),
		 name='proveedor_informe_pdf'),
	
]
