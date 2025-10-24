from django.db import migrations

def create_menu(apps, schema_editor):
    MenuHeading = apps.get_model('menu', 'MenuHeading')
    MenuItem = apps.get_model('menu', 'MenuItem')
    
    # Encabezados
    core = MenuHeading.objects.create(name='Core', order=1)
    ventas = MenuHeading.objects.create(name='Ventas', order=2)
    estadisticas = MenuHeading.objects.create(name='Estadísticas', order=3)
    
    # Core
    MenuItem.objects.create(heading=core, name='Panel', url_name='home', icon='fas fa-tachometer-alt', is_collapse=False, order=1)
    
    # Ventas > Archivos
    archivos = MenuItem.objects.create(heading=ventas, name='Archivos', icon='fas fa-book-open', is_collapse=True, order=1)
    catalogos = MenuItem.objects.create(parent=archivos, name='Catálogos', is_collapse=True, order=1)
    MenuItem.objects.create(parent=catalogos, name='Clientes', url_name='cliente_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=catalogos, name='Proveedores', url_name='proveedor_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=catalogos, name='Productos', url_name='producto_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=catalogos, name='Vendedores', url_name='vendedor_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=catalogos, name='Empresa', url_name='empresa_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=catalogos, name='Sucursales', url_name='sucursal_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=catalogos, name='Números', url_name='numero_list', is_collapse=False, order=7)
    
    tablas = MenuItem.objects.create(parent=archivos, name='Tablas', is_collapse=True, order=2)
    MenuItem.objects.create(parent=tablas, name='Actividad', url_name='actividad_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=tablas, name='Prod. Depósito', url_name='producto_deposito_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=tablas, name='Prod. Familia', url_name='producto_familia_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=tablas, name='Prod. Marca', url_name='producto_marca_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=tablas, name='Prod. Modelo', url_name='producto_modelo_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=tablas, name='Prod. CAI', url_name='producto_cai_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=tablas, name='Prod. Estado', url_name='producto_estado_list', is_collapse=False, order=7)
    MenuItem.objects.create(parent=tablas, name='Estados de Productos por Medidas', url_name='medidas_estados_list', is_collapse=False, order=8)
    MenuItem.objects.create(parent=tablas, name='Comp. Venta', url_name='comprobante_venta_list', is_collapse=False, order=9)
    MenuItem.objects.create(parent=tablas, name='Comp. Compra', url_name='comprobante_compra_list', is_collapse=False, order=10)
    MenuItem.objects.create(parent=tablas, name='Moneda', url_name='moneda_list', is_collapse=False, order=11)
    MenuItem.objects.create(parent=tablas, name='Provincia', url_name='provincia_list', is_collapse=False, order=12)
    MenuItem.objects.create(parent=tablas, name='Localidad', url_name='localidad_list', is_collapse=False, order=13)
    MenuItem.objects.create(parent=tablas, name='Tipo Documento', url_name='tipo_documento_identidad_list', is_collapse=False, order=14)
    MenuItem.objects.create(parent=tablas, name='Tipo IVA', url_name='tipo_iva_list', is_collapse=False, order=15)
    MenuItem.objects.create(parent=tablas, name='Alícuotas IVA', url_name='alicuota_iva_list', is_collapse=False, order=16)
    MenuItem.objects.create(parent=tablas, name='Tipo Percepción', url_name='tipo_percepcion_ib_list', is_collapse=False, order=17)
    MenuItem.objects.create(parent=tablas, name='Tipo Retención', url_name='tipo_retencion_ib_list', is_collapse=False, order=18)
    MenuItem.objects.create(parent=tablas, name='Operario', url_name='operario_list', is_collapse=False, order=19)
    MenuItem.objects.create(parent=tablas, name='Medio de Pago', url_name='medio_pago_list', is_collapse=False, order=20)
    MenuItem.objects.create(parent=tablas, name='Puntos de Venta', url_name='punto_venta_list', is_collapse=False, order=21)
    MenuItem.objects.create(parent=tablas, name='Bancos', url_name='banco_list', is_collapse=False, order=22)
    MenuItem.objects.create(parent=tablas, name='Cuentas de Bancos', url_name='cuenta_banco_list', is_collapse=False, order=23)
    MenuItem.objects.create(parent=tablas, name='Tarjeta', url_name='tarjeta_list', is_collapse=False, order=24)
    MenuItem.objects.create(parent=tablas, name='Códigos de Retención', url_name='codigo_retencion_list', is_collapse=False, order=25)
    MenuItem.objects.create(parent=tablas, name='Conceptos de Bancos', url_name='concepto_banco_list', is_collapse=False, order=26)
    MenuItem.objects.create(parent=tablas, name='Marketins Origen', url_name='marketing_origen_list', is_collapse=False, order=27)
    
    # Ventas > Procesos
    procesos = MenuItem.objects.create(heading=ventas, name='Procesos', icon='fas fa-book-open', is_collapse=True, order=2)
    procesos_ventas = MenuItem.objects.create(parent=procesos, name='Ventas', is_collapse=True, order=1)
    MenuItem.objects.create(parent=procesos_ventas, name='Comprobante Electrónico', url_name='factura_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=procesos_ventas, name='Comprobante Manual', url_name='factura_manual_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=procesos_ventas, name='Recibo', url_name='recibo_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=procesos_ventas, name='Presupuesto', url_name='presupuesto_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=procesos_ventas, name='Movimiento Interno', url_name='movimiento_interno_list', is_collapse=False, order=5)
    
    procesos_compras = MenuItem.objects.create(parent=procesos, name='Compras', is_collapse=True, order=2)
    MenuItem.objects.create(parent=procesos_compras, name='Compra - Remitos', url_name='compra_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=procesos_compras, name='Compra - Retención', url_name='compra_retencion_list', is_collapse=False, order=2)
    
    # Ventas > Informes
    informes = MenuItem.objects.create(heading=ventas, name='Informes', icon='fas fa-book-open', is_collapse=True, order=3)
    informes_catalogos = MenuItem.objects.create(parent=informes, name='Catálogos', is_collapse=True, order=1)
    MenuItem.objects.create(parent=informes_catalogos, name='Clientes', url_name='cliente_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=informes_catalogos, name='Proveedores', url_name='proveedor_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=informes_catalogos, name='Productos', url_name='producto_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=informes_catalogos, name='Vendedores', url_name='vendedor_informe_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=informes_catalogos, name='Empresa', url_name='', is_collapse=False, order=5)  # Sin url en el original
    MenuItem.objects.create(parent=informes_catalogos, name='Sucursales', url_name='sucursal_informe_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=informes_catalogos, name='Parámetros', url_name='', is_collapse=False, order=7)  # Sin url
    MenuItem.objects.create(parent=informes_catalogos, name='Números', url_name='', is_collapse=False, order=8)  # Sin url
    
    informes_tablas = MenuItem.objects.create(parent=informes, name='Tablas', is_collapse=True, order=2)
    MenuItem.objects.create(parent=informes_tablas, name='Actividades', url_name='actividad_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. Depósito', url_name='productodeposito_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. Familia', url_name='productofamilia_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. Marca', url_name='productomarca_informe_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. Modelo', url_name='productomodelo_informe_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. CAI', url_name='productocai_informe_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=informes_tablas, name='Prod. Estado', url_name='productoestado_informe_list', is_collapse=False, order=7)
    MenuItem.objects.create(parent=informes_tablas, name='Comp. Venta', url_name='comprobanteventa_informe_list', is_collapse=False, order=8)
    MenuItem.objects.create(parent=informes_tablas, name='Comp. Compra', url_name='comprobantecompra_informe_list', is_collapse=False, order=9)
    MenuItem.objects.create(parent=informes_tablas, name='Monedas', url_name='moneda_informe_list', is_collapse=False, order=10)
    MenuItem.objects.create(parent=informes_tablas, name='Provincias', url_name='provincia_informe_list', is_collapse=False, order=11)
    MenuItem.objects.create(parent=informes_tablas, name='Localidades', url_name='localidad_informe_list', is_collapse=False, order=12)
    MenuItem.objects.create(parent=informes_tablas, name='Tipos Documento', url_name='tipodocumentoidentidad_informe_list', is_collapse=False, order=13)
    MenuItem.objects.create(parent=informes_tablas, name='Tipos Iva', url_name='tipoiva_informe_list', is_collapse=False, order=14)
    MenuItem.objects.create(parent=informes_tablas, name='Alícuotas Iva', url_name='alicuotaiva_informe_list', is_collapse=False, order=15)
    MenuItem.objects.create(parent=informes_tablas, name='Tipos Percepción', url_name='tipopercepcionib_informe_list', is_collapse=False, order=16)
    MenuItem.objects.create(parent=informes_tablas, name='Tipos Retención', url_name='tiporetencionib_informe_list', is_collapse=False, order=17)
    MenuItem.objects.create(parent=informes_tablas, name='Operarios', url_name='operario_informe_list', is_collapse=False, order=18)
    MenuItem.objects.create(parent=informes_tablas, name='Medios de Pago', url_name='mediopago_informe_list', is_collapse=False, order=19)
    MenuItem.objects.create(parent=informes_tablas, name='Puntos de Venta', url_name='puntoventa_informe_list', is_collapse=False, order=20)
    MenuItem.objects.create(parent=informes_tablas, name='Bancos', url_name='banco_informe_list', is_collapse=False, order=21)
    MenuItem.objects.create(parent=informes_tablas, name='Cuentas de Bancos', url_name='cuentabanco_informe_list', is_collapse=False, order=22)
    MenuItem.objects.create(parent=informes_tablas, name='Tarjetas', url_name='tarjeta_informe_list', is_collapse=False, order=23)
    MenuItem.objects.create(parent=informes_tablas, name='Códigos de Retención', url_name='codigoretencion_informe_list', is_collapse=False, order=24)
    MenuItem.objects.create(parent=informes_tablas, name='Conceptos de Banco', url_name='conceptobanco_informe_list', is_collapse=False, order=25)
    MenuItem.objects.create(parent=informes_tablas, name='Marketing Origen', url_name='marketingorigen_informe_list', is_collapse=False, order=26)
    
    # Informes > Procesos
    informes_procesos = MenuItem.objects.create(parent=informes, name='Procesos', is_collapse=True, order=3)
    MenuItem.objects.create(parent=informes_procesos, name='Saldos de Clientes', url_name='vlsaldosclientes_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=informes_procesos, name='Resumen de Cuenta Corriente', url_name='vlresumenctacte_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=informes_procesos, name='Mercadería por Cliente', url_name='vlmercaderiaporcliente_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=informes_procesos, name='Remitos por Cliente', url_name='vlremitosclientes_informe_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=informes_procesos, name='Totales de Remitos por Cliente', url_name='vltotalremitosclientes_informe_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=informes_procesos, name='Comprobantes de Ventas por Localidad', url_name='vlventacomprolocalidad_informe_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=informes_procesos, name='Ventas por Mostrador', url_name='vlventamostrador_informe_list', is_collapse=False, order=7)
    MenuItem.objects.create(parent=informes_procesos, name='Total de Ventas por Comprobantes', url_name='vlventacompro_informe_list', is_collapse=False, order=8)
    MenuItem.objects.create(parent=informes_procesos, name='Comprobantes Vencidos', url_name='vlcomprobantesvencidos_informe_list', is_collapse=False, order=9)
    MenuItem.objects.create(parent=informes_procesos, name='Remitos Pendientes', url_name='vlremitospendientes_informe_list', is_collapse=False, order=10)
    MenuItem.objects.create(parent=informes_procesos, name='Remitos por Vendedor', url_name='vlremitosvendedor_informe_list', is_collapse=False, order=11)
    
    iva_ventas = MenuItem.objects.create(parent=informes_procesos, name='Libro I.V.A. Ventas', is_collapse=True, order=12)
    MenuItem.objects.create(parent=iva_ventas, name='Detalle', url_name='vlivaventasfull_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=iva_ventas, name='Totales por Provincia', url_name='vlivaventasprovincias_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=iva_ventas, name='Totales para SITRIB', url_name='vlivaventassitrib_informe_list', is_collapse=False, order=3)
    
    percep_vendedor = MenuItem.objects.create(parent=informes_procesos, name='Percepciones por Vendedor', is_collapse=True, order=13)
    MenuItem.objects.create(parent=percep_vendedor, name='Vendedores - Solo Totales', url_name='vlpercepibvendedortotales_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=percep_vendedor, name='Vendedores - Detallado por Comprobantes', url_name='vlpercepibvendedordetallado_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=percep_vendedor, name='Sub Cuentas - Solo Totales', url_name='vlpercepibsubcuentatotales_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=percep_vendedor, name='Sub Cuentas - Detallado por Comprobantes', url_name='vlpercepibsubcuentadetallado_informe_list', is_collapse=False, order=4)
    
    MenuItem.objects.create(parent=informes_procesos, name='Comisiones a Vendedores según Facturas', url_name='vlcomisionvendedor_informe_list', is_collapse=False, order=14)
    MenuItem.objects.create(parent=informes_procesos, name='Comisiones a Operarios', url_name='vlcomisionoperario_informe_list', is_collapse=False, order=15)
    MenuItem.objects.create(parent=informes_procesos, name='Diferencias de Precios en Facturación', url_name='vlpreciodiferente_informe_list', is_collapse=False, order=16)
    MenuItem.objects.create(parent=informes_procesos, name='Resumen de Ventas I. Brutos Mercadolibre', url_name='vlventasresumenib_informe_list', is_collapse=False, order=17)
    
    stock = MenuItem.objects.create(parent=informes_procesos, name='Stock', is_collapse=True, order=18)
    MenuItem.objects.create(parent=stock, name='Lista de Precios', url_name='vllista_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=stock, name='Lista de Precios a Revendedores', url_name='vllistarevendedor_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=stock, name='Listado de Stock por Sucursal', url_name='vlstocksucursal_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=stock, name='Stock General por Sucursal', url_name='vlstockgeneralsucursal_informe_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=stock, name='Listado de Stock Único', url_name='vlstockunico_informe_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=stock, name='Reposición de Stock', url_name='vlreposicionstock_informe_list', is_collapse=False, order=6)
    
    # Ventas > Opciones
    opciones = MenuItem.objects.create(heading=ventas, name='Opciones', icon='fas fa-book-open', is_collapse=True, order=4)
    MenuItem.objects.create(parent=opciones, name='Actualizar Productos (Excel)', url_name='cargar_excel', query_params='?proceso=actualizar', is_collapse=False, order=1)
    MenuItem.objects.create(parent=opciones, name='Agregar nuevos Productos (Excel)', url_name='cargar_excel', query_params='?proceso=agregar', is_collapse=False, order=2)
    
    # Estadísticas > Ventas
    estadisticas_ventas = MenuItem.objects.create(heading=estadisticas, name='Ventas', icon='fas fa-book-open', is_collapse=True, order=1)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas', url_name='vlestadisticasventas_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas Vendedores', url_name='vlestadisticasventasvendedor_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas Vendedores Clientes', url_name='vlestadisticasventasvendedorcliente_informe_list', is_collapse=False, order=3)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Ventas de Productos Según Condición', url_name='vlestadisticasseguncondicion_informe_list', is_collapse=False, order=4)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas por Marca', url_name='vlestadisticasventasmarca_informe_list', is_collapse=False, order=5)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas por Marca-Vendedor', url_name='vlestadisticasventasmarcavendedor_informe_list', is_collapse=False, order=6)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Clientes sin Movimiento', url_name='vlclienteultimaventa_informe_list', is_collapse=False, order=7)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Estadísticas de Ventas por Provincia', url_name='vlestadisticasventasprovincia_informe_list', is_collapse=False, order=8)
    MenuItem.objects.create(parent=estadisticas_ventas, name='Comprobantes sin Estadísticas', url_name='vlventasinestadistica_informe_list', is_collapse=False, order=9)
    
    tabla_dinamica = MenuItem.objects.create(parent=estadisticas_ventas, name='Tablas Dinámicas de Ventas', is_collapse=True, order=10)
    MenuItem.objects.create(parent=tabla_dinamica, name='Ventas por Comprobantes', url_name='vltabladinamicaventas_informe_list', is_collapse=False, order=1)
    MenuItem.objects.create(parent=tabla_dinamica, name='Detalle de Ventas por Productos', url_name='vltabladinamicadetalleventas_informe_list', is_collapse=False, order=2)
    MenuItem.objects.create(parent=tabla_dinamica, name='Tablas para Estadísticas', url_name='vltabladinamicaestadistica_informe_list', is_collapse=False, order=3)

class Migration(migrations.Migration):
    dependencies = [('menu', '0001_initial')]
    operations = [migrations.RunPython(create_menu)]