-- ---------------------------------------------------------------------------
--  Saldos Clientes.
--  Modelo: VLSaldosClientes
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS "main"."VLSaldosClientes";
CREATE VIEW "VLSaldosClientes" AS SELECT 
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
	f.condicion_comprobante
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
CREATE VIEW "VLMercaderiaPorCliente" AS SELECT 
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
CREATE VIEW "VLTotalRemitosClientes" AS SELECT 
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
CREATE VIEW "VLVentaComproLocalidad" AS SELECT 
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
CREATE VIEW "VLVentaMostrador" AS SELECT 
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
CREATE VIEW "VLVentaCompro" AS SELECT 
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
CREATE VIEW "VLComprobantesVencidos" AS SELECT 
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
CREATE VIEW "VLRemitosPendientes" AS SELECT 
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
	ORDER BY c.nombre_cliente, f.fecha_comprobante, f.numero_comprobante