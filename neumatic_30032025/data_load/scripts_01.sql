UPDATE detalle_factura
SET producto_venta = (
    SELECT nombre_producto
    FROM producto
    WHERE producto.id_producto = detalle_factura.id_producto_id
)
WHERE id_producto_id IS NOT NULL;


UPDATE factura
SET nombre_factura = (
    SELECT nombre_cliente
    FROM cliente
    WHERE cliente.id_cliente = factura.id_cliente_id
)
WHERE id_cliente_id IS NOT NULL;