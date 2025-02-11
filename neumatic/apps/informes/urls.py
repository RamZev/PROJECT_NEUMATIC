# neumatic\apps\informes\urls.py
from django.urls import path

#-- Catálogos.
from .views.cliente_list_views import *
from .views.proveedor_list_views import *
from .views.vendedor_list_views import *

#-- Tablas.
from .views.actividad_list_views import *
from .views.productodeposito_list_views import *
from .views.productofamilia_list_views import *
from .views.productomarca_list_views import *
from .views.productomodelo_list_views import *
from .views.productocai_list_views import *
from .views.productoestado_list_views import *
from .views.comprobanteventa_list_views import *
from .views.comprobantecompra_list_views import *
from .views.moneda_list_views import *
from .views.provincia_list_views import *
from .views.localidad_list_views import *
from .views.tipodocumentoidentidad_list_views import *
from .views.tipoiva_list_views import *
from .views.alicuotaiva_list_views import *
from .views.tipopercepcionib_list_views import *
from .views.tiporetencionib_list_views import *
from .views.operario_list_views import *
from .views.mediopago_list_views import *
from .views.puntoventa_list_views import *

#-- Otras rutas.
from apps.maestros.views.consulta_views_maestros import filtrar_localidad
from apps.informes.views.saldosclientes_list_views import *
from apps.informes.views.resumenctacte_list_views import *
from apps.informes.views.mercaderiaporcliente_list_views import *
from apps.informes.views.remitosclientes_list_views import *
from apps.informes.views.totalremitosclientes_list_views import *
from apps.informes.views.ventacomprolocalidad_list_views import *
from apps.informes.views.ventamostrador_list_views import *
from apps.informes.views.ventacompro_list_views import *


from apps.informes.views.ventacompro_list_views_prop import *


from apps.informes.views.consultas_informes_views import *

