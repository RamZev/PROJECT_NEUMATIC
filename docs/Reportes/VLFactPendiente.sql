DROP VIEW "main"."VLFactPendiente";
CREATE VIEW "VLFactPendiente" AS WITH acumulado AS (
    SELECT 
        f.id_cliente_id,
        f.fecha_comprobante,
        f.numero_comprobante,
        (f.total - f.entrega) * cv.mult_saldo AS saldo,
        ROW_NUMBER() OVER (PARTITION BY f.id_cliente_id ORDER BY f.fecha_comprobante, f.numero_comprobante) AS row_num
    FROM factura f
    JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
    WHERE f.total <> f.entrega 
    AND cv.mult_saldo <> 0
)
SELECT 
    f.id_cliente_id, 
    c.nombre_cliente AS razon_social, 
    cv.nombre_comprobante_venta, 
    f.letra_comprobante, 
    f.numero_comprobante, 
	(f.letra_comprobante || " " || SUBSTR(printf('%012d', numero_comprobante), 1, 4) || '-' || SUBSTR(printf('%012d', numero_comprobante), 5)) AS numero, 
    f.fecha_comprobante, 
    f.remito, 
	f.condicion_comprobante, 
    f.total * cv.mult_saldo AS total, 
    f.entrega * cv.mult_saldo AS entrega, 
    (f.total - f.entrega) * cv.mult_saldo AS saldo, 
    ( 
        SELECT SUM(a.saldo)
        FROM acumulado a
        WHERE a.id_cliente_id = f.id_cliente_id
        AND a.row_num <= (
            SELECT row_num 
            FROM acumulado 
            WHERE id_cliente_id = f.id_cliente_id 
            AND fecha_comprobante = f.fecha_comprobante
            AND numero_comprobante = f.numero_comprobante
        )
    ) AS saldo_acumulado,
	0 as intereses
FROM factura f 
JOIN cliente c ON f.id_cliente_id = c.id_cliente
JOIN comprobante_venta cv ON f.id_comprobante_venta_id = cv.id_comprobante_venta
WHERE 
    f.total <> f.entrega 
    AND cv.mult_saldo <> 0
