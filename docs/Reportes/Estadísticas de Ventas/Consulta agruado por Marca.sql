-- Consulta agruado por Marca
SELECT 
	producto_marca.nombre_producto_marca,
	SUM(detalle_factura.cantidad*comprobante_venta.mult_estadistica) AS cantidad,
	SUM(((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica) AS total
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False
GROUP BY producto.id_marca_id
ORDER BY producto.id_marca_id
