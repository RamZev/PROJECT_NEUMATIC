SELECT 
	SUM((df.total/(df.alic_iva/100+1))*cv.mult_venta) AS total,
	SUM((df.gravado)*cv.mult_venta) AS total_gravado,
	p.tipo_producto
FROM detalle_factura df
	JOIN factura f ON df.id_factura_id = f.id_factura
	JOIN producto p ON df.id_producto_id = p.id_producto
	JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
	JOIN vlventasresumenib vl ON df.id_factura_id = vl.id_factura
	--JOIN vlventasresumenib vl ON f.id_factura = vl.id_factura
WHERE p.tipo_producto = "S"
ORDER BY
	p.tipo_producto

-- INTO CURSOR T2
SELECT 
	SUM((detalle_factura.total/(detalle_factura.alic_iva/100+1))*comprobante_venta.mult_venta) AS total, 
	SUM((detalle_factura.gravado)*comprobante_venta.mult_venta) AS total_gravado, 
	producto.tipo_producto 
FROM detalle_factura, producto, vlventasresumenib, comprobante_venta
WHERE detalle_factura.compro = vlventasresumenib.compro AND detalle_factura.letra = vlventasresumenib.letra AND detalle_factura.numero = vlventasresumenib.numero
 AND detalle_factura.codigo = producto.codigo
 AND factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
 AND producto.tipo_producto = "S"
ORDER BY producto.tipo_producto
INTO CURSOR T2

-- ---------------------------
select * from detalle_factura
select * from comprobante_venta

select DISTINCT tipo_producto from producto
SELECT tipo_producto FROM producto WHERE tipo_producto = "O"
SELECT * FROM producto WHERE tipo_producto = "O"

