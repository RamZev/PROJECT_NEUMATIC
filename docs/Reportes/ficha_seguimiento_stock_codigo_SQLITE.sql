-- FICHA DE SEGUIMIENTO DE STOCK.
-- POR CÓDIGO DE PRODUCTO

-- NUEVAS TABLAS EN DB_BROWSER (movimientos en Ventas y Movimientos Internos)

--CREATE VIEW vlFichaStockVentas AS 
SELECT detalle_factura.id_producto_id, factura.compro, factura.letra_comprobante, factura.numero_comprobante, factura.fecha_comprobante,
	detalle_factura.cantidad*comprobante_venta.mult_stock as cantidad,
	detalle_factura.precio, detalle_factura.total,
	factura.id_cliente_id, cliente.nombre_cliente,
	factura.no_estadist, factura.id_sucursal_id, factura.id_deposito_id,
	'V' as marca
FROM detalle_factura 
	INNER JOIN factura on detalle_factura.id_factura_id = factura.id_factura
	INNER JOIN comprobante_venta on factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
	INNER JOIN cliente on factura.id_cliente_id = cliente.id_cliente
WHERE comprobante_venta.mult_stock <> 0
ORDER BY factura.fecha_comprobante


--(movimientos en Compras)
--CREATE VIEW vlFichaStockCompra AS
SELECT detalle_compra.id_producto_id, compra.compro, compra.letra_comprobante, compra.numero_comprobante, compra.fecha_comprobante,
	detalle_compra.cantidad*comprobante_compra.mult_stock as cantidad,
	detalle_compra.precio, detalle_compra.total,
	compra.id_proveedor_id, proveedor.nombre_proveedor,
	False as no_estadist, compra.id_sucursal_id, compra.id_deposito_id,
	'C' as marca
FROM detalle_compra
	INNER JOIN compra on detalle_compra.id_compra_id = compra.id_compra
	INNER JOIN comprobante_compra on compra.id_comprobante_compra_id = comprobante_compra.id_comprobante_compra
	INNER JOIN proveedor on compra.id_proveedor_id = proveedor.id_proveedor
WHERE comprobante_compra.mult_stock <> 0
ORDER BY compra.fecha_comprobante
