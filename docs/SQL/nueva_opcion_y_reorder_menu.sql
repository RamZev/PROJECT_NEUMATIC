-- Insertar la nueva opción en Archivos -> Productos.
INSERT INTO "main"."menu_menuitem" ("id_menu_item", "name", "url_name", "query_params", "icon", "is_collapse", "order", "heading_id", "parent_id") 
	VALUES (151, 'Actualizar Estados de Productos', 'actualizar_estados_productos', '', '', '0', 8, NULL, 136);

-- Reordenar opciones existentes.
UPDATE menu_menuitem SET "order" = 9 WHERE id_menu_item=11;
UPDATE menu_menuitem SET "order" = 10 WHERE id_menu_item=138;