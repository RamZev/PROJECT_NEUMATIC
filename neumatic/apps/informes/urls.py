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

#-- Procesos.
#- Lote 1:
from apps.informes.views.vlsaldosclientes_list_views import *
from apps.informes.views.vlsaldosclientes_list_views import *
from apps.informes.views.vlresumenctacte_list_views import *
from apps.informes.views.vlmercaderiaporcliente_list_views import *
from apps.informes.views.vlremitosclientes_list_views import *
from apps.informes.views.vltotalremitosclientes_list_views import *
from apps.informes.views.vlventacomprolocalidad_list_views import *
from apps.informes.views.vlventamostrador_list_views import *
from apps.informes.views.vlventacompro_list_views import *

#- Lote 2:
from apps.informes.views.vlcomprobantesvencidos_list_views import *
from apps.informes.views.vlremitospendientes_list_views import *
from apps.informes.views.vlremitosvendedor_list_views import *
from apps.informes.views.vlivaventasfull_list_views import *
from apps.informes.views.vlivaventasprovincias_list_views import *
from apps.informes.views.vlivaventassitrib_list_views import *
from apps.informes.views.vlpercepibvendedortotales_list_views import *
from apps.informes.views.vlpercepibvendedordetallado_list_views import *
from apps.informes.views.vlpercepibsubcuentatotales_list_views import *
from apps.informes.views.vlpercepibsubcuentadetallado_list_views import *

#- Lote 3:
from apps.informes.views.vlcomisionvendedor_list_views import *
from apps.informes.views.vlcomisionoperario_list_views import *
from apps.informes.views.vlpreciodiferente_list_views import *
from apps.informes.views.vlventasresumenib_list_views import *

#- Lote 4:
from apps.informes.views.vlestadisticasventas_list_views import *
from apps.informes.views.vlestadisticasventasvendedor_list_views import *



