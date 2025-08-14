UPDATE producto
SET obliga_operario = 1
WHERE tipo_producto = "S" AND (obliga_operario IS NULL OR obliga_operario = 0);