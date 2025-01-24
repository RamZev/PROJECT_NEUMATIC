WITH acumulado AS (
    SELECT 
        id_cliente_id,
        fecha_comprobante,
        numero_comprobante,
        (total - entrega) AS saldo, 
        ROW_NUMBER() OVER (
            PARTITION BY id_cliente_id 
            ORDER BY fecha_comprobante, numero_comprobante
        ) AS row_num
    FROM VLResumenCtaCte
    WHERE id_cliente_id = 9
    AND total <> entrega
)
SELECT 
    r.id_cliente_id, 
    r.razon_social, 
    r.nombre_comprobante_venta, 
    r.letra_comprobante, 
    r.numero_comprobante, 
    r.numero, 
    r.fecha_comprobante, 
    r.remito, 
    r.condicion_comprobante, 
    r.condicion, 
    r.total, 
    r.entrega, 
    (
        SELECT SUM(a.saldo)
        FROM acumulado a
        WHERE a.id_cliente_id = r.id_cliente_id
        AND a.row_num <= (
            SELECT row_num 
            FROM acumulado 
            WHERE id_cliente_id = r.id_cliente_id 
            AND fecha_comprobante = r.fecha_comprobante
            AND numero_comprobante = r.numero_comprobante
        )
    ) AS saldo_acumulado,
    r.intereses
FROM VLResumenCtaCte r
WHERE r.id_cliente_id = 9 
AND r.total <> r.entrega
ORDER BY r.fecha_comprobante, r.numero_comprobante;
