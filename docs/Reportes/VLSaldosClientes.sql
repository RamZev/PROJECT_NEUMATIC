DROP VIEW "main"."VLSaldosClientes";
CREATE VIEW "VLSaldosClientes" AS SELECT 
	f.id_cliente_id, 
	c.nombre_cliente, 
	c.domicilio_cliente, 
	l.nombre_localidad,
	c.codigo_postal, 
	c.telefono_cliente, 
	c.sub_cuenta, 
	SUM(f.total - f.entrega) AS saldo,
	MIN(CASE WHEN f.condicion_comprobante = 2 AND cv.mult_venta <> 0 AND f.total <> f.entrega THEN f.fecha_comprobante END) AS primer_fact_impaga, 
	MAX(f.fecha_pago) AS ultimo_pago 
FROM factura f 
	JOIN cliente c ON f.id_cliente_id = c.id_cliente 
	JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta 
	JOIN localidad l ON c.id_localidad_id = l.id_localidad
WHERE 
	f.condicion_comprobante = 2 AND 
	cv.mult_venta <> 0 
GROUP BY 
	f.id_cliente_id