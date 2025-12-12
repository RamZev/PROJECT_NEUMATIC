-- Caracter: 
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%%'
UPDATE producto SET nombre_producto = replace(nombre_producto, '', '');

-- Caracter: 
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%%'
UPDATE producto SET nombre_producto = replace(nombre_producto, '', '');

-- Caracter: 
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%%'
UPDATE producto SET nombre_producto = replace(nombre_producto, '', '');

-- Caracter: ÿ
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%ÿ%'
UPDATE producto SET nombre_producto = replace(nombre_producto, 'ÿ', ' ');

-- Caracter: ¥
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%Ñ%'
UPDATE producto SET nombre_producto = replace(nombre_producto, '¥', 'Ñ');

-- Caracter: à
--SELECT id_producto, nombre_producto FROM producto WHERE nombre_producto like '%à%'
UPDATE producto SET nombre_producto = replace(nombre_producto, 'à', 'Ó');


