# Define las columnas Bootstrap y sección para cada campo
estructura_campos = {
	'persona': {
		'Información Personal': {
			'fila_1': [
				{'field_name': 'estatus_persona', 'columna': 2},
				{'field_name': 'nombre_persona', 'columna': 4},
				{'field_name': 'apellido_persona', 'columna': 4},
				{'field_name': 'fecha_ingreso', 'columna': 2},
			],
			'fila_2': [
				{'field_name': 'email_persona1', 'columna': 5},
				{'field_name': 'email_persona2', 'columna': 5},
				{'field_name': 'fecha_nacimiento', 'columna': 2},
			],
			'fila_3': [
				{'field_name': 'direccion_persona', 'columna': 12},
			],
			'fila_4': [
				{'field_name': 'id_pais_telefono', 'columna': 2},
				{'field_name': 'telefono_persona', 'columna': 2},
				{'field_name': 'id_pais_telefmov1', 'columna': 2},
				{'field_name': 'telefmov_persona1', 'columna': 2},
				{'field_name': 'id_pais_telefmov2', 'columna': 2},
				{'field_name': 'telefmov_persona2', 'columna': 2},
			],
			'fila_5': [
				{'field_name': 'ciudad_residencia', 'columna': 3},
				{'field_name': 'id_pais_residencia', 'columna': 3},
				{'field_name': 'codigo_postal', 'columna': 3},
				{'field_name': 'aeropuerto_cercano', 'columna': 3},
			],
			'fila_6': [
				{'field_name': 'id_pais_nacimiento', 'columna': 4},
				{'field_name': 'id_pais_nacionalidad', 'columna': 4},
			],
			'fila_7': [
				{'field_name': 'imagen_persona1', 'columna': 4},
				{'field_name': 'imagen_persona2', 'columna': 4},
			],
			# Agrega más filas o campos según sea necesario
		},
		'Black List': {
			'fila_1': [
				{'field_name': 'estatus_black', 'columna': 3},
				{'field_name': 'fecha_black', 'columna': 3},
				{'field_name': 'motivo_black', 'columna': 6},
			],        
		},
		'Apariencia Personal y Tallas': {
			'fila_1': [
				{'field_name': 'id_color_cabello', 'columna': 3},
				{'field_name': 'id_color_ojos', 'columna': 3},
				{'field_name': 'estatura', 'columna': 3},
				{'field_name': 'peso', 'columna': 3},
			],
			'fila_2': [
				{'field_name': 'talla_tshirt', 'columna': 4},
				{'field_name': 'talla_coverall', 'columna': 4},
				{'field_name': 'talla_pantalon', 'columna': 4},
			],
			# Agrega más filas o campos según sea necesario
		},
		'Información en caso de Emergencia': {
			'fila_1': [
				{'field_name': 'nombre_apellidos_contacto', 'columna': 12},
			],
			'fila_2': [
				{'field_name': 'id_pais_telefcont', 'columna': 4},
				{'field_name': 'telefono_contacto', 'columna': 4},
				{'field_name': 'email_contacto', 'columna': 4},
			],
			# Agrega más filas o campos según sea necesario
		},
		'Pasaporte Visa y Documentos de Viaje': {
			'fila_1': [
				{'field_name': 'nombre_apellidos_contacto', 'columna': 12},
			],
			'fila_2': [
				{'field_name': 'id_pais_telefcont', 'columna': 4},
				{'field_name': 'telefono_contacto', 'columna': 4},
				{'field_name': 'email_contacto', 'columna': 4},
			],
			# Agrega más filas o campos según sea necesario
		},
	},
	'unidad': {
		'Esto NO Sale': {
			'fila_1': [
				{'field_name': 'estatus_black', 'columna': 3},
				{'field_name': 'fecha_black', 'columna': 3},
				{'field_name': 'motivo_black', 'columna': 6}
			]
		}
	}
}
