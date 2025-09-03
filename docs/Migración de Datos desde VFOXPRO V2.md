# Migración de Datos desde VFOXPRO

## 1. Renombrar o Eliminar la base de datos de la carpeta

\neumatic\data\db_neumatic.db

## 2. Eliminar los archivos de migraciones

Eliminar los archivos de migraciones de las carpetas migrations de todas la aplicaciones, para ello ubíquese desde la ventana terminal en la carpeta neumatic\data_load y ejecute:

python 00_limpiar_migraciones.py

## 3. Aplicar las migraciones

```shell
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic> python manage.py makemigrations
Migrations for 'informes':
 apps\informes\migrations\0001_initial.py  
 + Create model VLClienteUltimaVenta  
 + Create model VLComisionOperario
 + Create model VLComisionVendedor
 + Create model VLComprobantesVencidos  
 + Create model VLEstadisticasSegunCondicion
 + Create model VLEstadisticasVentas  
 + Create model VLEstadisticasVentasMarca  
 + Create model VLEstadisticasVentasMarcaVendedor
 + Create model VLEstadisticasVentasProvincia
 + Create model VLEstadisticasVentasVendedor
 + Create model VLEstadisticasVentasVendedorCliente
 + Create model VLIVAVentasFULL
 + Create model VLIVAVentasProvincias
 + Create model VLIVAVentasSitrib
 + Create model VLMercaderiaPorCliente
 + Create model VLPercepIBSubcuentaDetallado
 + Create model VLPercepIBSubcuentaTotales
 + Create model VLPercepIBVendedorDetallado
 + Create model VLPercepIBVendedorTotales
 + Create model VLPrecioDiferente
 + Create model VLRemitosClientes
 + Create model VLRemitosPendientes
 + Create model VLRemitosVendedor
 + Create model VLResumenCtaCte
 + Create model VLSaldosClientes
 + Create model VLTablaDinamicaDetalleVentas
 + Create model VLTablaDinamicaEstadistica
 + Create model VLTablaDinamicaVentas
 + Create model VLTotalRemitosClientes
 + Create model VLVentaCompro
 + Create model VLVentaComproLocalidad
 + Create model VLVentaMostrador
 + Create model VLVentaSinEstadistica
 + Create model VLVentasResumenIB
Migrations for 'maestros':
 apps\maestros\migrations\0001_initial.py
 + Create model Actividad
 + Create model AlicuotaIva
 + Create model Banco
 + Create model Cliente
 + Create model CodigoRetencion
 + Create model ComprobanteCompra
 + Create model ComprobanteVenta
 + Create model ConceptoBanco
 + Create model CuentaBanco
 + Create model DescuentoVendedor
 + Create model DetalleVendedorComision
 + Create model Empresa
 + Create model Leyenda
 + Create model Localidad
 + Create model MarketingOrigen
 + Create model MedioPago
 + Create model Moneda
 + Create model Numero
 + Create model Operario
 + Create model Parametro
 + Create model Producto
 + Create model ProductoCai
 + Create model ProductoDeposito
 + Create model ProductoEstado
 + Create model ProductoFamilia
 + Create model ProductoMarca
 + Create model ProductoMinimo
 + Create model ProductoModelo
 + Create model ProductoStock
 + Create model Proveedor
 + Create model Provincia
 + Create model PuntoVenta
 + Create model Sucursal
 + Create model Tarjeta
 + Create model TipoDocumentoIdentidad
 + Create model TipoIva
 + Create model TipoPercepcionIb
 + Create model TipoRetencionIb
 + Create model Valida
 + Create model Vendedor
 + Create model VendedorComision
 apps\maestros\migrations\0002_initial.py
 + Add field id_user to actividad
 + Add field id_user to alicuotaiva
 + Add field id_user to banco
 + Add field id_actividad to cliente
 + Add field id_user to cliente
 + Add field id_user to codigoretencion
 + Add field id_user to comprobantecompra
 + Add field id_user to comprobanteventa
 + Add field id_user to conceptobanco
 + Add field id_banco to cuentabanco
 + Add field id_user to cuentabanco
 + Add field id_user to descuentovendedor
 + Add field id_user to detallevendedorcomision
 + Add field id_user to empresa
 + Add field id_user to leyenda
 + Add field id_user to localidad
 + Add field id_localidad to empresa
 + Add field id_localidad to cliente
 + Add field id_user to marketingorigen
 + Add field id_user to mediopago
 + Add field id_user to moneda
 + Add field id_moneda to cuentabanco
 + Add field id_user to numero
 + Add field id_user to operario
 + Add field id_empresa to parametro
 + Add field id_user to parametro
 + Add field id_alicuota_iva to producto
 + Add field id_user to producto
 + Add field id_user to productocai
 + Add field id_cai to producto
 + Add field id_user to productodeposito
 + Add field id_user to productoestado
 + Add field id_user to productofamilia
 + Add field id_familia to producto
 + Add field id_familia to detallevendedorcomision
 + Add field id_familia to descuentovendedor
 + Add field id_moneda to productomarca
 + Add field id_user to productomarca
 + Add field id_marca to producto
 + Add field id_marca to detallevendedorcomision
 + Add field id_marca to descuentovendedor
 + Add field id_cai to productominimo
 + Add field id_deposito to productominimo
 + Add field id_user to productominimo
 + Add field id_user to productomodelo
 + Add field id_modelo to producto
 + Add field id_deposito to productostock
 + Add field id_producto to productostock
 + Add field id_user to productostock
 + Add field id_localidad to proveedor
 + Add field id_user to proveedor
 + Add field id_proveedor to cuentabanco
 + Add field id_user to provincia
 + Add field id_provincia to proveedor
 + Add field id_provincia to localidad
 + Add field id_provincia to empresa
 + Add field id_provincia to cliente
 + Add field id_user to puntoventa
 + Add field id_punto_venta to numero
 + Add field id_localidad to sucursal
 + Add field id_provincia to sucursal
 + Add field id_user to sucursal
 + Add field id_sucursal to puntoventa
 + Add field id_sucursal to productodeposito
 + Add field id_sucursal to numero
 + Add field id_sucursal to cliente
 + Add field id_user to tarjeta
 + Add field id_user to tipodocumentoidentidad
 + Add field id_tipo_documento_identidad to cliente
 + Add field id_user to tipoiva
 + Add field id_tipo_iva to proveedor
 + Add field id_iva to empresa
 + Add field id_tipo_iva to cliente
 + Add field id_user to tipopercepcionib
 + Add field id_percepcion_ib to cliente
 + Add field id_user to tiporetencionib
 + Add field id_tipo_retencion_ib to proveedor
 + Add field id_cliente to valida
 + Add field id_sucursal to valida
 + Add field id_user to valida
 + Add field id_sucursal to vendedor
 + Add field id_user to vendedor
 + Add field id_vendedor to cliente
 + Add field id_user to vendedorcomision
 + Add field id_vendedor to vendedorcomision
 + Add field id_vendedor_comision to detallevendedorcomision
Migrations for 'usuarios':
 apps\usuarios\migrations\0001_initial.py
 + Create model User
Migrations for 'ventas':
 apps\ventas\migrations\0001_initial.py
 + Create model Factura
 + Create model DetalleRecibo
 + Create model DetalleFactura
 + Create model DepositoRecibo
 + Create model ChequeRecibo
 + Create model RetencionRecibo
 + Create model SerialFactura
 + Create model TarjetaRecibo
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic>
```