#-- Otras rutas.
from apps.maestros.views.consulta_views_maestros import filtrar_localidad
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
	
	#-- Informes-Procesos. --------------------------------------------------------
	
	# #-- VL Saldos Clientes.
	path('vlsaldosclientes_informe/', VLSaldosClientesInformeView.as_view(), 
		 name='vlsaldosclientes_informe_list'),
	path('vlsaldosclientes/vista-preliminar/', vlsaldosclientes_vista_pantalla, 
		 name="vlsaldosclientes_vista_pantalla"),
	path("vlsaldosclientes/vista-pdf/", vlsaldosclientes_vista_pdf, 
		 name="vlsaldosclientes_vista_pdf"),
	path("vlsaldosclientes/vista-excel/", vlsaldosclientes_vista_excel, 
		 name="vlsaldosclientes_vista_excel"),
	path("vlsaldosclientes/vista-csv/", vlsaldosclientes_vista_csv, 
		 name="vlsaldosclientes_vista_csv"),
	
	#-- VL Resumen Cuenta Corriente.
	path('vlresumenctacte_informe/', VLResumenCtaCteInformeView.as_view(), 
		 name='vlresumenctacte_informe_list'),
	path('vlresumenctacte/vista-preliminar/', vlresumenctacte_vista_pantalla, 
		 name="vlresumenctacte_vista_pantalla"),
	path("vlresumenctacte/vista-pdf/", vlresumenctacte_vista_pdf, 
		 name="vlresumenctacte_vista_pdf"),	
	path("vlresumenctacte/vista-excel/", vlresumenctacte_vista_excel, 
		 name="vlresumenctacte_vista_excel"),
	path("vlresumenctacte/vista-csv/", vlresumenctacte_vista_csv, 
		 name="vlresumenctacte_vista_csv"),
	
	#-- VL Mercadería por Cliente.
	path('vlmercaderiaporcliente_informe/', VLMercaderiaPorClienteInformeView.as_view(), 
		 name='vlmercaderiaporcliente_informe_list'),
	path('vlmercaderiaporcliente/vista-preliminar/', vlmercaderiaporcliente_vista_pantalla, 
		 name="vlmercaderiaporcliente_vista_pantalla"),
	path("vlmercaderiaporcliente/vista-pdf/", vlmercaderiaporcliente_vista_pdf, 
		 name="vlmercaderiaporcliente_vista_pdf"),
	path("vlmercaderiaporcliente/vista-excel/", vlmercaderiaporcliente_vista_excel, 
		 name="vlmercaderiaporcliente_vista_excel"),
	path("vlmercaderiaporcliente/vista-csv/", vlmercaderiaporcliente_vista_csv, 
		 name="vlmercaderiaporcliente_vista_csv"),
	
	#-- VL Remitos por Cliente.
	path('vlremitosclientes_informe/', VLRemitosClientesInformeView.as_view(), 
		 name='vlremitosclientes_informe_list'),
	path('vlremitosclientes/vista-preliminar/', vlremitosclientes_vista_pantalla, 
		 name="vlremitosclientes_vista_pantalla"),
	path("vlremitosclientes/vista-pdf/", vlremitosclientes_vista_pdf, 
		 name="vlremitosclientes_vista_pdf"),
	path("vlremitosclientes/vista-excel/", vlremitosclientes_vista_excel, 
		 name="vlremitosclientes_vista_excel"),
	path("vlremitosclientes/vista-csv/", vlremitosclientes_vista_csv, 
		 name="vlremitosclientes_vista_csv"),
	
	#-- VL Total Remitos por Cliente.
	path('vltotalremitosclientes_informe/', VLTotalRemitosClientesInformeView.as_view(), 
		 name='vltotalremitosclientes_informe_list'),
	path('vltotalremitosclientes/vista-preliminar/', vltotalremitosclientes_vista_pantalla, 
		 name="vltotalremitosclientes_vista_pantalla"),
	path("vltotalremitosclientes/vista-pdf/", vltotalremitosclientes_vista_pdf, 
		 name="vltotalremitosclientes_vista_pdf"),
	path("vltotalremitosclientes/vista-excel/", vltotalremitosclientes_vista_excel, 
		 name="vltotalremitosclientes_vista_excel"),
	path("vltotalremitosclientes/vista-csv/", vltotalremitosclientes_vista_csv, 
		 name="vltotalremitosclientes_vista_csv"),
	
	#-- VL Venta Compro Localidad.
	path('vlventacomprolocalidad_informe/', VLVentaComproLocalidadInformeView.as_view(), 
		 name='vlventacomprolocalidad_informe_list'),
	path('vlventacomprolocalidad/vista-preliminar/', vlventacomprolocalidad_vista_pantalla, 
		 name="vlventacomprolocalidad_vista_pantalla"),
	path("vlventacomprolocalidad/vista-pdf/", vlventacomprolocalidad_vista_pdf, 
		 name="vlventacomprolocalidad_vista_pdf"),
	path("vlventacomprolocalidad/vista-excel/", vlventacomprolocalidad_vista_excel, 
		 name="vlventacomprolocalidad_vista_excel"),
	path("vlventacomprolocalidad/vista-csv/", vlventacomprolocalidad_vista_csv, 
		 name="vlventacomprolocalidad_vista_csv"),
	
	#-- VL Venta Mostrador.
	path('vlventamostrador_informe/', VLVentaMostradorInformeView.as_view(), 
		 name='vlventamostrador_informe_list'),
	path('vlventamostrador/vista-preliminar/', vlventamostrador_vista_pantalla, 
		 name="vlventamostrador_vista_pantalla"),
	path("vlventamostrador/vista-pdf/", vlventamostrador_vista_pdf, 
		 name="vlventamostrador_vista_pdf"),
	path("vlventamostrador/vista-excel/", vlventamostrador_vista_excel, 
		 name="vlventamostrador_vista_excel"),
	path("vlventamostrador/vista-csv/", vlventamostrador_vista_csv, 
		 name="vlventamostrador_vista_csv"),
	
	#-- VL Venta Compro.
	path('vlventacompro_informe/', VLVentaComproInformeView.as_view(), 
		 name='vlventacompro_informe_list'),
	path('vlventacompro/vista-preliminar/', vlventacompro_vista_pantalla, 
		 name="vlventacompro_vista_pantalla"),
	path("vlventacompro/vista-pdf/", vlventacompro_vista_pdf, 
		 name="vlventacompro_vista_pdf"),
	path("vlventacompro/vista-excel/", vlventacompro_vista_excel, 
		 name="vlventacompro_vista_excel"),
	path("vlventacompro/vista-csv/", vlventacompro_vista_csv, 
		 name="vlventacompro_vista_csv"),
	
	#-- VL Comprobantes Vencidos.
	path('vlcomprobantesvencidos_informe/', VLComprobantesVencidosInformeView.as_view(), 
		 name='vlcomprobantesvencidos_informe_list'),
	path('vlcomprobantesvencidos/vista-preliminar/', vlcomprobantesvencidos_vista_pantalla, 
		 name="vlcomprobantesvencidos_vista_pantalla"),
	path("vlcomprobantesvencidos/vista-pdf/", vlcomprobantesvencidos_vista_pdf, 
		 name="vlcomprobantesvencidos_vista_pdf"),
	path("vlcomprobantesvencidos/vista-excel/", vlcomprobantesvencidos_vista_excel, 
		 name="vlcomprobantesvencidos_vista_excel"),
	path("vlcomprobantesvencidos/vista-csv/", vlcomprobantesvencidos_vista_csv, 
		 name="vlcomprobantesvencidos_vista_csv"),
	
	#-- VL Remitos Pendientes.
	path('vlremitospendientes_informe/', VLRemitosPendientesInformeView.as_view(), 
		 name='vlremitospendientes_informe_list'),
	path('vlremitospendientes/vista-preliminar/', vlremitospendientes_vista_pantalla, 
		 name="vlremitospendientes_vista_pantalla"),
	path("vlremitospendientes/vista-pdf/", vlremitospendientes_vista_pdf, 
		 name="vlremitospendientes_vista_pdf"),
	path("vlremitospendientes/vista-excel/", vlremitospendientes_vista_excel, 
		 name="vlremitospendientes_vista_excel"),
	path("vlremitospendientes/vista-csv/", vlremitospendientes_vista_csv, 
		 name="vlremitospendientes_vista_csv"),
	
	#-- VL Remitos por Vendedor.
	path('vlremitosvendedor_informe/', VLRemitosVendedorInformeView.as_view(), 
		 name='vlremitosvendedor_informe_list'),
	path('vlremitosvendedor/vista-preliminar/', vlremitosvendedor_vista_pantalla, 
		 name="vlremitosvendedor_vista_pantalla"),
	path("vlremitosvendedor/vista-pdf/", vlremitosvendedor_vista_pdf, 
		 name="vlremitosvendedor_vista_pdf"),
	path("vlremitosvendedor/vista-excel/", vlremitosvendedor_vista_excel, 
		 name="vlremitosvendedor_vista_excel"),
	path("vlremitosvendedor/vista-csv/", vlremitosvendedor_vista_csv, 
		 name="vlremitosvendedor_vista_csv"),
	
	#-- VL IVA Ventas FULL.
	path('vlivaventasfull_informe/', VLIVAVentasFULLInformeView.as_view(), 
		 name='vlivaventasfull_informe_list'),
	path('vlivaventasfull/vista-preliminar/', vlivaventasfull_vista_pantalla, 
		 name="vlivaventasfull_vista_pantalla"),
	path("vlivaventasfull/vista-pdf/", vlivaventasfull_vista_pdf, 
		 name="vlivaventasfull_vista_pdf"),
	path("vlivaventasfull/vista-excel/", vlivaventasfull_vista_excel, 
		 name="vlivaventasfull_vista_excel"),
	path("vlivaventasfull/vista-csv/", vlivaventasfull_vista_csv, 
		 name="vlivaventasfull_vista_csv"),
	
	#-- VL IVA Ventas - Totales por Provincias.
	path('vlivaventasprovincias_informe/', VLIVAVentasProvinciasInformeView.as_view(), 
		 name='vlivaventasprovincias_informe_list'),
	path('vlivaventasprovincias/vista-preliminar/', vlivaventasprovincias_vista_pantalla, 
		 name="vlivaventasprovincias_vista_pantalla"),
	path("vlivaventasprovincias/vista-pdf/", vlivaventasprovincias_vista_pdf, 
		 name="vlivaventasprovincias_vista_pdf"),
	path("vlivaventasprovincias/vista-excel/", vlivaventasprovincias_vista_excel, 
		 name="vlivaventasprovincias_vista_excel"),
	path("vlivaventasprovincias/vista-csv/", vlivaventasprovincias_vista_csv, 
		 name="vlivaventasprovincias_vista_csv"),
	
	#-- VL IVA Ventas - Totales para SITRIB.
	path('vlivaventassitrib_informe/', VLIVAVentasSitribInformeView.as_view(), 
		 name='vlivaventassitrib_informe_list'),
	path('vlivaventassitrib/vista-preliminar/', vlivaventassitrib_vista_pantalla, 
		 name="vlivaventassitrib_vista_pantalla"),
	path("vlivaventassitrib/vista-pdf/", vlivaventassitrib_vista_pdf, 
		 name="vlivaventassitrib_vista_pdf"),
	path("vlivaventassitrib/vista-excel/", vlivaventassitrib_vista_excel, 
		 name="vlivaventassitrib_vista_excel"),
	path("vlivaventassitrib/vista-csv/", vlivaventassitrib_vista_csv, 
		 name="vlivaventassitrib_vista_csv"),
	
	#-- VL Percep IB Vendedor - Totales.
	path('vlpercepibvendedortotales_informe/', VLPercepIBVendedorTotalesInformeView.as_view(), 
		 name='vlpercepibvendedortotales_informe_list'),
	path('vlpercepibvendedortotales/vista-preliminar/', vlpercepibvendedortotales_vista_pantalla, 
		 name="vlpercepibvendedortotales_vista_pantalla"),
	path("vlpercepibvendedortotales/vista-pdf/", vlpercepibvendedortotales_vista_pdf, 
		 name="vlpercepibvendedortotales_vista_pdf"),
	path("vlpercepibvendedortotales/vista-excel/", vlpercepibvendedortotales_vista_excel, 
		 name="vlpercepibvendedortotales_vista_excel"),
	path("vlpercepibvendedortotales/vista-csv/", vlpercepibvendedortotales_vista_csv, 
		 name="vlpercepibvendedortotales_vista_csv"),
	
	#-- VL Percep IB Vendedor - Detallado.
	path('vlpercepibvendedordetallado_informe/', VLPercepIBVendedorDetalladoInformeView.as_view(), 
		 name='vlpercepibvendedordetallado_informe_list'),
	path('vlpercepibvendedordetallado/vista-preliminar/', vlpercepibvendedordetallado_vista_pantalla, 
		 name="vlpercepibvendedordetallado_vista_pantalla"),
	path("vlpercepibvendedordetallado/vista-pdf/", vlpercepibvendedordetallado_vista_pdf, 
		 name="vlpercepibvendedordetallado_vista_pdf"),
	path("vlpercepibvendedordetallado/vista-excel/", vlpercepibvendedordetallado_vista_excel, 
		 name="vlpercepibvendedordetallado_vista_excel"),
	path("vlpercepibvendedordetallado/vista-csv/", vlpercepibvendedordetallado_vista_csv, 
		 name="vlpercepibvendedordetallado_vista_csv"),
	
	#-- VL Percep IB Subcuenta - Totales.
	path('vlpercepibsubcuentatotales_informe/', VLPercepIBSubcuentaTotalesInformeView.as_view(), 
		 name='vlpercepibsubcuentatotales_informe_list'),
	path('vlpercepibsubcuentatotales/vista-preliminar/', vlpercepibsubcuentatotales_vista_pantalla, 
		 name="vlpercepibsubcuentatotales_vista_pantalla"),
	path("vlpercepibsubcuentatotales/vista-pdf/", vlpercepibsubcuentatotales_vista_pdf, 
		 name="vlpercepibsubcuentatotales_vista_pdf"),
	path("vlpercepibsubcuentatotales/vista-excel/", vlpercepibsubcuentatotales_vista_excel, 
		 name="vlpercepibsubcuentatotales_vista_excel"),
	path("vlpercepibsubcuentatotales/vista-csv/", vlpercepibsubcuentatotales_vista_csv, 
		 name="vlpercepibsubcuentatotales_vista_csv"),
	
	#-- VL Percep IB Subcuenta - Detallado.
	path('vlpercepibsubcuentadetallado_informe/', VLPercepIBSubcuentaDetalladoInformeView.as_view(), 
		 name='vlpercepibsubcuentadetallado_informe_list'),
	path('vlpercepibsubcuentadetallado/vista-preliminar/', vlpercepibsubcuentadetallado_vista_pantalla, 
		 name="vlpercepibsubcuentadetallado_vista_pantalla"),
	path("vlpercepibsubcuentadetallado/vista-pdf/", vlpercepibsubcuentadetallado_vista_pdf, 
		 name="vlpercepibsubcuentadetallado_vista_pdf"),
	path("vlpercepibsubcuentadetallado/vista-excel/", vlpercepibsubcuentadetallado_vista_excel, 
		 name="vlpercepibsubcuentadetallado_vista_excel"),
	path("vlpercepibsubcuentadetallado/vista-csv/", vlpercepibsubcuentadetallado_vista_csv, 
		 name="vlpercepibsubcuentadetallado_vista_csv"),
	
	#-- VL Comisión Vendedor.
	path('vlcomisionvendedor_informe/', VLComisionVendedorInformeView.as_view(), 
		 name='vlcomisionvendedor_informe_list'),
	path('vlcomisionvendedor/vista-preliminar/', vlcomisionvendedor_vista_pantalla, 
		 name="vlcomisionvendedor_vista_pantalla"),
	path("vlcomisionvendedor/vista-pdf/", vlcomisionvendedor_vista_pdf, 
		 name="vlcomisionvendedor_vista_pdf"),
	path("vlcomisionvendedor/vista-excel/", vlcomisionvendedor_vista_excel, 
		 name="vlcomisionvendedor_vista_excel"),
	path("vlcomisionvendedor/vista-csv/", vlcomisionvendedor_vista_csv, 
		 name="vlcomisionvendedor_vista_csv"),
	
	#-- VL Comisión Operario.
	path('vlcomisionoperario_informe/', VLComisionOperarioInformeView.as_view(), 
		 name='vlcomisionoperario_informe_list'),
	path('vlcomisionoperario/vista-preliminar/', vlcomisionoperario_vista_pantalla, 
		 name="vlcomisionoperario_vista_pantalla"),
	path("vlcomisionoperario/vista-pdf/", vlcomisionoperario_vista_pdf, 
		 name="vlcomisionoperario_vista_pdf"),
	path("vlcomisionoperario/vista-excel/", vlcomisionoperario_vista_excel, 
		 name="vlcomisionoperario_vista_excel"),
	path("vlcomisionoperario/vista-csv/", vlcomisionoperario_vista_csv, 
		 name="vlcomisionoperario_vista_csv"),
	
	#-- VL Precio Diferente.
	path('vlpreciodiferente_informe/', VLPrecioDiferenteInformeView.as_view(), 
		 name='vlpreciodiferente_informe_list'),
	path('vlpreciodiferente/vista-preliminar/', vlpreciodiferente_vista_pantalla, 
		 name="vlpreciodiferente_vista_pantalla"),
	path("vlpreciodiferente/vista-pdf/", vlpreciodiferente_vista_pdf, 
		 name="vlpreciodiferente_vista_pdf"),
	path("vlpreciodiferente/vista-excel/", vlpreciodiferente_vista_excel, 
		 name="vlpreciodiferente_vista_excel"),
	path("vlpreciodiferente/vista-csv/", vlpreciodiferente_vista_csv, 
		 name="vlpreciodiferente_vista_csv"),
	
	#-- VL Ventas Resumne IB.
	path('vlventasresumenib_informe/', VLVentasResumenIBInformeView.as_view(), 
		 name='vlventasresumenib_informe_list'),
	path('vlventasresumenib/vista-preliminar/', vlventasresumenib_vista_pantalla, 
		 name="vlventasresumenib_vista_pantalla"),
	path("vlventasresumenib/vista-pdf/", vlventasresumenib_vista_pdf, 
		 name="vlventasresumenib_vista_pdf"),
	path("vlventasresumenib/vista-excel/", vlventasresumenib_vista_excel, 
		 name="vlventasresumenib_vista_excel"),
	path("vlventasresumenib/vista-csv/", vlventasresumenib_vista_csv, 
		 name="vlventasresumenib_vista_csv"),
	
	#-- VL Estadísticas de Ventas.
	path('vlestadisticasventas_informe/', VLEstadisticasVentasInformeView.as_view(), 
		 name='vlestadisticasventas_informe_list'),
	path('vlestadisticasventas/vista-preliminar/', vlestadisticasventas_vista_pantalla, 
		 name="vlestadisticasventas_vista_pantalla"),
	path("vlestadisticasventas/vista-pdf/", vlestadisticasventas_vista_pdf, 
		 name="vlestadisticasventas_vista_pdf"),
	path("vlestadisticasventas/vista-excel/", vlestadisticasventas_vista_excel, 
		 name="vlestadisticasventas_vista_excel"),
	path("vlestadisticasventas/vista-csv/", vlestadisticasventas_vista_csv, 
		 name="vlestadisticasventas_vista_csv"),
	
	#-- VL Estadísticas de Ventas Vendedor.
	path('vlestadisticasventasvendedor_informe/', VLEstadisticasVentasVendedorInformeView.as_view(), 
		 name='vlestadisticasventasvendedor_informe_list'),
	path('vlestadisticasventasvendedor/vista-preliminar/', vlestadisticasventasvendedor_vista_pantalla, 
		 name="vlestadisticasventasvendedor_vista_pantalla"),
	path("vlestadisticasventasvendedor/vista-pdf/", vlestadisticasventasvendedor_vista_pdf, 
		 name="vlestadisticasventasvendedor_vista_pdf"),
	path("vlestadisticasventasvendedor/vista-excel/", vlestadisticasventasvendedor_vista_excel, 
		 name="vlestadisticasventasvendedor_vista_excel"),
	path("vlestadisticasventasvendedor/vista-csv/", vlestadisticasventasvendedor_vista_csv, 
		 name="vlestadisticasventasvendedor_vista_csv"),
	
	
	
	
	#-- Otras rutas.
	path('filtrar-localidad/', filtrar_localidad, name='filtrar_localidad'),
	path('buscar/cliente/id/', buscar_cliente_id, name='buscar_cliente_id'),
	path('buscar/cliente/', buscar_cliente, name='buscar_cliente'),
	
	

]
