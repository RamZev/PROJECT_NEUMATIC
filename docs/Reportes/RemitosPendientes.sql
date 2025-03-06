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
		f.id_sucursal_id AS sucursal_fac,
		c.id_sucursal_id AS sucursal_cli
	FROM detalle_factura df
		INNER JOIN factura f ON df.id_factura_id = f.id_factura
		INNER JOIN producto p ON df.id_producto_id = p.id_producto
		INNER JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
		INNER JOIN cliente c ON f.id_cliente_id = c.id_cliente
	WHERE cv.mult_venta = 0 AND f.estado = ""
	ORDER BY c.nombre_cliente, f.fecha_comprobante, f.numero_comprobante


	
SELECT 
		comprobante_venta.nombre_comprobante_venta,
		factura.letra_comprobante,
		factura.numero_comprobante,
		factura.fecha_comprobante,
		factura.id_cliente_id,
		cliente.nombre_cliente,
		detalle_factura.id_producto_id,
		producto.nombre_producto, producto.cai,
		producto.medida,
		detalle_factura.cantidad,
		detalle_factura.precio,
		detalle_factura.descuento,
		detalle_factura.total*comprobante_venta.mult_stock*-1 as total,
		factura.id_sucursal_id,
		cliente.id_sucursal_id as Sucursal_cliente
	FROM detalle_factura 
		INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
		INNER JOIN cliente ON factura.id_cliente_id = cliente.id_cliente
	WHERE comprobante_venta.mult_venta = 0
	ORDER BY cliente.nombre_cliente, factura.fecha_comprobante, factura.numero_comprobante
