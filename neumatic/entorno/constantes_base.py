# neumatic\entorno\constantes_base.py

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
    (True, 'Activo'),
    (False, 'Inactivo'),
]

TIPO_PERSONA = [
    ("N", 'Natural'),
    ("F", 'Física'),
]

CONDICION_VENTA = [
    (1, 'Contado'),
    (2, 'Cuenta Corriente'),
]

CONDICION_COMPRA = [
    (1, 'Contado'),
    (2, 'Cuenta Corriente'),
]

SEXO = [
    ("M", 'Masculino'),
    ("F", 'Femenino'),
]

TIPO_PRODUCTO_SERVICIO = [
	('P', 'Producto'),
	('S', 'Servicio')
]

CLIENTE_VIP = [
	(True, 'SI'),
	(False, 'NO')
]

CLIENTE_MAYORISTA = [
	(True, 'SI'),
	(False, 'NO')
]

BLACK_LIST = [
    (True, 'Si'),
    (False, 'No'),
]

TIPO_VENTA = [
	('M', 'Mostrador'),
	('R', 'Revendedor'),
]

WS_MODO = [
	(1, 'Homologación'),
	(2, 'Producción'),
]

CONDICION_PAGO = [
    (1, 'Contado'),
    (2, 'Cuenta Corriente'),
]