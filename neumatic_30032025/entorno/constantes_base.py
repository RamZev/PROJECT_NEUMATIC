# neumatic\entorno\constantes_base.py

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
	(True, 'Activo'),
	(False, 'Inactivo'),
]

TIPO_PERSONA = [
	("F", 'Física'),
	("J", 'Jurídica'),
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
	('E', 'E-Commerce'),
]

WS_MODO = [
	(1, 'Homologación'),
	(2, 'Producción'),
]

CONDICION_PAGO = [
	(1, 'Contado'),
	(2, 'Cuenta Corriente'),
]

JERARQUIA = [
	('A', 'A'),
	('B', 'B'),
	('C', 'C'),
	('D', 'D'),
	('E', 'E'),
	('F', 'F'),
	('G', 'G'),
	('H', 'H'),
	('I', 'I'),
	('J', 'J'),
	('K', 'K'),
	('L', 'L'),
	('M', 'M'),
	('N', 'N'),
	('Ñ', 'Ñ'),
	('O', 'O'),
	('P', 'P'),
	('Q', 'Q'),
	('R', 'R'),
	('S', 'S'),
	('T', 'T'),
	('U', 'U'),
	('V', 'V'),
	('W', 'W'),
	('X', 'X'),
	('Y', 'Y'),
	('Z', 'Z'),
]

ESTATUS_CHOICES = [ 
	('activos', 'Activos'),
	('inactivos', 'Inactivos'), 
	('todos', 'Todos'), 
]

ORDEN_CHOICES = [ 
	('nombre', 'Nombre'),
	('codigo', 'Código'), 
]

ORDEN_CHOICES = [ 
	('nombre', 'Nombre'),
	('codigo', 'Código'), 
]

PRECIO_DESCRIPCION = [
	(True, 'SI'),
	(False, 'NO')
]