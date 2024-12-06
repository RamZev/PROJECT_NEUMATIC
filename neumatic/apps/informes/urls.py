# neumatic\apps\informes\urls.py
from django.urls import path

from .views.cliente_list_views import (ClienteInformeListView, ClienteInformesView, ClienteInformePDFView)

urlpatterns = [
	path('cliente_informe/', ClienteInformeListView.as_view(),
		 name='cliente_informe_list'),
	
	path('cliente_generado/', ClienteInformesView.as_view(),
		 name='cliente_informe_generado'),
	path('cliente_vista_pdf/', ClienteInformePDFView.as_view(),
		 name='cliente_informe_pdf'),
]