urlpatterns = [
	#-- Catálogos.
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
	
	#-- Vendedores.
	path('vendedor_informe/', VendedorInformeListView.as_view(),
		 name='vendedor_informe_list'),
	
	path('vendedor_generado/', VendedorInformesView.as_view(),
		 name='vendedor_informe_generado'),
	path('vendedor_vista_pdf/', VendedorInformePDFView.as_view(),
		 name='vendedor_informe_pdf'),
	
	#-- Tablas.
	#-- Actividades.
	path('actividad_informe/', ActividadInformeListView.as_view(),
		 name='actividad_informe_list'),
	
	path('actividad_generado/', ActividadInformesView.as_view(),
		 name='actividad_informe_generado'),
	path('actividad_vista_pdf/', ActividadInformePDFView.as_view(),
		 name='actividad_informe_pdf'),
	
	#-- Producto Depósitos.
	path('productodeposito_informe/', ProductoDepositoInformeListView.as_view(),
		 name='productodeposito_informe_list'),
	
	path('productodeposito_generado/', ProductoDepositoInformesView.as_view(),
		 name='productodeposito_informe_generado'),
	path('productodeposito_vista_pdf/', ProductoDepositoInformePDFView.as_view(),
		 name='productodeposito_informe_pdf'),
	
	#-- Producto Familia.
	path('productofamilia_informe/', ProductoFamiliaInformeListView.as_view(),
		 name='productofamilia_informe_list'),
	
	path('productofamilia_generado/', ProductoFamiliaInformesView.as_view(),
		 name='productofamilia_informe_generado'),
	path('productofamilia_vista_pdf/', ProductoFamiliaInformePDFView.as_view(),
		 name='productofamilia_informe_pdf'),
	
	#-- Producto Marca.
	path('productomarca_informe/', ProductoMarcaInformeListView.as_view(),
		 name='productomarca_informe_list'),
	
	path('productomarca_generado/', ProductoMarcaInformesView.as_view(),
		 name='productomarca_informe_generado'),
	path('productomarca_vista_pdf/', ProductoMarcaInformePDFView.as_view(),
		 name='productomarca_informe_pdf'),
	
	#-- Producto Modelo.
	path('productomodelo_informe/', ProductoModeloInformeListView.as_view(),
		 name='productomodelo_informe_list'),
	
	path('productomodelo_generado/', ProductoModeloInformesView.as_view(),
		 name='productomodelo_informe_generado'),
	path('productomodelo_vista_pdf/', ProductoModeloInformePDFView.as_view(),
		 name='productomodelo_informe_pdf'),
	
	#-- Producto CAI.
	path('productocai_informe/', ProductoCaiInformeListView.as_view(),
		 name='productocai_informe_list'),
	
	path('productocai_generado/', ProductoCaiInformesView.as_view(),
		 name='productocai_informe_generado'),
	path('productocai_vista_pdf/', ProductoCaiInformePDFView.as_view(),
		 name='productocai_informe_pdf'),
	
	#-- Producto Estado.
	path('productoestado_informe/', ProductoEstadoInformeListView.as_view(),
		 name='productoestado_informe_list'),
	
	path('productoestado_generado/', ProductoEstadoInformesView.as_view(),
		 name='productoestado_informe_generado'),
	path('productoestado_vista_pdf/', ProductoEstadoInformePDFView.as_view(),
		 name='productoestado_informe_pdf'),
	
	#-- Comprobante Venta.
	path('comprobanteventa_informe/', ComprobanteVentaInformeListView.as_view(),
		 name='comprobanteventa_informe_list'),
	
	path('comprobanteventa_generado/', ComprobanteVentaInformesView.as_view(),
		 name='comprobanteventa_informe_generado'),
	path('comprobanteventa_vista_pdf/', ComprobanteVentaInformePDFView.as_view(),
		 name='comprobanteventa_informe_pdf'),
	
	#-- Comprobante Compra.
	path('comprobantecompra_informe/', ComprobanteCompraInformeListView.as_view(),
		 name='comprobantecompra_informe_list'),
	
	path('comprobantecompra_generado/', ComprobanteCompraInformesView.as_view(),
		 name='comprobantecompra_informe_generado'),
	path('comprobantecompra_vista_pdf/', ComprobanteCompraInformePDFView.as_view(),
		 name='comprobantecompra_informe_pdf'),
	
	#-- Moneda.
	path('moneda_informe/', MonedaInformeListView.as_view(),
		 name='moneda_informe_list'),
	
	path('moneda_generado/', MonedaInformesView.as_view(),
		 name='moneda_informe_generado'),
	path('moneda_vista_pdf/', MonedaInformePDFView.as_view(),
		 name='moneda_informe_pdf'),
	
	#-- Provincia.
	path('provincia_informe/', ProvinciaInformeListView.as_view(),
		 name='provincia_informe_list'),
	
	path('provincia_generado/', ProvinciaInformesView.as_view(),
		 name='provincia_informe_generado'),
	path('provincia_vista_pdf/', ProvinciaInformePDFView.as_view(),
		 name='provincia_informe_pdf'),
	
	#-- Localidades.
	path('localidad_informe/', LocalidadInformeListView.as_view(),
		 name='localidad_informe_list'),
	
	path('localidad_generado/', LocalidadInformesView.as_view(),
		 name='localidad_informe_generado'),
	path('localidad_vista_pdf/', LocalidadInformePDFView.as_view(),
		 name='localidad_informe_pdf'),
	
	#-- Tipo Documento Identidad.
	path('tipo_documento_identidad_informe/', TipoDocumentoIdentidadInformeListView.as_view(),
		 name='tipodocumentoidentidad_informe_list'),
	
	path('tipo_documento_identidad_generado/', TipoDocumentoIdentidadInformesView.as_view(),
		 name='tipodocumentoidentidad_informe_generado'),
	path('tipo_documento_identidad_vista_pdf/', TipoDocumentoIdentidadInformePDFView.as_view(),
		 name='tipodocumentoidentidad_informe_pdf'),
	
	#-- Tipo IVA.
	path('tipo_iva_informe/', TipoIvaInformeListView.as_view(),
		 name='tipoiva_informe_list'),
	
	path('tipo_iva_generado/', TipoIvaInformesView.as_view(),
		 name='tipoiva_informe_generado'),
	path('tipo_iva_vista_pdf/', TipoIvaInformePDFView.as_view(),
		 name='tipoiva_informe_pdf'),
	
	#-- Alícuota IVA.
	path('alicuota_iva_informe/', AlicuotaIvaInformeListView.as_view(),
		 name='alicuotaiva_informe_list'),
	
	path('alicuota_iva_generado/', AlicuotaIvaInformesView.as_view(),
		 name='alicuotaiva_informe_generado'),
	path('alicuota_iva_vista_pdf/', AlicuotaIvaInformePDFView.as_view(),
		 name='alicuotaiva_informe_pdf'),
	
	#-- Tipo Percepción Ib.
	path('tipo_percepcion_ib_informe/', TipoPercepcionIbInformeListView.as_view(),
		 name='tipopercepcionib_informe_list'),
	
	path('tipo_percepcion_ib_generado/', TipoPercepcionIbInformesView.as_view(),
		 name='tipopercepcionib_informe_generado'),
	path('tipo_percepcion_ib_vista_pdf/', TipoPercepcionIbInformePDFView.as_view(),
		 name='tipopercepcionib_informe_pdf'),
	
	#-- Tipo Retención Ib.
	path('tipo_retencion_ib_informe/', TipoRetencionIbInformeListView.as_view(),
		 name='tiporetencionib_informe_list'),
	
	path('tipo_retencion_ib_generado/', TipoRetencionIbInformesView.as_view(),
		 name='tiporetencionib_informe_generado'),
	path('tipo_retencion_ib_vista_pdf/', TipoRetencionIbInformePDFView.as_view(),
		 name='tiporetencionib_informe_pdf'),
	
	#-- Operario.
	path('operario_informe/', OperarioInformeListView.as_view(),
		 name='operario_informe_list'),
	
	path('operario_generado/', OperarioInformesView.as_view(),
		 name='operario_informe_generado'),
	path('operario_vista_pdf/', OperarioInformePDFView.as_view(),
		 name='operario_informe_pdf'),
	
	#-- Medio Pago.
	path('medio_pago_informe/', MedioPagoInformeListView.as_view(),
		 name='mediopago_informe_list'),
	
	path('medio_pago_generado/', MedioPagoInformesView.as_view(),
		 name='mediopago_informe_generado'),
	path('medio_pago_vista_pdf/', MedioPagoInformePDFView.as_view(),
		 name='mediopago_informe_pdf'),
	
	#-- Punto Venta.
	path('punto_venta_informe/', PuntoVentaInformeListView.as_view(),
		 name='puntoventa_informe_list'),
	
	path('punto_venta_generado/', PuntoVentaInformesView.as_view(),
		 name='puntoventa_informe_generado'),
	path('punto_venta_vista_pdf/', PuntoVentaInformePDFView.as_view(),
		 name='puntoventa_informe_pdf'),
		 
	#-- VL Saldos Clientes.
	path('vlsaldosclientes_informe/', VLSaldosClientesInformeListView.as_view(),
		 name='vlsaldosclientes_informe_list'),
	
	path('vlsaldosclientes_generado/', VLSaldosClientesInformesView.as_view(),
		 name='vlsaldosclientes_informe_generado'),
	path('vlsaldosclientes_vista_pdf/', VLSaldosClientesInformePDFView.as_view(),
		 name='vlsaldosclientes_informe_pdf'),
	
	#-- VL Resumen Cuenta Corriente.
	path('vlresumenctacte_informe/', VLResumenCtaCteInformeListView.as_view(),
		 name='vlresumenctacte_informe_list'),
	
	path('vlresumenctacte_generado/', VLResumenCtaCteInformesView.as_view(),
		 name='vlresumenctacte_informe_generado'),
	path('vlresumenctacte_vista_pdf/', VLResumenCtaCteInformePDFView.as_view(),
		 name='vlresumenctacte_informe_pdf'),
	
	#-- VL Mercadería por Cliente.
	path('vlmercaderiaporcliente_informe/', VLMercaderiaPorClienteInformeListView.as_view(),
		 name='vlmercaderiaporcliente_informe_list'),
	
	path('vlmercaderiaporcliente_generado/', VLMercaderiaPorClienteInformesView.as_view(),
		 name='vlmercaderiaporcliente_informe_generado'),
	path('vlmercaderiaporcliente_vista_pdf/', VLMercaderiaPorClienteInformePDFView.as_view(),
		 name='vlmercaderiaporcliente_informe_pdf'),
	
	#-- VL Remitos por Cliente.
	path('vlremitosclientes_informe/', VLRemitosClientesInformeListView.as_view(),
		 name='vlremitosclientes_informe_list'),
	
	path('vlremitosclientes_generado/', VLRemitosClientesInformesView.as_view(),
		 name='vlremitosclientes_informe_generado'),
	path('vlremitosclientes_vista_pdf/', VLRemitosClientesInformePDFView.as_view(),
		 name='vlremitosclientes_informe_pdf'),
	
	#-- VL Total Remitos por Cliente.
	path('vltotalremitosclientes_informe/', VLTotalRemitosClientesInformeListView.as_view(),
		 name='vltotalremitosclientes_informe_list'),
	
	path('vltotalremitosclientes_generado/', VLTotalRemitosClientesInformesView.as_view(),
		 name='vltotalremitosclientes_informe_generado'),
	path('vltotalremitosclientes_vista_pdf/', VLTotalRemitosClientesInformePDFView.as_view(),
		 name='vltotalremitosclientes_informe_pdf'),
	
	#-- VL Venta Compro Localidad.
	path('vlventacomprolocalidad_informe/', VLVentaComproLocalidadInformeListView.as_view(),
		 name='vlventacomprolocalidad_informe_list'),
	
	path('vlventacomprolocalidad_generado/', VLVentaComproLocalidadInformesView.as_view(),
		 name='vlventacomprolocalidad_informe_generado'),
	path('vlventacomprolocalidad_vista_pdf/', VLVentaComproLocalidadInformePDFView.as_view(),
		 name='vlventacomprolocalidad_informe_pdf'),
	
	#-- VL Venta Mostrador.
	path('vlventamostrador_informe/', VLVentaMostradorInformeListView.as_view(),
		 name='vlventamostrador_informe_list'),
	
	path('vlventamostrador_generado/', VLVentaMostradorInformesView.as_view(),
		 name='vlventamostrador_informe_generado'),
	path('vlventamostrador_vista_pdf/', VLVentaMostradorInformePDFView.as_view(),
		 name='vlventamostrador_informe_pdf'),
	
	#-- VL Venta Compro.
	path('vlventacompro_informe/', VLVentaComproInformeListView.as_view(),
		 name='vlventacompro_informe_list'),
	
	path('vlventacompro_generado/', VLVentaComproInformesView.as_view(),
		 name='vlventacompro_informe_generado'),
	path('vlventacompro_vista_pdf/', VLVentaComproInformePDFView.as_view(),
		 name='vlventacompro_informe_pdf'),
	
	
	#-- VL Venta Compro Propuesta nueva.
	path('vlventacompro_informe_prop/', VLVentaComproInformeView.as_view(),
		 name='vlventacompro_informe_list_prop'),
	
	path('ventacompro/vista-preliminar/', ventacompro_vista_pantalla, name="ventacompro_vista_pantalla"),
	path("ventacompro/vista-pdf/", ventacompro_vista_pdf, name="ventacompro_vista_pdf"),
	
	
	
	#-- Otras rutas.
	path('filtrar-localidad/', filtrar_localidad, name='filtrar_localidad'),
	path('buscar/cliente/id/', buscar_cliente_id, name='buscar_cliente_id'),
	path('buscar/cliente/', buscar_cliente, name='buscar_cliente'),
	
	

]
