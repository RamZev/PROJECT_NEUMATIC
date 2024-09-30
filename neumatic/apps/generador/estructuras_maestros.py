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
	
	'actividad': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_actividad', 'columna': 2},
				{'field_name': 'descripcion_actividad', 'columna': 4},
				{'field_name': 'fecha_registro_actividad', 'columna': 2}
			]
		}
	},
	
	'prod_deposito': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_producto_deposito', 'columna': 2},
				{'field_name': 'id_sucursal', 'columna': 4},
				{'field_name': 'nombre_producto_deposito', 'columna': 4}
			]
		}
	},
	
	'prod_familia': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_producto_familia', 'columna': 2},
				{'field_name': 'nombre_producto_familia', 'columna': 4},
				{'field_name': 'comision_operario', 'columna': 2}
			]
		}
	},
	
	'moneda': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_moneda', 'columna': 2},
				{'field_name': 'nombre_moneda', 'columna': 4},
				{'field_name': 'simbolo_moneda', 'columna': 2}
			],
			'fila_2': [
				{'field_name': 'cotizacion_moneda', 'columna': 2},
				{'field_name': 'ws_afip', 'columna': 2},
				{'field_name': 'predeterminada', 'columna': 2}
			],
		}
	},
	
	'prod_marca': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_producto_marca', 'columna': 2},
				{'field_name': 'nombre_producto_marca', 'columna': 4},
				{'field_name': 'principal', 'columna': 2},
				{'field_name': 'id_moneda', 'columna': 2},
			]
		}
	},
	
	'prod_modelo': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_modelo', 'columna': 2},
				{'field_name': 'nombre_modelo', 'columna': 4},
			]
		}
	},
	
	'prod_minimo': {
		'Información General': {
			'fila_1': [
				{'field_name': 'cai', 'columna': 2},
				{'field_name': 'minimo', 'columna': 2},
				{'field_name': 'id_deposito', 'columna': 4},
			]
		}
	},
	
	'prod_stock': {
		'Información General': {
			'fila_1': [
				{'field_name': 'id_producto', 'columna': 3},
				{'field_name': 'id_deposito', 'columna': 3},
				{'field_name': 'stock', 'columna': 2},
				{'field_name': 'minimo', 'columna': 2},
				{'field_name': 'fecha_producto_stock', 'columna': 2},
			]
		}
	},
	
	'prod_estado': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estado_producto', 'columna': 2},
				{'field_name': 'nombre_producto_estado', 'columna': 3},
			]
		}
	},
	
	'comprobante_venta': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_comprobante_venta', 'columna': 2},
				{'field_name': 'codigo_comprobante_venta', 'columna': 2},
				{'field_name': 'nombre_comprobante_venta', 'columna': 6},
			],
			'fila_2': [
				{'field_name': 'impresion', 'columna': 6},
				{'field_name': 'compro_asociado', 'columna': 4},
			],
			'fila_3': [
				{'field_name': 'mult_venta', 'columna': 2},
				{'field_name': 'mult_saldo', 'columna': 2},
				{'field_name': 'mult_stock', 'columna': 2},
				{'field_name': 'mult_comision', 'columna': 2},
				{'field_name': 'mult_caja', 'columna': 2},
				{'field_name': 'mult_estadistica', 'columna': 2},
			],
			'fila_4': [
				{'field_name': 'libro_iva', 'columna': 2},
				{'field_name': 'estadistica', 'columna': 2},
				{'field_name': 'electronica', 'columna': 2},
				{'field_name': 'presupuesto', 'columna': 2},
				{'field_name': 'pendiente', 'columna': 2},
			],
			'fila_5': [
				{'field_name': 'codigo_afip_a', 'columna': 2},
				{'field_name': 'codigo_afip_b', 'columna': 2},
				{'field_name': 'info_michelin_auto', 'columna': 2},
				{'field_name': 'info_michelin_camion', 'columna': 2},
			],
		}
	},
	
	'comprobante_compra': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_comprobante_compra', 'columna': 2},
				{'field_name': 'codigo_comprobante_compra', 'columna': 3},
				{'field_name': 'nombre_comprobante_compra', 'columna': 3},
			],
			'fila_2': [
				{'field_name': 'mult_compra', 'columna': 2},
				{'field_name': 'mult_saldo', 'columna': 2},
				{'field_name': 'mult_stock', 'columna': 2},
				{'field_name': 'mult_caja', 'columna': 2},
			],
			'fila_3': [
				{'field_name': 'codigo_afip_a', 'columna': 2},
				{'field_name': 'codigo_afip_b', 'columna': 2},
				{'field_name': 'codigo_afip_c', 'columna': 2},
				{'field_name': 'codigo_afip_m', 'columna': 2},
			],
			'fila_4': [
				{'field_name': 'libro_iva', 'columna': 2},
			],
		}
	},
	
	'provincia': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_provincia', 'columna': 2},
				{'field_name': 'codigo_provincia', 'columna': 2},
				{'field_name': 'nombre_provincia', 'columna': 3},
			]
		}
	},
	
	'localidad': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_localidad', 'columna': 2},
				{'field_name': 'id_provincia', 'columna': 3},
				{'field_name': 'codigo_postal', 'columna': 2},
				{'field_name': 'nombre_localidad', 'columna': 3},
			]
		}
	},
	
	'tipo_documento_identidad': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_tipo_documento_identidad', 'columna': 2},
				{'field_name': 'nombre_documento_identidad', 'columna': 2},
				{'field_name': 'tipo_documento_identidad', 'columna': 2},
				{'field_name': 'codigo_afip', 'columna': 2},
				{'field_name': 'ws_afip', 'columna': 2},
			]
		}
	},
	
	'tipo_iva': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_tipo_iva', 'columna': 2},
				{'field_name': 'codigo_iva', 'columna': 2},
				{'field_name': 'nombre_iva', 'columna': 3},
				{'field_name': 'discrimina_iva', 'columna': 2},
			]
		}
	},
	
	'tipo_percepcion_ib': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_tipo_percepcion_ib', 'columna': 2},
				{'field_name': 'descripcion_tipo_percepcion_ib', 'columna': 6},
			],
			'fila_2': [
				{'field_name': 'alicuota', 'columna': 2},
				{'field_name': 'monto', 'columna': 2},
				{'field_name': 'minimo', 'columna': 2},
				{'field_name': 'neto_total', 'columna': 2},
			],
		}
	},
	
	'tipo_retencion_ib': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_tipo_retencion_ib', 'columna': 2},
				{'field_name': 'descripcion_tipo_retencion_ib', 'columna': 6},
			],
			'fila_2': [
				{'field_name': 'alicuota_inscripto', 'columna': 2},
				{'field_name': 'alicuota_no_inscripto', 'columna': 2},
				{'field_name': 'monto', 'columna': 2},
				{'field_name': 'minimo', 'columna': 2},
			],
		}
	},
	
	'operario': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_operario', 'columna': 2},
				{'field_name': 'nombre_operario', 'columna': 6},
			],
			'fila_2': [
				{'field_name': 'telefono_operario', 'columna': 6},
				{'field_name': 'email_operario', 'columna': 6},
			],
		}
	},
	
	'producto': {
		'Información General': {
			'fila_1': [
				{'field_name': 'estatus_producto', 'columna': 2},
				{'field_name': 'codigo_producto', 'columna': 2},
				{'field_name': 'nombre_producto', 'columna': 4},
				{'field_name': 'tipo_producto', 'columna': 2},
			],
			'fila_2': [
				{'field_name': 'id_familia', 'columna': 4},
				{'field_name': 'id_marca', 'columna': 4},
				{'field_name': 'id_modelo', 'columna': 4},
			],
			'fila_3': [
				{'field_name': 'cai', 'columna': 6},
				{'field_name': 'medida', 'columna': 6},
				{'field_name': 'segmento', 'columna': 6},
				{'field_name': 'unidad', 'columna': 6},
				{'field_name': 'fecha_fabricacion', 'columna': 6},
			],
			'fila_4': [
				{'field_name': 'costo', 'columna': 6},
				{'field_name': 'alicuota_iva', 'columna': 6},
				{'field_name': 'precio', 'columna': 6},
				{'field_name': 'descuento', 'columna': 6},
			],
			'fila_5': [
				{'field_name': 'id_familia', 'columna': 6},
				{'field_name': 'email_operario', 'columna': 6},
				{'field_name': 'email_operario', 'columna': 6},
			],
			'fila_6': [
				{'field_name': 'id_familia', 'columna': 6},
				{'field_name': 'email_operario', 'columna': 6},
				{'field_name': 'email_operario', 'columna': 6},
			],
		}
	},
	
}
