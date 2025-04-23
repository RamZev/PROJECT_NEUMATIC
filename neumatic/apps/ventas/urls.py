# neumatic\apps\ventas\urls.py
from django.urls import path
from .views.factura_views import (FacturaListView, FacturaCreateView, 
                                  FacturaUpdateView, FacturaDeleteView)

from .views.consultas_factura_views import (buscar_agenda, 
                                            buscar_producto,
                                            buscar_cliente,
                                            validar_documento,
                                            detalle_producto,
                                            datos_comprobante,
                                            obtener_numero_comprobante,
                                            validar_vencimientos_cliente,
                                            valida_autorizacion)

from .views.crear_agenda import crear_agenda
from .views.genera_pdf import GeneraPDFView

urlpatterns = [
   path('factura/listar/', FacturaListView.as_view(), name='factura_list'),
   path('factura/crear/', FacturaCreateView.as_view(), name='factura_create'),
   path('factura/editar/<int:pk>/', FacturaUpdateView.as_view(), name='factura_update'),
   path('factura/eliminar/<int:pk>/', FacturaDeleteView.as_view(), name='factura_delete'),
      
   path('buscar/producto/', buscar_producto, name='buscar_producto'),
   path('validar/documento/', validar_documento, name='validar_documento'),
   path('buscar/agenda/', buscar_agenda, name='buscar_agenda'),
   path('buscar/cliente/', buscar_cliente, name='buscar_agenda'),
   
   path('crear/agenda/', crear_agenda, name='crear_agenda'),
   path('detalle_producto/<int:id_producto>/', detalle_producto, name='detalle_producto'),
   path('comprobante/<int:pk>/codigo/', datos_comprobante, name='comprobante_codigo'),
   path('obtener-numero-comprobante/', obtener_numero_comprobante, name='obtener_numero_comprobante'),
   path('<str:model_name>/pdf/<int:pk>/', GeneraPDFView.as_view(), name='generic_pdf'),
   path('clientes/<int:cliente_id>/validar-vencimientos/', validar_vencimientos_cliente, name='validar_vencimientos'),
   path('clientes/validar-autorizacion/', valida_autorizacion, name='validar_autorizacion'),
]