```shell
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic> python manage.py migrate  
Operations to perform:
 Apply all migrations: admin, auth, contenttypes, informes, maestros, sessions, usuarios, ventas
Running migrations:
 Applying maestros.0001_initial... OK
 Applying contenttypes.0001_initial... OK
 Applying contenttypes.0002_remove_content_type_name... OK
 Applying auth.0001_initial... OK
 Applying auth.0002_alter_permission_name_max_length... OK
 Applying auth.0003_alter_user_email_max_length... OK
 Applying auth.0004_alter_user_username_opts... OK
 Applying auth.0005_alter_user_last_login_null... OK
 Applying auth.0006_require_contenttypes_0002... OK
 Applying auth.0007_alter_validators_add_error_messages... OK
 Applying auth.0008_alter_user_username_max_length... OK
 Applying auth.0009_alter_user_last_name_max_length... OK
 Applying auth.0010_alter_group_name_max_length... OK
 Applying auth.0011_update_proxy_permissions... OK
 Applying auth.0012_alter_user_first_name_max_length... OK
 Applying usuarios.0001_initial... OK
 Applying admin.0001_initial... OK
 Applying admin.0002_logentry_remove_auto_add... OK
 Applying admin.0003_logentry_add_action_flag_choices... OK
 Applying informes.0001_initial... OK
 Applying maestros.0002_initial... OK
 Applying sessions.0001_initial... OK
 Applying ventas.0001_initial... OK
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic>
```

No debe existir ningún problema en el proceso de migración.

## 4. Crear el superuasuario

```shell
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic> python manage.py createsuperuser
Nombre de usuario: admin
Correo electrónico: ramosric1410@gmail.com
Password: 
Password (again): 
Superuser created successfully.
(venv) PS D:\PROJECT_NEUMATIC_MIGRA\neumatic>
```

Para la fase de desarrollo, utilice

> Nombre de usuario: admin
> 
> Correo electrónico: SU CORREO PERSONAL
> 
> Password : admin54321$$

## 

## 5. Ejecutar la secuencia de los archivos generales de migración:

Ubíquese desde la ventana terminal en la carpeta neumatic\data_load y ejecute:

python 01_migra_base.py  
python 02_migra_producto.py  
python 03_migra_cliente.py  
python 04_migra_factura.py  
python 05_migra_recibo.py

**Al finalizar las migraciones:**

1. Ejecute la actualización del superusuario (OBLIGATORIO)
   
   **actualiza_user.py** 

2. Crear las vistas en la base de datos
   
   2.1. Abrir la base de datos en DB Browser
   
   2.2. Copiar todo el contenido del script: crear_vista_sql.sql
   
   2.3. Ir a la pestaña Execute SQL y pagar todo el contendo
   
   2.4. Ejecutar todo el contenido
   
   2.5. Grabar los cambios y salir de DB Browser

3. Entrar al sistema e ir a comprobantes de venta
   
   3.1. Asignar los documentos relacionados a Facturas Remito
   
   3.2. Marcar los Recibos y Remitos el checkbox y grupo correspondiente
