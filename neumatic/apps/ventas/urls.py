# neumatic\apps\ventas\urls.py
from django.urls import path
from .views.factura_views import (FacturaListView, FacturaCreateView, 
								  FacturaUpdateView, FacturaDeleteView)

from .views.factura2_views import (FacturaManualListView, FacturaManualCreateView, 
								  FacturaManualUpdateView, FacturaManualDeleteView)

from .views.factura3_views import (PresupuestoListView, PresupuestoCreateView, 
								  PresupuestoUpdateView, PresupuestoDeleteView)

from .views.recibo_views import (ReciboListView, ReciboCreateView, 
								ReciboUpdateView, ReciboDeleteView)

from .views.consultas_factura_views import (buscar_agenda, 
											buscar_producto,
											buscar_cliente,
											validar_documento,
											detalle_producto,
											datos_comprobante,
											obtener_numero_comprobante,
											obtener_numero_comprobante2,
											validar_vencimientos_cliente,
											validar_deudas_cliente,
											valida_autorizacion,
											verificar_remito,
											buscar_banco,
											buscar_codigo_banco,
											obtener_libro_iva,
											buscar_factura)

from .views.crear_agenda import crear_agenda
from .views.genera_pdf import GeneraPDFView

urlpatterns = [
	path('factura/listar/', FacturaListView.as_view(), name='factura_list'),
	path('factura/crear/', FacturaCreateView.as_view(), name='factura_create'),
	path('factura/editar/<int:pk>/', FacturaUpdateView.as_view(), name='factura_update'),
	path('factura/eliminar/<int:pk>/', FacturaDeleteView.as_view(), name='factura_delete'),
	
	#-- Opción 2: Comprobante Manual.
	path('facturamanual/listar/', FacturaManualListView.as_view(), name='factura_manual_list'),
	path('facturamanual/crear/', FacturaManualCreateView.as_view(), name='factura_manual_create'),
	path('facturamanual/editar/<int:pk>/', FacturaManualUpdateView.as_view(), name='factura_manual_update'),
	path('facturamanual/eliminar/<int:pk>/', FacturaManualDeleteView.as_view(), name='factura_manual_delete'),
	
	#-- Opción 3: Presupuesto.
	path('presupuesto/listar/', PresupuestoListView.as_view(), name='presupuesto_list'),
	path('presupeusto/crear/', PresupuestoCreateView.as_view(), name='presupuesto_create'),
	path('presupuesto/editar/<int:pk>/', PresupuestoUpdateView.as_view(), name='presupuesto_update'),
	path('presupuesto/eliminar/<int:pk>/', PresupuestoDeleteView.as_view(), name='presupuesto_delete'),
	###
	
	path('recibo/listar/', ReciboListView.as_view(), name='recibo_list'),
	path('recibo/crear/', ReciboCreateView.as_view(), name='recibo_create'),
	path('recibo/editar/<int:pk>/', ReciboUpdateView.as_view(), name='recibo_update'),
	path('recibo/eliminar/<int:pk>/', ReciboDeleteView.as_view(), name='recibo_delete'),
	
	path('buscar/producto/', buscar_producto, name='buscar_producto'),
	path('validar/documento/', validar_documento, name='validar_documento'),
	path('buscar/agenda/', buscar_agenda, name='buscar_agenda'),
	path('buscar/cliente/', buscar_cliente, name='buscar_agenda'),
	
	path('crear/agenda/', crear_agenda, name='crear_agenda'),
	path('detalle_producto/<int:id_producto>/', detalle_producto, name='detalle_producto'),
	path('comprobante/<int:pk>/codigo/', datos_comprobante, name='comprobante_codigo'),
	path('obtener-numero-comprobante/', obtener_numero_comprobante, name='obtener_numero_comprobante'),
	path('obtener-numero-comprobante2/', obtener_numero_comprobante2, name='obtener_numero_comprobante2'),
	# path('<str:model_name>/pdf/<int:pk>/', GeneraPDFView.as_view(), name='generic_pdf'),
	# path('<str:model_string>/pdf/<int:pk>/', GeneraPDFView.as_view(), name='generic_pdf'),
	path('pdf/<int:pk>/', GeneraPDFView.as_view(), name='generic_pdf'),
	path('clientes/<int:cliente_id>/validar-vencimientos/', validar_vencimientos_cliente, name='validar_vencimientos'),
	path('clientes/<int:cliente_id>/validar-deudas-cliente/', validar_deudas_cliente, name='validar_deudas_cliente'),
	path('clientes/validar-autorizacion/', valida_autorizacion, name='validar_autorizacion'),
	path('verificar/remito/', verificar_remito, name='verificar_remito'),
	path('buscar/banco/', buscar_banco, name='buscar_banco'),
	path('buscar/codigo_banco/', buscar_codigo_banco, name='buscar_codigo_banco'),
	path('obtener/libro_iva/', obtener_libro_iva, name='obtener_libro_iva'),
	path('buscar/factura/', buscar_factura, name='buscar_factura'),
]