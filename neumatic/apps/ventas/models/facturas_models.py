# neumatic\apps\ventas\models\facturas_models.py
from django.db import models

from apps.maestros.models.base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN, CONDICION_VENTA
from apps.maestros.models.base_models import ComprobanteVenta, ProductoDeposito, Operario
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.cliente_models import Cliente
from apps.maestros.models.producto_models import Producto


class Factura(ModeloBaseGenerico):
	id_factura = models.AutoField(
		primary_key=True
	)
	id_orig = models.IntegerField(
		verbose_name="ID_ORIG",
		null=True,
		blank=True
	)	
	estatus_comprobante = models.BooleanField(
		verbose_name="Estatus",
		default=True,
		choices=ESTATUS_GEN
	)
	id_sucursal = models.ForeignKey(
		Sucursal,
		on_delete=models.PROTECT,
		verbose_name="Sucursal",
		null=True,
		blank=True
	)
	id_comprobante_venta = models.ForeignKey(
		ComprobanteVenta,
		on_delete=models.PROTECT,
		verbose_name="Comprobante",
		null=True,
		blank=True
	)
	compro = models.CharField(
		verbose_name="Compro",
		max_length=3,
		null=True,
		blank=True
	) 
	letra_comprobante = models.CharField(
		verbose_name="Letra",
		max_length=1,
		null=True,
		blank=True
	)
	numero_comprobante = models.IntegerField(
		verbose_name="Número",
		null=True,
		blank=True
	)
	remito = models.CharField(
		verbose_name="Remito",
		max_length=15,
		null=True,
		blank=True
	)
	fecha_comprobante = models.DateField(
		verbose_name="Fecha Emisión",
		null=True,
		blank=True
	)
	id_cliente = models.ForeignKey(
		Cliente,
		on_delete=models.PROTECT,
		verbose_name="Cliente",
		null=True,
		blank=True
	)
	cuit = models.IntegerField(
		verbose_name="CUIT",
		null=True,
		blank=True
	)
	condicion_comprobante = models.IntegerField(
		verbose_name="Condición de Venta",
		default=1,
		choices=CONDICION_VENTA
	)
	gravado = models.DecimalField(
		verbose_name="Gravado",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	exento = models.DecimalField(
		verbose_name="Exento",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	iva = models.DecimalField(
		verbose_name="IVA",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	# Esta campo no es necesario pero se deja por tema de migración de datos y confirmar si se elimina o no.
	# acrece = models.DecimalField(
	# 	verbose_name="Acrece",
	# 	max_digits=14,
	# 	decimal_places=2,
	# 	null=True,
	# 	blank=True,
	# 	default=0.0
	# )
	# Esta campo no es necesario
	# impint = models.DecimalField(
	# 	verbose_name="Imp. Interno",
	# 	max_digits=14,
	# 	decimal_places=2,
	# 	null=True,
	# 	blank=True,
	# 	default=0.0
	# )
	percep_ib = models.DecimalField(
		verbose_name="Percepción IB",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	total = models.DecimalField(
		verbose_name="Total",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	entrega = models.DecimalField(
		verbose_name="Entrega",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
	estado = models.CharField(
		verbose_name="Estado",
		max_length=1,
		null=True,
		blank=True
	)
	# Esta campo no es necesario
	# codimp = models.SmallIntegerField(
	# 	verbose_name="codimp",
	# 	null=True,
	# 	blank=True,
	# 	default=1
	# )
	marca = models.CharField(
		verbose_name="Marca",
		max_length=1,
		null=True,
		blank=True
	)
	# id_usuario = models.ForeignKey(
	# 	User,
	# 	on_delete=models.PROTECT,
	# 	verbose_name="Usuario",
	# 	null=True,
	# 	blank=True		
	# )
	# Esta campo no es necesario
	# comision = models.CharField(
	# 	verbose_name="Comisión",
	# 	max_length=1,
	# 	null=True,
	# 	blank=True
	# )
	# Esta campo no es necesario
	# codcomis = models.SmallIntegerField(
	# 	verbose_name="codcomis",
	# 	null=True,
	# 	blank=True,
	# 	default=0
	# )
	fecha_pago = models.DateField(
		verbose_name="Fecha Pago",
		null=True,
		blank=True
	)
	# Esta campo no es necesario
	# nombre = models.CharField(
	# 	verbose_name="Nombre",
	# 	max_length=30,
	# 	null=True,
	# 	blank=True
	# )
	# Esta campo no es necesario
	# id_tipo_iva = models.ForeignKey(
	# 	TipoIva,
	# 	on_delete=models.PROTECT,
	# 	verbose_name="Topo IVA",
	# 	null=True,
	# 	blank=True
	# )
	no_estadist = models.BooleanField(
		verbose_name="No estadist.",
		null=True,
		blank=True
	)
	# Esta campo no es necesario
	# usuario = models.CharField(
	# 	verbose_name="Nombre Usuario",
	# 	max_length=15,
	# 	null=True,
	# 	blank=True
	# )
	suc_imp = models.SmallIntegerField(
		verbose_name="sucimp",
		null=True,
		blank=True
	)
	cae = models.IntegerField(
		verbose_name="CAE",
		null=True,
		blank=True,
		default=0
	)
	cae_vto = models.DateField(
		verbose_name="Vcto. CAE",
		null=True,
		blank=True
	)
	observa_comprobante = models.CharField(
		verbose_name="Observaciones",
		max_length=30,
		null=True,
		blank=True
	)
	stock_clie = models.BooleanField(
		verbose_name="stockclie",
		null=True,
		blank=True
	)
	id_deposito = models.ForeignKey(
		ProductoDeposito,
		on_delete=models.PROTECT,
		verbose_name="Depósito",
		null=True,
		blank=True
	)
	promo = models.BooleanField(
		verbose_name="Promo",
		null=True,
		blank=True
	)
	
	def __str__(self):
		numero = str(self.numero_comprobante).strip().zfill(12)
		return f"{self.id_comprobante_venta.codigo_comprobante_venta} {self.letra_comprobante} {numero[:4]}-{numero[4:]}"
	
	
	class Meta:
		db_table = "factura"
		verbose_name = ('Factura')
		verbose_name_plural = ('Facturas')
		# ordering = ['id_factura']


class DetalleFactura(ModeloBaseGenerico):
	id_detalle_factura = models.AutoField(
		primary_key=True
	)
	id_factura = models.ForeignKey(
		Factura,
		on_delete=models.CASCADE,
		verbose_name="Factura",
		null=True,
		blank=True
	)
	id_producto = models.ForeignKey(
		Producto,
		on_delete=models.PROTECT,
		verbose_name="Producto",
		null=True,
		blank=True
	)
	codigo = models.IntegerField(
		verbose_name="Cód. Producto",
		null=True,
		blank=True
	)
	cantidad = models.DecimalField(
		verbose_name="Cantidad",
		max_digits=7,
		decimal_places=2,
		null=True,
		blank=True
	)
	costo = models.DecimalField(
		verbose_name="Costo",
		max_digits=12,
		decimal_places=2,
		null=True,
		blank=True
	)
	precio = models.DecimalField(
		verbose_name="Precio",
		max_digits=12,
		decimal_places=2,
		null=True,
		blank=True
	)
	descuento = models.DecimalField(
		verbose_name="Descuento(%)",
		max_digits=6,
		decimal_places=2,
		null=True,
		blank=True
	)
	gravado = models.DecimalField(
		verbose_name="Gravado",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True
	)
	alic_iva = models.DecimalField(
		verbose_name="Alíc. IVA(%)",
		max_digits=6,
		decimal_places=2,
		null=True,
		blank=True
	)
	iva = models.DecimalField(
		verbose_name="IVA",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True
	)
	total = models.DecimalField(
		verbose_name="Total",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True
	)
	reventa = models.CharField(
		verbose_name="Reventa",
		max_length=1,
		null=True,
		blank=True
	)
	stock = models.DecimalField(
		verbose_name="Stock",
		max_digits=10,
		decimal_places=2,
		null=True,
		blank=True
	)
	act_stock = models.BooleanField(
		verbose_name="Act. Stock",
		null=True,
		blank=True
	)
	id_operario = models.ForeignKey(
		Operario,
		on_delete=models.PROTECT,
		null=True,
		blank=True
	)
	
	def __str__(self):
		return self.id_detalle_factura
	
	
	class Meta:
		db_table = "detalle_factura"
		verbose_name = ('Detalle Factura')
		verbose_name_plural = ('Detalles Factura')
		# ordering = ['id_detalle_factura']