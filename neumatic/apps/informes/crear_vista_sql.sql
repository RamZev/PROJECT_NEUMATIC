DROP VIEW IF EXISTS "main"."A";
CREATE VIEW A AS SELECT "prueba";
-- ---------------------------------------------------------------------------
--  Saldos Clientes.
--  Modelo: VLSaldosClientes
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLSaldosClientes";
CREATE VIEW "VLSaldosClientes" AS 
	SELECT 
		f.id_cliente_id, 
		f.fecha_comprobante, 
		f.fecha_pago, 
		c.nombre_cliente, 
		c.domicilio_cliente, 
		l.nombre_localidad,
		c.codigo_postal, 
		c.telefono_cliente, 
		c.sub_cuenta, 
		c.id_vendedor_id, 
		f.total, 
		f.entrega, 
		f.condicion_comprobante,
		cv.mult_saldo
	FROM factura f 
		JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta 
		JOIN localidad l ON c.id_localidad_id = l.id_localidad
	WHERE 
		f.condicion_comprobante = 2 AND 
		cv.mult_saldo <> 0;

-- ---------------------------------------------------------------------------
-- Resumen Cuenta Corriente.
-- Modelo: VLResumenCtaCte
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLResumenCtaCte";
CREATE VIEW "VLResumenCtaCte" AS 
	SELECT 
		f.id_cliente_id, 
		c.nombre_cliente AS razon_social, 
		cv.nombre_comprobante_venta, 
		f.letra_comprobante, 
		f.numero_comprobante, 
		(f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS numero, 
		f.fecha_comprobante, 
		f.remito,
		f.condicion_comprobante, 
		CASE 
			WHEN f.condicion_comprobante = 1 THEN 'Contado'
			WHEN f.condicion_comprobante = 2 THEN 'Cta. Cte.'
			ELSE 'Desconocido'
		END AS condicion,
		f.total * cv.mult_saldo AS total, 
		f.entrega * cv.mult_saldo AS entrega, 
		0 AS intereses
	FROM factura f 
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE cv.mult_saldo <> 0;

-- ---------------------------------------------------------------------------
-- Mercadería por Cliente.
-- Modelo: VLMercaderiaPorCliente
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLMercaderiaPorCliente";
CREATE VIEW "VLMercaderiaPorCliente" AS 
	SELECT 
	   f.id_cliente_id, 
	   cv.nombre_comprobante_venta, 
	   f.letra_comprobante, 
	   f.numero_comprobante,
	   (f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS numero, 
	   f.fecha_comprobante, 
	   COALESCE(m.nombre_producto_marca, '') AS nombre_producto_marca, 
	   COALESCE(p.medida, '') AS medida, 
	   df.id_producto_id, 
	   COALESCE(p.nombre_producto, '') AS nombre_producto, 
	   CAST(COALESCE(df.cantidad, 0.0) AS DECIMAL) AS cantidad, 
	   CAST(COALESCE(df.precio, 0.0) AS DECIMAL) AS precio, 
	   CAST(COALESCE(df.descuento, 0.0) AS DECIMAL) AS descuento, 
	   CAST(COALESCE(df.total, 0.0) AS DECIMAL) AS total
	FROM detalle_factura df JOIN factura f ON df.id_factura_id = f.id_factura 
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto 
		JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca;

-- ---------------------------------------------------------------------------
-- Remitos por Clientes.
-- Modelo: VLRemitosClientes
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLRemitosClientes";
CREATE VIEW "VLRemitosClientes" AS
	SELECT 
		f.id_cliente_id, 
		cv.codigo_comprobante_venta, 
		cv.nombre_comprobante_venta, 
		f.fecha_comprobante, 
		f.letra_comprobante, 
		f.numero_comprobante, 
		(f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS numero, 
		p.nombre_producto, 
		p.medida, 
		CAST(COALESCE(df.cantidad, 0.0) AS DECIMAL) AS cantidad, 
		CAST(COALESCE(df.precio, 0.0) AS DECIMAL) AS precio, 
		CAST(COALESCE(df.descuento, 0.0) AS DECIMAL) AS descuento, 
		CAST(COALESCE(df.total, 0.0) AS DECIMAL) * CAST(COALESCE(cv.mult_stock, 0.0) AS DECIMAL) * -1 AS total
	FROM detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto
	WHERE
		cv.mult_venta = 0
	ORDER BY
		f.fecha_comprobante, f.numero_comprobante;

-- ---------------------------------------------------------------------------
-- Total Remitos por Clientes.
-- Modelo: VLTotalRemitosClientes
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLTotalRemitosClientes";
CREATE VIEW "VLTotalRemitosClientes" AS 
	SELECT 
		f.id_cliente_id, 
		f.fecha_comprobante, 
		c.nombre_cliente, 
		c.domicilio_cliente, 
		c.codigo_postal, 
		ti.nombre_iva, 
		c.cuit, 
		c.telefono_cliente, 
		(f.total * cv.mult_stock * -1) AS total
	FROM factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
	WHERE cv.mult_saldo = 0
	ORDER BY c.nombre_cliente;

-- ---------------------------------------------------------------------------
-- Ventas por Localidad.
-- Modelo: VLVentaComproLocalidad
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLVentaComproLocalidad";
CREATE VIEW "VLVentaComproLocalidad" AS 
	SELECT 
		f.id_cliente_id,
		f.id_sucursal_id,
		f.fecha_comprobante,
		c.nombre_cliente,
		c.cuit,
		c.codigo_postal,
		cv.nombre_comprobante_venta,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(cv.codigo_comprobante_venta || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante, 
		CAST(COALESCE(f.gravado, 0.0) AS DECIMAL) AS gravado,
		CAST(COALESCE(f.exento, 0.0) AS DECIMAL) AS exento,
		CAST(COALESCE(f.iva, 0.0) AS DECIMAL) AS iva,
		CAST(COALESCE(f.percep_ib, 0.0) AS DECIMAL) AS percep_ib,
		CAST(COALESCE(f.total, 0.0) AS DECIMAL) AS total,
		u.iniciales
	FROM factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN usuarios_user u ON f.id_user_id = u.id
	WHERE cv.mult_venta <> 0
	ORDER BY f.fecha_comprobante;

-- ---------------------------------------------------------------------------
-- Ventas por Mostrador.
-- Modelo: VLVentaMostrador
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLVentaMostrador";
CREATE VIEW "VLVentaMostrador" AS 
	SELECT 
		df.id_detalle_factura,
		cv.nombre_comprobante_venta,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(cv.codigo_comprobante_venta || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.mayorista,
		df.reventa,
		df.id_producto_id,
		p.nombre_producto,
		p.tipo_producto,
		(df.reventa || " " || p.tipo_producto) AS rv_tp,
		df.cantidad,
		df.precio,
		df.total*cv.mult_venta AS Total,
		f.id_sucursal_id
	FROM detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto
	WHERE cv.mult_venta <> 0 AND f.no_estadist <> True
	ORDER BY f.fecha_comprobante, f.numero_comprobante;

-- ---------------------------------------------------------------------------
-- Ventas por Comprobantes.
-- Modelo: VLVentaCompro
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLVentaCompro";
CREATE VIEW "VLVentaCompro" AS 
	SELECT 
		f.id_factura,
		cv.nombre_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(cv.codigo_comprobante_venta || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		f.condicion_comprobante,
		CASE 
			WHEN f.condicion_comprobante = 1 THEN 'Contado'
			WHEN f.condicion_comprobante = 2 THEN 'Cta. Cte.'
		END AS condicion,
		f.id_cliente_id,
		c.nombre_cliente,
		f.gravado*cv.mult_venta as gravado,
		f.iva*cv.mult_venta AS IVA,
		f.percep_ib*cv.mult_venta AS percep_ib,
		f.total*cv.mult_venta AS total,
		f.id_sucursal_id
	FROM factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
	ORDER BY nombre_comprobante_venta, letra_comprobante, numero_comprobante;

-- ---------------------------------------------------------------------------
-- Comprobantes Vencidos.
-- Modelo: VLComprobantesVencidos
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLComprobantesVencidos";
CREATE VIEW "VLComprobantesVencidos" AS 
	SELECT 
		f.id_factura,
		f.fecha_comprobante,
		CAST(JULIANDAY(DATE('now')) - JULIANDAY(f.fecha_comprobante) AS INTEGER) AS dias_vencidos,
		f.compro AS codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		CAST(f.total AS NUMERIC)* 1.0 AS total,
		CAST(f.entrega AS NUMERIC)* 1.0 AS entrega,
		ROUND(CAST(f.total - f.entrega AS NUMERIC), 2) * 1.0 AS saldo,
		f.id_vendedor_id,
		f.id_sucursal_id
	FROM factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE f.estado = ""
	ORDER by f.fecha_comprobante;

-- ---------------------------------------------------------------------------
-- Remitos Pendientes.
-- Modelo: VLRemitosPendientes
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLRemitosPendientes";
CREATE VIEW "VLRemitosPendientes" AS 
	SELECT 
		f.id_factura,
		f.id_cliente_id,
		c.nombre_cliente,
		cv.nombre_comprobante_venta,
		f.fecha_comprobante,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		df.id_producto_id,
		p.nombre_producto,
		p.medida,
		df.cantidad,
		df.precio,
		df.descuento,
		df.total*cv.mult_stock*-1 AS total,
		f.id_vendedor_id,
		f.id_sucursal_id AS id_sucursal_fac,
		c.id_sucursal_id AS id_sucursal_cli
	FROM detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE cv.mult_venta = 0 AND f.estado = ""
	ORDER BY c.nombre_cliente, f.fecha_comprobante, f.numero_comprobante;

-- ---------------------------------------------------------------------------
-- Remitos Vendedor.
-- Modelo: VLRemitosVendedor
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLRemitosVendedor";
CREATE VIEW "VLRemitosVendedor" AS 
	SELECT 
		f.id_factura,
		f.id_cliente_id,
		c.nombre_cliente,
		cv.nombre_comprobante_venta,
		f.fecha_comprobante,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		df.id_producto_id,
		p.nombre_producto,
		p.medida,
		df.cantidad,
		df.precio,
		df.descuento,
		df.total*cv.mult_stock*-1 AS total,
		f.id_vendedor_id
	FROM detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE cv.mult_venta = 0
	ORDER BY c.nombre_cliente, f.fecha_comprobante, f.numero_comprobante;

-- ---------------------------------------------------------------------------
-- Libro I.V.A. Ventas - Detalle.
-- Modelo: VLIVAVentasFULL
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLIVAVentasFULL";
CREATE VIEW "VLIVAVentasFULL" AS 
	SELECT 
		f.id_factura,
		cv.nombre_comprobante_venta,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		c.nombre_cliente,
		c.cuit,
		ti.codigo_iva,
		ROUND(f.gravado*cv.mult_venta, 2) * 1.0 AS gravado,
		ROUND(f.exento*cv.mult_venta, 2) * 1.0 AS exento,
		ROUND(f.iva*cv.mult_venta, 2) * 1.0 AS iva,
		ROUND(f.percep_ib*cv.mult_venta, 2) * 1.0 AS percep_ib,
		ROUND(f.total*cv.mult_venta, 2) * 1.0 AS total,
		f.id_sucursal_id
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
	WHERE cv.libro_iva
	ORDER by f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Libro I.V.A. Ventas - Totales por Provincias.
-- Modelo: VLIVAVentasProvincias
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLIVAVentasProvincias";
CREATE VIEW "VLIVAVentasProvincias" AS 
	SELECT 
		f.id_factura,
		p.id_provincia,
		p.nombre_provincia,
		f.fecha_comprobante,
		ROUND(f.gravado*cv.mult_venta * 1.0, 2) AS gravado,
		ROUND(f.exento*cv.mult_venta * 1.0, 2)  AS exento,
		ROUND(f.iva*cv.mult_venta * 1.0, 2)  AS iva,
		ROUND(f.percep_ib*cv.mult_venta * 1.0, 2)  AS percep_ib,
		ROUND(f.total*cv.mult_venta * 1.0, 2)  AS total,
		f.id_sucursal_id AS id_sucursal_id
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN localidad l ON c.id_localidad_id = l.id_localidad
		INNER JOIN provincia p ON l.id_provincia_id = p.id_provincia
	WHERE cv.libro_iva
	ORDER by p.nombre_provincia;


-- ---------------------------------------------------------------------------
-- Libro I.V.A. Ventas - Totales para SITRIB.
-- Modelo: VLIVAVentasProvincias
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLIVAVentasSitrib";
CREATE VIEW "VLIVAVentasSitrib" AS 
	SELECT 
		f.id_factura,
		f.fecha_comprobante,
		ti.codigo_iva,
		ti.nombre_iva,
		ROUND(f.gravado*cv.mult_venta * 1.0, 2) AS gravado, 
		ROUND(f.exento*cv.mult_venta * 1.0, 2) AS exento, 
		ROUND(f.iva*cv.mult_venta * 1.0, 2) AS iva, 
		ROUND(f.percep_ib*cv.mult_venta * 1.0, 2) AS percep_ib, 
		ROUND(f.total*cv.mult_venta * 1.0, 2) AS total,
		f.id_sucursal_id
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
		INNER JOIN localidad l ON c.id_localidad_id = l.id_localidad
		INNER JOIN provincia p ON l.id_provincia_id = p.id_provincia
	WHERE cv.libro_iva
	ORDER by ti.codigo_iva;


-- ---------------------------------------------------------------------------
-- Percepciones por Vendedor - Totales.
-- Modelo: VLPercepIBVendedorTotales
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLPercepIBVendedorTotales";
CREATE VIEW "VLPercepIBVendedorTotales" AS 
	SELECT 
		f.id_factura,
		c.id_vendedor_id,
		v.nombre_vendedor,
		f.fecha_comprobante,
		ROUND(f.gravado*cv.mult_venta * 1.0, 2) AS neto,
		ROUND(f.percep_ib*cv.mult_venta * 1.0, 2) AS percep_ib
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		INNER JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE f.percep_ib<>0 AND cv.mult_venta<>0
	ORDER BY c.id_vendedor_id;


-- ---------------------------------------------------------------------------
-- Percepciones por Vendedor - Detallado.
-- Modelo: VLPercepIBVendedorDetallado
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLPercepIBVendedorDetallado";
CREATE VIEW VLPercepIBVendedorDetallado AS
	SELECT 
		f.id_factura,
		c.id_vendedor_id,
		v.nombre_vendedor,
		cv.nombre_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		f.fecha_comprobante,
		--(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5) || "   " || substr(f.fecha_comprobante, 9, 2) || '/' || substr(f.fecha_comprobante, 6, 2) || '/' || substr(f.fecha_comprobante, 1, 4)) AS comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.cuit,
		f.gravado*cv.mult_venta AS neto,
		f.percep_ib*cv.mult_venta AS percep_ib,
		f.no_estadist
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		INNER JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE f.percep_ib<>0 AND cv.mult_venta<>0
	ORDER BY v.nombre_vendedor, f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Percepciones por Sub Cuenta - Totales.
-- Modelo: VLPercepIBSubcuentaTotales
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLPercepIBSubcuentaTotales";
CREATE VIEW "VLPercepIBSubcuentaTotales" AS 
	SELECT 
		f.id_factura,
		f.fecha_comprobante,
		c.sub_cuenta,
		p.nombre_cliente AS nombre_cliente_padre,
		f.id_cliente_id,
		c.nombre_cliente,
		ROUND(f.gravado * cv.mult_venta * 1.0, 2) AS neto,
		ROUND(f.percep_ib * cv.mult_venta * 1.0, 2) AS percep_ib
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		LEFT JOIN cliente p ON c.sub_cuenta = p.id_cliente 
	WHERE f.percep_ib <> 0 AND cv.mult_venta <> 0 
	ORDER BY c.sub_cuenta;


-- ---------------------------------------------------------------------------
-- Percepciones por Sub Cuenta - Detallado.
-- Modelo: VLPercepIBSubcuentaDetallado
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLPercepIBSubcuentaDetallado";
CREATE VIEW "VLPercepIBSubcuentaDetallado" AS 
	SELECT 
		f.id_factura,
		c.sub_cuenta,
		p.nombre_cliente AS nombre_cliente_padre,
		f.compro,
		f.letra_comprobante,
		f.numero_comprobante,
		f.fecha_comprobante,
		--(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5) || "   " || substr(f.fecha_comprobante, 9, 2) || '/' || substr(f.fecha_comprobante, 6, 2) || '/' || substr(f.fecha_comprobante, 1, 4)) AS comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.cuit,
		f.gravado*cv.mult_venta AS neto,
		f.percep_ib*cv.mult_venta AS percep_ib,
		f.no_estadist
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		LEFT JOIN cliente p ON c.sub_cuenta = p.id_cliente
	WHERE f.percep_ib<>0 AND cv.mult_venta<>0
	GROUP BY c.sub_cuenta, f.numero_comprobante
	ORDER BY c.sub_cuenta, f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Comisiones a Operarios.
-- Modelo: VLComisionOperario
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLComisionOperario";
CREATE VIEW "VLComisionOperario" AS 
	SELECT 
		f.id_factura,
		df.id_operario_id,
		o.nombre_operario,
		f.compro,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		df.id_producto_id,
		pf.nombre_producto_familia,
		p.nombre_producto,
		(df.total*cv.mult_estadistica) * 1.0 AS total,
		(pf.comision_operario) * 1.0 AS comision_operario,
		(((df.total*cv.mult_estadistica) * pf.comision_operario / 100)) * 1.0 AS monto_comision
	FROM
		detalle_factura df
			INNER JOIN factura f ON df.id_factura_id = f.id_factura
			INNER JOIN operario o ON df.id_operario_id = o.id_operario
			INNER JOIN producto p ON df.id_producto_id = p.id_producto
			INNER JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
			INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE 
		pf.comision_operario <> 0 AND
		cv.mult_estadistica <> 0
	ORDER BY o.nombre_operario, f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Diferencias de Precios en Facturación.
-- Modelo: VLPrecioDiferente
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLPrecioDiferente";
CREATE VIEW "VLPrecioDiferente" AS 
	SELECT 
		f.id_factura,
		f.compro,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		df.id_producto_id,
		p.nombre_producto,
		df.cantidad,
		df.precio,
		df.precio_lista,
		(df.precio - df.precio_lista) * 1.0 AS diferencia,
		df.descuento,
		round(p.precio*p.descuento/100,2) AS adicional,
		c.id_vendedor_id,
		v.nombre_vendedor
	FROM detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE 
		f.no_estadist = False AND df.precio <> df.precio_lista
	ORDER BY
		v.nombre_vendedor, f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Resumen de Ventas Ing. Brutos Mercadolibre.
-- Modelo: VLVentasResumenIB
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLVentasResumenIB";
CREATE VIEW "VLVentasResumenIB" AS 
	SELECT 
		f.id_factura,
		f.fecha_comprobante,
		f.gravado*cv.mult_venta AS gravado,
		f.iva*cv.mult_venta AS iva,
		f.total*cv.mult_venta AS total,
		c.id_provincia_id,
		p.nombre_provincia,
		f.suc_imp
	FROM factura f
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN provincia p ON c.id_provincia_id = p.id_provincia
	WHERE
		cv.libro_iva = True;


-- ---------------------------------------------------------------------------
-- Comisiones a Vendedores según Facturas.
-- Modelo: VLComisionVendedor
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLComisionVendedor";
CREATE VIEW "VLComisionVendedor" AS 
	SELECT 
		f.id_factura,
		f.compro,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		--f.id_cliente_id,
		c.nombre_cliente,
		--"R" AS reventa,
		"" AS reventa,
		--"id_producto_id" AS id_producto_id,
		"" AS id_producto_id,
		--"medida" AS medida,
		"" AS medida,
		--"nombre_producto_marca" AS nombre_producto_marca,
		"" AS nombre_producto_marca,
		--"nombre_producto_familia" AS nombre_producto_familia,
		"" AS nombre_producto_familia,
		ROUND(f.total/(((SELECT alicuota_iva FROM codigo_alicuota WHERE codigo_alicuota = "0005")/100.0)+1),2) AS gravado,
--		f.total,
		CASE
			WHEN f.comision = "C" THEN v.pje_camion
			ELSE v.pje_auto
		END AS pje_comision,
--		v.pje_auto, 
--		v.pje_camion,
--		f.comision AS tipo_comision,
--		CASE
--			WHEN f.comision = "C" THEN ROUND(f.total/(((SELECT alicuota_iva FROM codigo_alicuota WHERE codigo_alicuota = "0005")/100.0)+1),2) * v.pje_camion/100.0
--			ELSE ROUND(f.total/(((SELECT alicuota_iva FROM codigo_alicuota WHERE codigo_alicuota = "0005")/100.0)+1),2) * v.pje_auto/100.0
--		END AS monto_comision,
		c.id_vendedor_id,
		v.nombre_vendedor,
		"R" AS consulta
	FROM factura f
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE
		(f.compro = 'RC' OR f.compro = 'RB' OR f.compro = 'RE');
	--ORDER BY
	--	v.nombre_vendedor, f.fecha_comprobante, f.numero_comprobante;


-- ---------------------------------------------------------------------------
-- Comisiones a Vendedores según Facturas (Detalle).
-- Modelo: VLComisionVendedor
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLComisionVendedorDetalle";
CREATE VIEW "VLComisionVendedorDetalle" AS 
	SELECT 
		f.id_factura,
		f.compro,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		--f.id_cliente_id,
		c.nombre_cliente,
		df.reventa,
		df.id_producto_id,
		p.medida,
		--p.id_marca_id,
		pm.nombre_producto_marca,
		--p.id_familia_id,
		pf.nombre_producto_familia,
		--df.cantidad,
		--df.precio,
		--df.costo,
		--df.descuento,
		df.gravado*cv.mult_comision AS gravado,
		--df.total*comprobante_venta.mult_comision AS total,
		--f.no_estadist,
		--df.alic_iva*0 AS pje_auto,
		COALESCE(ROUND((SELECT 
				dvc.comision_porcentaje
			FROM vendedor_comision vc
				JOIN detalle_vendedor_comision dvc ON dvc.id_vendedor_comision_id = vc.id_vendedor_comision
				--JOIN vendedor v ON vc.id_vendedor_id = v.id_vendedor
				--JOIN producto_familia f ON dvc.id_familia_id = f.id_producto_familia
				--JOIN producto_marca m ON dvc.id_marca_id = m.id_producto_marca
			WHERE vc.id_vendedor_id = c.id_vendedor_id
				AND dvc.id_familia_id = p.id_familia_id
				AND dvc.id_marca_id = p.id_marca_id
			LIMIT 1), 2), 0) AS pje_comision,
		--df.alic_iva*0 AS comision,
		c.id_vendedor_id,
		v.nombre_vendedor,
		"D" AS consulta
	FROM 
		detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
		INNER JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		INNER JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
	WHERE 
		cv.mult_comision<>0 AND 
		f.no_estadist <> True;


