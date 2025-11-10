BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "comprobante_compra" (
	"usuario"	varchar(20),
	"estacion"	varchar(20),
	"fcontrol"	varchar(22),
	"id_comprobante_compra"	integer NOT NULL,
	"estatus_comprobante_compra"	bool NOT NULL,
	"codigo_comprobante_compra"	varchar(3) NOT NULL UNIQUE,
	"nombre_comprobante_compra"	varchar(30) NOT NULL,
	"nombre_impresion"	varchar(20) NOT NULL,
	"mult_compra"	integer NOT NULL,
	"mult_saldo"	integer NOT NULL,
	"mult_stock"	integer NOT NULL,
	"mult_caja"	integer NOT NULL,
	"libro_iva"	bool NOT NULL,
	"codigo_afip_a"	varchar(3) NOT NULL,
	"codigo_afip_b"	varchar(3) NOT NULL,
	"codigo_afip_c"	varchar(3) NOT NULL,
	"codigo_afip_m"	varchar(3) NOT NULL,
	"remito"	bool,
	"retencion"	bool,
	"id_user_id"	bigint,
	PRIMARY KEY("id_comprobante_compra" AUTOINCREMENT),
	FOREIGN KEY("id_user_id") REFERENCES "usuarios_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE VIEW A AS SELECT "prueba";
CREATE VIEW "VLClienteUltimaVenta" AS 
	SELECT 
		f.id_cliente_id,
		c.nombre_cliente,
		MAX(f.fecha_comprobante) fecha_ultimo_comprobante,
		f.id_vendedor_id
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
	GROUP BY
		f.id_cliente_id;
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
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN operario o ON df.id_operario_id = o.id_operario
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE 
		pf.comision_operario <> 0
		AND cv.mult_estadistica <> 0;
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
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE
		(f.compro = 'RC' OR f.compro = 'RB' OR f.compro = 'RE');
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
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
	WHERE 
		cv.mult_comision<>0
		AND f.no_estadist <> True;
CREATE VIEW VLCompraIngresada AS
	SELECT
		--c.compro,
		--c.letra_comprobante,
		--c.numero_comprobante,
		c.fecha_comprobante,
		cc.codigo_comprobante_compra,
		cc.nombre_comprobante_compra,
		(cc.codigo_comprobante_compra || '  ' || c.letra_comprobante || '  ' || SUBSTR(printf('%012d', c.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', c.numero_comprobante), 5)) AS comprobante,
		c.id_proveedor_id,
		p.nombre_proveedor,
		c.total,
		c.observa_comprobante
	FROM
		compra c
		INNER JOIN comprobante_compra cc ON c.id_comprobante_compra_id = cc.id_comprobante_compra
		INNER JOIN proveedor p ON c.id_proveedor_id = p.id_proveedor;
CREATE VIEW "VLComprobantesVencidos" AS 
	SELECT 
		f.id_factura,
		f.fecha_comprobante,
		CAST(JULIANDAY(DATE('now')) - JULIANDAY(f.fecha_comprobante) AS INTEGER) AS dias_vencidos,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(cv.codigo_comprobante_venta || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		CAST(f.total AS NUMERIC)* 1.0 AS total,
		CAST(f.entrega AS NUMERIC)* 1.0 AS entrega,
		ROUND(CAST(f.total - f.entrega AS NUMERIC), 2) * 1.0 AS saldo,
		f.id_vendedor_id,
		f.id_sucursal_id
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE
		f.estado = "";
CREATE VIEW VLDetalleCompraProveedor AS
	SELECT
		c.id_proveedor_id,
		pv.nombre_proveedor,
		--c.compro,
		--c.letra_comprobante,
		--c.numero_comprobante,
		(cc.codigo_comprobante_compra || '  ' || c.letra_comprobante || '  ' || SUBSTR(printf('%012d', c.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', c.numero_comprobante), 5)) AS comprobante,
		c.fecha_comprobante,
		p.id_cai_id,
		pc.cai,
		dc.id_producto_id,
		p.nombre_producto,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_marca_id,
		pm.nombre_producto_marca,
		dc.cantidad,
		p.unidad,
		dc.precio,
		dc.total,
		c.id_sucursal_id,
		s.nombre_sucursal,
		c.id_deposito_id,
		pd.nombre_producto_deposito
	FROM
		detalle_compra dc
		INNER JOIN compra c ON dc.id_compra_id = c.id_compra
		INNER JOIN comprobante_compra cc ON c.id_comprobante_compra_id = cc.id_comprobante_compra
		INNER JOIN producto p ON dc.id_producto_id = p.id_producto
		INNER JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		INNER JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
		INNER JOIN proveedor pv ON c.id_proveedor_id = pv.id_proveedor
		INNER JOIN sucursal s ON c.id_sucursal_id = s.id_sucursal
		INNER JOIN producto_deposito pd ON c.id_deposito_id = pd.id_producto_deposito
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai;
CREATE VIEW "VLEstadisticasSegunCondicion" AS 
	SELECT
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_marca_id,
		pk.nombre_producto_marca,
		p.id_modelo_id,
		pm.nombre_modelo,
		df.id_producto_id, 
		p.nombre_producto,
		df.reventa,
		df.cantidad*cv.mult_estadistica AS cantidad,
		((df.precio+(df.precio*df.descuento/100))*df.cantidad)*cv.mult_estadistica AS importe,
		df.costo*df.cantidad*cv.mult_estadistica AS costo,
		f.fecha_comprobante,
		f.id_sucursal_id
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura 
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_marca pk ON p.id_marca_id = pk.id_producto_marca
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
	WHERE
		f.no_estadist = False
		AND cv.mult_estadistica <> 0;
CREATE VIEW "VLEstadisticasVentas" AS 
	SELECT 
		f.id_factura, 
		df.id_producto_id, 
		pc.cai,
		p.nombre_producto,
		p.id_familia_id,
		pf.nombre_producto_familia, 
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		m.nombre_producto_marca,
		df.cantidad*cv.mult_estadistica AS cantidad,
		((df.cantidad*df.precio)+(df.cantidad*df.precio*df.descuento/100))*cv.mult_estadistica AS total,
		f.fecha_comprobante,
		f.id_cliente_id,
		f.id_sucursal_id
	FROM 
		detalle_factura df
		LEFT JOIN factura f ON df.id_factura_id = f.id_factura
		LEFT JOIN producto p ON df.id_producto_id = p.id_producto
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca
		LEFT JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
	WHERE 
		df.id_producto_id <> 0
		AND cv.mult_estadistica <> 0
		AND f.no_estadist = False;
CREATE VIEW "VLEstadisticasVentasMarca" AS 
	SELECT
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		f.id_cliente_id,
		df.id_producto_id,
		p.nombre_producto,
		p.medida,
		df.cantidad,
		df.precio,
		df.descuento,
		df.total,
		df.precio*df.cantidad*cv.mult_estadistica AS compra,
		f.id_sucursal_id,
		p.id_marca_id,
		pk.nombre_producto_marca,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto_marca pk ON p.id_marca_id = pk.id_producto_marca
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
	WHERE
		cv.mult_estadistica <> 0
		AND f.no_estadist <> True;
CREATE VIEW "VLEstadisticasVentasMarcaVendedor" AS 
	SELECT
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.fecha_comprobante,
		f.id_cliente_id,
		df.id_producto_id,
		p.nombre_producto,
		p.medida,
		df.cantidad,
		df.precio,
		df.descuento,
		df.total,
		f.id_sucursal_id,
		c.id_vendedor_id,
		p.id_marca_id,
		pk.nombre_producto_marca,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto_marca pk ON p.id_marca_id = pk.id_producto_marca
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
	WHERE
		cv.mult_estadistica <> 0
		AND f.no_estadist <> True;
CREATE VIEW "VLEstadisticasVentasProvincia" AS 
	SELECT 
		f.id_factura,
		df.id_producto_id,
		p.nombre_producto,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		m.nombre_producto_marca,
		df.cantidad*cv.mult_estadistica AS cantidad,
		((df.cantidad*df.precio)+(df.cantidad*df.precio*df.descuento/100))*cv.mult_estadistica AS total,
		f.fecha_comprobante,
		p.id_marca_id,
		f.id_sucursal_id,
		f.id_vendedor_id,
		pr.id_provincia,
		pr.nombre_provincia
	FROM 
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN provincia pr ON c.id_provincia_id = pr.id_provincia
	WHERE 
		df.id_producto_id <> 0
		AND cv.mult_estadistica <> 0
		AND f.no_estadist = False;
CREATE VIEW "VLEstadisticasVentasVendedor" AS 
	SELECT 
		f.id_factura, 
		df.id_producto_id, 
		p.nombre_producto,
		p.id_familia_id,
		pf.nombre_producto_familia, 
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		m.nombre_producto_marca,
		df.cantidad*cv.mult_estadistica AS cantidad,
		((df.cantidad*df.precio)+(df.cantidad*df.precio*df.descuento/100))*cv.mult_estadistica AS total,
		f.fecha_comprobante,
		p.id_marca_id,
		f.id_sucursal_id,
		f.id_vendedor_id
	FROM 
		detalle_factura df JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE 
		df.id_producto_id <> 0
		AND cv.mult_estadistica <> 0
		AND f.no_estadist = False;
CREATE VIEW "VLEstadisticasVentasVendedorCliente" AS 
	SELECT 
		df.id_producto_id,
		p.nombre_producto,
		p.id_familia_id,
		pf.nombre_producto_familia, 
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		m.nombre_producto_marca,
		df.cantidad*cv.mult_estadistica AS cantidad,
		((df.cantidad*df.precio)+(df.cantidad*df.precio*df.descuento/100))*cv.mult_estadistica AS total,
		f.fecha_comprobante,
		f.id_sucursal_id,
		f.id_cliente_id,
		c.nombre_cliente,
		f.id_vendedor_id,
		v.nombre_vendedor,
		f.no_estadist
	FROM 
		detalle_factura df 
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN vendedor v ON f.id_vendedor_id = v.id_vendedor
	WHERE 
		df.id_producto_id <> 0
		AND cv.mult_estadistica <> 0;
CREATE VIEW VLFichaSeguimientoStock AS 
	SELECT
		--ROW_NUMBER() OVER(ORDER BY fecha_comprobante) AS id,
		id_producto_id,
		id_cai_id,
		cai,
		medida,
		nombre_producto,
		id_marca_id,
		nombre_producto_marca,
		fecha_comprobante,
		comprobante,
		cantidad,
		precio,
		total,
		id_cliente_proveedor,
		nombre_cliente_proveedor,
		no_estadist,
		id_sucursal_id,
		id_deposito_id,
		marca
	FROM (
		-- Consulta VENTAS.
		SELECT
			df.id_producto_id,
			p.id_cai_id,
			pc.cai,
			p.medida,
			p.nombre_producto,
			p.id_marca_id,
			pm.nombre_producto_marca,
			f.fecha_comprobante,
			(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
			(df.cantidad * cv.mult_stock) AS cantidad,
			--df.precio,
			CAST(COALESCE(df.precio, 0.0) AS DECIMAL) AS precio,
			--df.total,
			CAST(COALESCE(df.total, 0.0) AS DECIMAL) AS total,
			f.id_cliente_id AS id_cliente_proveedor,
			c.nombre_cliente AS nombre_cliente_proveedor,
			f.no_estadist,
			f.id_sucursal_id,
			f.id_deposito_id,
			'Vta.' AS marca
		FROM
			detalle_factura df
			INNER JOIN factura f ON df.id_factura_id = f.id_factura
			INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
			INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
			INNER JOIN producto p ON df.id_producto_id = p.id_producto
			LEFT JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
			LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
		WHERE
			cv.mult_stock <> 0
		
		UNION ALL
		
		SELECT
			-- Consulta COMPRAS.
			dc.id_producto_id,
			p.id_cai_id,
			pc.cai,
			p.medida,
			p.nombre_producto,
			p.id_marca_id,
			pm.nombre_producto_marca,
			c.fecha_comprobante,
			(c.compro || ' ' || c.letra_comprobante || ' ' || SUBSTR(printf('%012d', c.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', c.numero_comprobante), 5)) AS comprobante,
			(dc.cantidad * cc.mult_stock) AS cantidad,
			--dc.precio,
			CAST(COALESCE(dc.precio, 0.0) AS DECIMAL) AS precio,
			--dc.total,
			CAST(COALESCE(dc.total, 0.0) AS DECIMAL) AS total, 
			c.id_proveedor_id AS id_cliente_proveedor,
			pr.nombre_proveedor AS nombre_cliente_proveedor,
			False AS no_estadist,
			c.id_sucursal_id,
			c.id_deposito_id,
			'Cpr.' AS marca
		FROM detalle_compra dc
			INNER JOIN compra c ON dc.id_compra_id = c.id_compra
			INNER JOIN comprobante_compra cc ON c.id_comprobante_compra_id = cc.id_comprobante_compra
			INNER JOIN proveedor pr ON c.id_proveedor_id = pr.id_proveedor
			INNER JOIN producto p ON dc.id_producto_id = p.id_producto
			LEFT JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
			LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
		WHERE
			cc.mult_stock <> 0
	);
CREATE VIEW "VLIVAVentasFULL" AS 
	SELECT 
		f.id_factura,
		cv.nombre_comprobante_venta,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		(cv.codigo_comprobante_venta || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
	WHERE
		cv.libro_iva;
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN localidad l ON c.id_localidad_id = l.id_localidad
		JOIN provincia p ON l.id_provincia_id = p.id_provincia
	WHERE
		cv.libro_iva;
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
		JOIN localidad l ON c.id_localidad_id = l.id_localidad
		JOIN provincia p ON l.id_provincia_id = p.id_provincia
	WHERE
		cv.libro_iva;
CREATE VIEW "VLLista" AS 
	SELECT
		p.id_producto,
		p.id_cai_id,
		pc.cai,
		p.tipo_producto,
		p.medida,
		p.segmento,
		p.unidad,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.nombre_producto,
		p.id_marca_id,
		px.nombre_producto_marca,
		p.precio,
		p.costo,
		p.descuento,
		p.id_alicuota_iva_id,
		ca.alicuota_iva,
		p.minimo,
		p.despacho_1,
		p.despacho_2,
		p.fecha_fabricacion,
		p.id_producto_estado_id,
		pe.nombre_producto_estado,
		p.descripcion_producto,
		p.carrito,
		p.obliga_operario,
		p.iva_exento
	FROM 
		producto p
		LEFT JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
		LEFT JOIN producto_estado pe ON p.id_producto_estado_id = pe.id_producto_estado
		LEFT JOIN codigo_alicuota ca ON p.id_alicuota_iva_id = ca.id_alicuota_iva;
CREATE VIEW "VLListaRevendedor" AS 
	SELECT
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_marca_id,
		px.nombre_producto_marca,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_producto,
		p.id_cai_id,
		pc.cai,
		p.medida,
		p.nombre_producto,
		p.precio AS contado,
		p.precio AS precio30,
		p.precio AS precio90,
		p.precio AS precio120
	FROM 
		producto p
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai;
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
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura 
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto 
		LEFT JOIN producto_marca m ON p.id_marca_id = m.id_producto_marca;
CREATE VIEW VLMovimientoInternoStock AS
	SELECT
		f.fecha_comprobante,
		f.numero_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.observa_comprobante,
		df.id_producto_id,
		p.medida,
		p.id_marca_id,
		pm.nombre_producto_marca,
		p.nombre_producto,
		df.cantidad,
		f.id_deposito_id
	FROM
		detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE
		cv.interno = 1;
CREATE VIEW "VLPercepIBSubcuentaDetallado" AS 
	SELECT 
		f.id_factura,
		c.sub_cuenta,
		p.nombre_cliente AS nombre_cliente_padre,
		cv.codigo_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		f.fecha_comprobante,
		(cv.codigo_comprobante_venta || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.cuit,
		f.gravado*cv.mult_venta AS neto,
		f.percep_ib*cv.mult_venta AS percep_ib,
		f.no_estadist
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		LEFT JOIN cliente p ON c.sub_cuenta = p.id_cliente
	WHERE
		f.percep_ib<>0
		AND cv.mult_venta<>0
	GROUP BY
		c.sub_cuenta, f.numero_comprobante;
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		LEFT JOIN cliente p ON c.sub_cuenta = p.id_cliente 
	WHERE
		f.percep_ib <> 0
		AND cv.mult_venta <> 0;
CREATE VIEW VLPercepIBVendedorDetallado AS
	SELECT 
		f.id_factura,
		c.id_vendedor_id,
		v.nombre_vendedor,
		cv.nombre_comprobante_venta,
		f.letra_comprobante,
		f.numero_comprobante,
		f.fecha_comprobante,
		(cv.codigo_comprobante_venta || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.cuit,
		f.gravado*cv.mult_venta AS neto,
		f.percep_ib*cv.mult_venta AS percep_ib,
		f.no_estadist
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE
		f.percep_ib <> 0
		AND cv.mult_venta <> 0;
CREATE VIEW "VLPercepIBVendedorTotales" AS 
	SELECT 
		f.id_factura,
		c.id_vendedor_id,
		v.nombre_vendedor,
		f.fecha_comprobante,
		ROUND(f.gravado*cv.mult_venta * 1.0, 2) AS neto,
		ROUND(f.percep_ib*cv.mult_venta * 1.0, 2) AS percep_ib
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE
		f.percep_ib <> 0
		AND cv.mult_venta <> 0;
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
		ROUND(p.precio*p.descuento/100,2) AS adicional,
		c.id_vendedor_id,
		v.nombre_vendedor
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE 
		f.no_estadist = False
		AND df.precio <> df.precio_lista;
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
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto
	WHERE
		cv.mult_venta = 0;
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
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE
		cv.mult_venta = 0
		AND f.estado = "";
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
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN producto p ON df.id_producto_id = p.id_producto
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE
		cv.mult_venta = 0;
CREATE VIEW VLReposicionStock AS 
	SELECT 1 AS dummy;
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
	FROM
		factura f 
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	WHERE
		cv.mult_saldo <> 0;
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
	FROM
		factura f 
		JOIN cliente c ON f.id_cliente_id = c.id_cliente 
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta 
		JOIN localidad l ON c.id_localidad_id = l.id_localidad
	WHERE 
		f.condicion_comprobante = 2
		AND cv.mult_saldo <> 0;
CREATE VIEW VLStockCliente AS 
	SELECT
		f.id_cliente_id,
		sc.id_stock_cliente,
		c.nombre_cliente,
		sc.id_producto_id,
		p.medida,
		pc.cai,
		sc.cantidad,
		sc.retirado,
		(sc.cantidad - sc.retirado) AS stock,
		--f.compro,
		--f.letra_comprobante,
		--f.numero_comprobante,
		--f.fecha_comprobante,
		(f.compro || '  ' || f.letra_comprobante || '  ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5) || '  ' || strftime('%d/%m/%Y', f.fecha_comprobante)) AS comprobante,
		f.id_sucursal_id,
		f.id_vendedor_id
	FROM
		stock_cliente sc
		INNER JOIN factura f ON sc.id_factura_id = f.id_factura
		INNER JOIN producto p ON sc.id_producto_id = p.id_producto
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE
		sc.cantidad <> sc.retirado;
CREATE VIEW VLStockDeposito AS
	SELECT
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		px.nombre_producto_marca,
		sc.id_producto_id,
		p.medida,
		pc.cai,
		p.nombre_producto,
		SUM(sc.cantidad-sc.retirado) AS stock,
		f.id_sucursal_id
	FROM
		stock_cliente sc
		INNER JOIN producto p ON sc.id_producto_id = p.id_producto
		INNER JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		INNER JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		INNER JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
		INNER JOIN factura f ON sc.id_factura_id = f.id_factura
	WHERE
		sc.cantidad <> sc.retirado
	GROUP by
		sc.id_producto_id
	HAVING
		SUM(sc.cantidad - sc.retirado) <> 0;
CREATE VIEW "VLStockFecha" AS 
	SELECT
		ROW_NUMBER() OVER() AS id,
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		px.nombre_producto_marca,
		ps.id_producto_id,
		p.id_cai_id,
	--	p.cai,
		pc.cai,
		p.medida,
		p.nombre_producto,
	--	ps.minimo,
		SUM(ps.stock) AS stock
	FROM
		producto_stock ps
		LEFT JOIN producto p ON ps.id_producto_id = p.id_producto
		LEFT JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
	WHERE
		p.tipo_producto = "P" AND
		ps.stock <> 0
	GROUP by
		ps.id_producto_id
	HAVING
		SUM(ps.stock) <> 0
	ORDER by
		p.id_familia_id, p.id_modelo_id, p.id_marca_id, ps.id_producto_id;
CREATE VIEW VLStockGeneralSucursal AS 
	SELECT 1 AS dummy;
CREATE VIEW "VLStockSucursal" AS 
	SELECT
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		px.nombre_producto_marca,
		ps.id_producto_id,
		p.id_cai_id,
		pc.cai,
		p.medida,
		p.nombre_producto,
	--	p.precio,
		ps.stock,
	--	ps.minimo,
		p.costo*ps.stock AS costo_inventario,
		ps.id_deposito_id
	FROM
		producto_stock ps
		LEFT JOIN producto p ON ps.id_producto_id = p.id_producto
		LEFT JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
	WHERE
		ps.stock <> 0;
CREATE VIEW "VLStockUnico" AS 
	SELECT
		p.id_familia_id,
		pf.nombre_producto_familia,
		p.id_modelo_id,
		pm.nombre_modelo,
		p.id_marca_id,
		px.nombre_producto_marca,
		ps.id_producto_id,
		p.id_cai_id,
		pc.cai,
		p.medida,
		p.nombre_producto,
	--	ps.minimo,
		SUM(ps.stock) AS stock
	FROM
		producto_stock ps
		LEFT JOIN producto p ON ps.id_producto_id = p.id_producto
		LEFT JOIN producto_marca px ON p.id_marca_id = px.id_producto_marca
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_modelo pm ON p.id_modelo_id = pm.id_modelo
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
	WHERE
		ps.stock <> 0
	GROUP by
		ps.id_producto_id
	HAVING
		SUM(ps.stock) <> 0;
CREATE VIEW "VLTablaDinamicaDetalleVentas" AS 
	SELECT
		df.id_factura_id,
		s.nombre_sucursal,
		cv.nombre_comprobante_venta,
		f.fecha_comprobante,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante, 
		CASE f.condicion_comprobante
			WHEN 1 THEN 'Contado'
			WHEN 2 THEN 'Cta. Cte.'
			ELSE 'Desconocido'
		END AS condicion_comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.mayorista,
		df.reventa,
		df.id_producto_id,
		pc.cai,
		p.nombre_producto,
		pm.nombre_producto_marca,
		pf.nombre_producto_familia,
		p.segmento,
		df.cantidad*cv.mult_venta AS cantidad,
		df.costo,
		df.precio,
		df.descuento,
		df.gravado*cv.mult_venta AS gravado,
		df.no_gravado*cv.mult_venta AS no_gravado,
		df.iva*cv.mult_venta AS iva,
		df.total*cv.mult_venta AS total,
		f.no_estadist,
		f.id_user_id,
		c.codigo_postal,
		l.nombre_localidad,
		pr.nombre_provincia,
		v.nombre_vendedor,
		f.comision,
		df.id_operario_id,
		o.nombre_operario,
		f.promo,
		cv.libro_iva
	FROM
		detalle_factura df
		LEFT JOIN factura f ON df.id_factura_id = f.id_factura
		LEFT JOIN producto p ON df.id_producto_id = p.id_producto
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
		LEFT JOIN operario o ON df.id_operario_id = o.id_operario
		LEFT JOIN cliente c ON f.id_cliente_id = c.id_cliente
		LEFT JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		LEFT JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
		LEFT JOIN sucursal s ON f.id_sucursal_id = s.id_sucursal
		LEFT JOIN localidad l ON c.id_localidad_id = l.id_localidad
		LEFT JOIN provincia pr ON l.id_provincia_id = pr.id_provincia
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai;
CREATE VIEW "VLTablaDinamicaEstadistica" AS 
	SELECT
		df.id_factura_id,
		s.nombre_sucursal,
		cv.nombre_comprobante_venta,
		f.fecha_comprobante,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante, 
		CASE f.condicion_comprobante
			WHEN 1 THEN 'Contado'
			WHEN 2 THEN 'Cta. Cte.'
			ELSE 'Desconocido'
		END AS condicion_comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.mayorista,
		df.reventa,
		df.id_producto_id,
		pc.cai,
		p.nombre_producto,
		pm.nombre_producto_marca,
		pf.nombre_producto_familia,
		p.segmento,
		df.cantidad*cv.mult_estadistica AS cantidad,
		df.costo,
		df.precio,
		df.descuento,
		df.gravado*cv.mult_estadistica AS gravado,
		df.no_gravado*cv.estadistica AS no_gravado,
		df.total*cv.mult_estadistica AS total,
		f.no_estadist,
		f.id_user_id,
		c.codigo_postal,
		l.nombre_localidad,
		pr.nombre_provincia,
		v.nombre_vendedor,
		f.comision,
		df.id_operario_id,
		o.nombre_operario,
		f.promo,
		cv.libro_iva
	FROM
		detalle_factura df
		LEFT JOIN factura f ON df.id_factura_id = f.id_factura
		LEFT JOIN producto p ON df.id_producto_id = p.id_producto
		LEFT JOIN producto_familia pf ON p.id_familia_id = pf.id_producto_familia
		LEFT JOIN producto_marca pm ON p.id_marca_id = pm.id_producto_marca
		LEFT JOIN operario o ON df.id_operario_id = o.id_operario
		LEFT JOIN cliente c ON f.id_cliente_id = c.id_cliente
		LEFT JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		LEFT JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
		LEFT JOIN sucursal s ON f.id_sucursal_id = s.id_sucursal
		LEFT JOIN localidad l ON c.id_localidad_id = l.id_localidad
		LEFT JOIN provincia pr ON l.id_provincia_id = pr.id_provincia
		LEFT JOIN producto_cai pc ON p.id_cai_id = pc.id_cai
	WHERE
		cv.mult_estadistica<>0
		AND f.no_estadist=False;
CREATE VIEW "VLTablaDinamicaVentas" AS 
	SELECT
		s.nombre_sucursal,
		cv.nombre_comprobante_venta,
		f.fecha_comprobante,
		f.letra_comprobante,
		f.numero_comprobante,
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante, 
		CASE f.condicion_comprobante
			WHEN 1 THEN 'Contado'
			WHEN 2 THEN 'Cta. Cte.'
			ELSE 'Desconocido'
		END AS condicion_comprobante,
		f.id_cliente_id,
		c.nombre_cliente,
		c.mayorista,
		f.gravado*cv.mult_venta AS gravado,
		f.exento*cv.mult_venta AS exento,
		f.iva*cv.mult_venta AS iva,
		f.percep_ib*cv.mult_venta AS percepcion,
		f.total*cv.mult_venta AS total,
		f.no_estadist,
		f.id_user_id,
		c.codigo_postal,
		l.nombre_localidad,
		p.nombre_provincia,
		v.nombre_vendedor,
		f.comision,
		f.promo,
		cv.libro_iva
	FROM
		factura f
		LEFT JOIN cliente c ON f.id_cliente_id = c.id_cliente
		LEFT JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		LEFT JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
		LEFT JOIN sucursal s ON f.id_sucursal_id = s.id_sucursal
		LEFT JOIN localidad l ON c.id_localidad_id = l.id_localidad
		LEFT JOIN provincia p ON l.id_provincia_id = p.id_provincia;
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
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN tipo_iva ti ON c.id_tipo_iva_id = ti.id_tipo_iva
	WHERE
		cv.mult_saldo = 0;
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente;
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
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN usuarios_user u ON f.id_user_id = u.id
	WHERE
		cv.mult_venta <> 0;
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
	FROM
		detalle_factura df
		JOIN factura f ON df.id_factura_id = f.id_factura
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN producto p ON df.id_producto_id = p.id_producto
	WHERE
		cv.mult_venta <> 0 AND f.no_estadist <> True;
CREATE VIEW "VLVentaSinEstadistica" AS 
	SELECT
		f.fecha_comprobante, 
		(f.compro || ' ' || f.letra_comprobante || ' ' || SUBSTR(printf('%012d', f.numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', f.numero_comprobante), 5)) AS comprobante, 
		f.id_cliente_id,
		c.nombre_cliente,
		f.total,
		c.id_vendedor_id,
		v.nombre_vendedor,
		c.sub_cuenta,
		f.id_sucursal_id,
		s.nombre_sucursal
	FROM
		factura f
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN sucursal s ON f.id_sucursal_id = s.id_sucursal
		JOIN vendedor v ON c.id_vendedor_id = v.id_vendedor
	WHERE
		f.no_estadist = True;
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
	FROM
		factura f
		JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		JOIN cliente c ON f.id_cliente_id = c.id_cliente
		JOIN provincia p ON c.id_provincia_id = p.id_provincia
	WHERE
		cv.libro_iva = True;
CREATE INDEX IF NOT EXISTS "comprobante_compra_id_user_id_142a4f52" ON "comprobante_compra" (
	"id_user_id"
);
COMMIT;
