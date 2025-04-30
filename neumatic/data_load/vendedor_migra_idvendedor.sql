-- Actualización de vendedor en factura
UPDATE factura
SET id_vendedor_id = 1
WHERE id_vendedor_id IS NULL;

-- Actualización de vendedor mostrador en cliente
UPDATE cliente
SET id_vendedor_id = 1
WHERE id_vendedor_id IS NULL;
