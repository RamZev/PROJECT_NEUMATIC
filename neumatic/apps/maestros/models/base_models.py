# neumatic\apps\maestros\models\base_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
# from .sucursal_models import Sucursal
from entorno.constantes_base import ESTATUS_GEN, CONDICION_PAGO


class Actividad(ModeloBaseGenerico):
	id_actividad = models.AutoField(primary_key=True)
	estatus_actividad = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	descripcion_actividad = models.CharField("Descripción actividad",
											 max_length=30)
	
	def __str__(self):
		return self.descripcion_actividad
	
	class Meta:
		db_table = 'actividad'
		verbose_name = ('Actividad')
		verbose_name_plural = ('Actividades')
		ordering = ['descripcion_actividad']


class ProductoDeposito(ModeloBaseGenerico):
	id_producto_deposito = models.AutoField(primary_key=True)
	estatus_producto_deposito = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)
	id_sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE,
									verbose_name="Sucursal")
	nombre_producto_deposito = models.CharField("Nombre", max_length=50)
	
	def __str__(self):
		return self.nombre_producto_deposito
	
	class Meta:
		db_table = 'producto_deposito'
		verbose_name = 'Producto Depósito'
		verbose_name_plural = 'Producto Depósitos'
		ordering = ['nombre_producto_deposito']


class ProductoFamilia(ModeloBaseGenerico):
	id_producto_familia = models.AutoField(primary_key=True)
	estatus_producto_familia = models.BooleanField("Estatus", default=True,
												   choices=ESTATUS_GEN)
	nombre_producto_familia = models.CharField("Nombre", max_length=50)
	comision_operario = models.DecimalField("Comisión Operario(%)",
											max_digits=4, decimal_places=2,
										 	default=0.00, null=True, blank=True)
	info_michelin_auto = models.BooleanField("Info. Michelin auto", 
										  	 default=False)
	info_michelin_camion = models.BooleanField("Info. Michelin camión", 
											   default=False)
	
	def __str__(self):
		return self.nombre_producto_familia
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		comision_operario_str = str(self.comision_operario) if self.comision_operario else ""
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$|^$', comision_operario_str):
			errors.update({'comision_operario': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'producto_familia'
		verbose_name = ('Familia de Producto')
		verbose_name_plural = ('Familias de Producto')
		ordering = ['nombre_producto_familia']


class Moneda(ModeloBaseGenerico):
	id_moneda = models.AutoField(primary_key=True)
	estatus_moneda = models.BooleanField("Estatus", default=True,
										 choices=ESTATUS_GEN)
	nombre_moneda = models.CharField("Nombre", max_length=20)
	cotizacion_moneda = models.DecimalField("Cotización", max_digits=15,
											decimal_places=4,
											validators=[MinValueValidator(1),
					   									MaxValueValidator(99999999999.9999)])
	simbolo_moneda = models.CharField("Símbolo", max_length=3)
	ws_afip = models.CharField("WS AFIP", max_length=3)
	predeterminada = models.BooleanField("Predeterminada", null=True,
										 blank=True, default=False)

	def __str__(self):
		return self.nombre_moneda

	class Meta:
		db_table = 'moneda'
		verbose_name = ('Moneda')
		verbose_name_plural = ('Monedas')
		ordering = ['nombre_moneda']


class ProductoMarca(ModeloBaseGenerico):
	id_producto_marca = models.AutoField(primary_key=True)
	estatus_producto_marca = models.BooleanField("Estatus", default=True,
												 choices=ESTATUS_GEN)
	nombre_producto_marca = models.CharField("Nombre", max_length=50)
	principal = models.BooleanField("Principal", default=False)
	info_michelin_auto = models.BooleanField("Info. Michelin auto", 
										  	  default=False)
	info_michelin_camion = models.BooleanField("Info. Michelin camión", 
												default=False)
	id_moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT,
								  verbose_name="Moneda")
	
	def __str__(self):
		return self.nombre_producto_marca
	
	class Meta:
		db_table = 'producto_marca'
		verbose_name = ('Marca de Producto')
		verbose_name_plural = ('Marcas de Producto')
		ordering = ['nombre_producto_marca']


class ProductoModelo(ModeloBaseGenerico):
	id_modelo = models.AutoField(primary_key=True)  # Clave primaria
	estatus_modelo = models.BooleanField("Estatus", default=True,
										 choices=ESTATUS_GEN)  # Estatus del modelo
	nombre_modelo = models.CharField("Nombre", max_length=50)

	def __str__(self):
		return self.nombre_modelo

	class Meta:
		db_table = 'producto_modelo'
		verbose_name = 'Modelo de Producto'
		verbose_name_plural = 'Modelos de Producto'
		ordering = ['nombre_modelo']


class ProductoCai(ModeloBaseGenerico):
	id_cai = models.AutoField(primary_key=True)
	estatus_cai = models.BooleanField("Estatus*", default=True,
										   choices=ESTATUS_GEN)
	cai = models.CharField("CAI*", max_length=20)
	descripcion_cai = models.CharField("Descripción CAI", max_length=50, 
										null=True, blank=True)
	
	def __str__(self):
		return self.cai
	
	class Meta:
		db_table = 'producto_cai'
		verbose_name = 'CAI'
		verbose_name_plural = 'CAIs de Productos'
		ordering = ['cai']

	
class ProductoMinimo(ModeloBaseGenerico):
	id_producto_minimo = models.AutoField(primary_key=True)
	# cai = models.CharField("CAI", max_length=20)
	id_cai = models.ForeignKey(ProductoCai, on_delete=models.PROTECT, 
								verbose_name="CAI")
	minimo = models.IntegerField("Mínimo",
								 validators=[MinValueValidator(1),
											 MaxValueValidator(99)])
	id_deposito = models.ForeignKey('ProductoDeposito',
									on_delete=models.CASCADE,
									verbose_name="Depósito")

	def __str__(self):
		return f'{self.id_cai} - Min: {self.minimo}'

	class Meta:
		db_table = 'producto_minimo'
		verbose_name = 'Producto Mínimo'
		verbose_name_plural = 'Productos Mínimos'
		ordering = ['id_producto_minimo']


class ProductoStock(ModeloBaseGenerico):
	id_producto_stock = models.AutoField(primary_key=True)
	id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE,
									verbose_name="Producto")
	id_deposito = models.ForeignKey('ProductoDeposito', on_delete=models.CASCADE,
									verbose_name="Depósito")
	stock = models.IntegerField("Stock",
								validators=[MinValueValidator(1),
											MaxValueValidator(999)])
	minimo = models.IntegerField("Mínimo",
								 validators=[MinValueValidator(1),
											 MaxValueValidator(999)])
	fecha_producto_stock = models.DateField("Fecha Stock")

	def __str__(self):
		return f'Producto {self.id_producto} - Stock: {self.stock} - \
			Depósito: {self.id_deposito}'

	class Meta:
		db_table = 'producto_stock'
		verbose_name = 'Producto Stock'
		verbose_name_plural = 'Productos Stock'
		ordering = ['id_producto_stock']


class ProductoEstado(ModeloBaseGenerico):
	id_producto_estado = models.AutoField(primary_key=True)
	estado_producto = models.CharField("Estado Producto", max_length=1)
	nombre_producto_estado = models.CharField("Nombre", max_length=15)

	def __str__(self):
		return self.nombre_producto_estado

	class Meta:
		db_table = 'producto_estado'
		verbose_name = 'Estado de Producto'
		verbose_name_plural = 'Estados de Productos'
		ordering = ['nombre_producto_estado']


class ComprobanteVenta(ModeloBaseGenerico):
	id_comprobante_venta = models.AutoField(primary_key=True)
	estatus_comprobante_venta = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)  # Estatus del comprobante
	codigo_comprobante_venta = models.CharField("Código Comprobante",
												max_length=3)
	nombre_comprobante_venta = models.CharField("Nombre Comprobante", 
												max_length=50)  # Nombre del comprobante
	compro_asociado = models.CharField("Comprobate Asociado", 
										max_length=20, null=True, blank=True)  # Comprobante asociado
	
	mult_venta = models.IntegerField("Mult. Venta")  # Multiplicador de venta
	mult_saldo = models.IntegerField("Mult. Saldo")  # Multiplicador de saldo
	mult_stock = models.IntegerField("Mult. Stock")  # Multiplicador de stock
	mult_comision = models.IntegerField("Mult. Comisión")  # Multiplicador de comisión
	mult_caja = models.IntegerField("Mult. Caja")  # Multiplicador de caja
	mult_estadistica = models.IntegerField("Mult. Estadísticas")  # Multiplicador de estadísticas
	
	libro_iva = models.BooleanField("Libro IVA", default=False)  # Libro IVA asociado
	estadistica = models.BooleanField("Estadísticas", default=False)  # Indicador de estadísticas
	electronica = models.BooleanField("Electrónica", default=False)  # Comprobante electrónico
	presupuesto = models.BooleanField("Presupuesto", default=False)  # Presupuesto
	pendiente = models.BooleanField("Pendiente", default=False)  # Indicador de pendiente
	info_michelin_auto = models.BooleanField("Info. Michelin auto", 
										  	  default=False)  # Información Michelin auto
	info_michelin_camion = models.BooleanField("Info. Michelin camión", 
												default=False)  # Información Michelin camión
	codigo_afip_a = models.CharField("Código AFIP A", 
									max_length=3)  # Código AFIP A
	codigo_afip_b = models.CharField("Código AFIP B", 
									max_length=3)  # Código AFIP B
	
	def __str__(self):
		return self.nombre_comprobante_venta
	
	def clean(self):
		errors = {}
		
		if self.mult_venta != -1 and self.mult_venta != 0 and self.mult_venta != 1:
			errors.update({'mult_venta': "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_saldo != -1 and self.mult_saldo != 0 and self.mult_saldo != 1:
			errors.update({'mult_saldo': "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_stock != -1 and self.mult_stock != 0 and self.mult_stock != 1:
			errors.update({'mult_stock': "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_comision != -1 and self.mult_comision != 0 and self.mult_comision != 1:
			errors.update({'mult_comision': "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_caja != -1 and self.mult_caja != 0 and self.mult_caja != 1:
			errors.update({'mult_caja': "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_estadistica != -1 and self.mult_estadistica != 0 and self.mult_estadistica != 1:
			errors.update({'mult_estadistica': "Los valores permitidos son: -1, 0 y 1"})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()
	
	class Meta:
		db_table = 'comprobante_venta'
		verbose_name = 'Comprobante de Venta'
		verbose_name_plural = 'Comprobantes de Venta'
		ordering = ['nombre_comprobante_venta']


class ComprobanteCompra(ModeloBaseGenerico):
	id_comprobante_compra = models.AutoField(primary_key=True)
	estatus_comprobante_compra = models.BooleanField("Estatus", default=True,
													 choices=ESTATUS_GEN)
	codigo_comprobante_compra = models.CharField("Código comprobante",
												 max_length=3)
	nombre_comprobante_compra = models.CharField("Nombre", max_length=30)
	mult_compra = models.IntegerField("Mult. Compra")
	mult_saldo = models.IntegerField("Mult. Saldo")
	mult_stock = models.IntegerField("Mult. Stock")
	mult_caja = models.IntegerField("Mult. IVA")
	libro_iva = models.BooleanField("Libreo IVA", default=False)
	codigo_afip_a = models.CharField("Código AFIP A", max_length=3)
	codigo_afip_b = models.CharField("Código AFIP B", max_length=3)
	codigo_afip_c = models.CharField("Código AFIP C", max_length=3)
	codigo_afip_m = models.CharField("Código AFIP M", max_length=3)
	
	def __str__(self):
		return self.nombre_comprobante_compra
	
	def clean(self):
		errors = {}
		
		if self.mult_compra != -1 and self.mult_compra != 0 and self.mult_compra != 1:
			errors.update({"mult_compra": "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_saldo != -1 and self.mult_saldo != 0 and self.mult_saldo != 1:
			errors.update({"mult_saldo": "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_stock != -1 and self.mult_stock != 0 and self.mult_stock != 1:
			errors.update({"mult_stock": "Los valores permitidos son: -1, 0 y 1"})
		
		if self.mult_caja != -1 and self.mult_caja != 0 and self.mult_caja != 1:
			errors.update({"mult_caja": "Los valores permitidos son: -1, 0 y 1"})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()
	
	class Meta:
		db_table = 'comprobante_compra'
		verbose_name = 'Comprobante de Compra'
		verbose_name_plural = 'Comprobantes de Compra'
		ordering = ['nombre_comprobante_compra']


class Provincia(ModeloBaseGenerico):
	id_provincia = models.AutoField(primary_key=True)
	estatus_provincia = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	codigo_provincia = models.CharField("Código", max_length=1)
	nombre_provincia = models.CharField("Nombre", max_length=30)

	def __str__(self):
		return self.nombre_provincia

	class Meta:
		db_table = 'provincia'
		verbose_name = ('Provincia')
		verbose_name_plural = ('Provincias')
		ordering = ['nombre_provincia']


class Localidad(ModeloBaseGenerico):
	id_localidad = models.AutoField(primary_key=True)
	estatus_localidad = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	nombre_localidad = models.CharField("Nombre Localidad", max_length=30)
	codigo_postal = models.CharField("Código Postal", max_length=5)
	id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE,
									 verbose_name="Provincia")
	
	def __str__(self):
		return self.nombre_localidad
	
	class Meta:
		db_table = 'localidad'
		verbose_name = ('Localidad')
		verbose_name_plural = ('Localidades')
		ordering = ['codigo_postal']


class TipoDocumentoIdentidad(ModeloBaseGenerico):
	id_tipo_documento_identidad = models.AutoField(primary_key=True)
	estatus_tipo_documento_identidad = models.BooleanField("Estatus",
														   default=True,
														   choices=ESTATUS_GEN)
	nombre_documento_identidad = models.CharField("Nombre", max_length=20)
	tipo_documento_identidad = models.CharField("Tipo", max_length=4)
	codigo_afip = models.CharField("Código AFIP", max_length=2)
	ws_afip = models.CharField("WS AFIP", max_length=2)

	def __str__(self):
		return self.nombre_documento_identidad

	class Meta:
		db_table = 'tipo_documento_identidad'
		verbose_name = ('Tipo de Documento de Identidad')
		verbose_name_plural = ('Tipos de Documentos de Identidad')
		ordering = ['tipo_documento_identidad']


class TipoIva(ModeloBaseGenerico):
	id_tipo_iva = models.AutoField(primary_key=True)
	estatus_tipo_iva = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	codigo_iva = models.CharField("Código IVA", max_length=4)
	nombre_iva = models.CharField("Nombre", max_length=25)
	discrimina_iva = models.BooleanField("Discrimina IVA", null=True,
										 blank=True)

	def __str__(self):
		return self.nombre_iva

	class Meta:
		db_table = 'tipo_iva'
		verbose_name = ('Tipo de IVA')
		verbose_name_plural = ('Tipos de IVA')
		ordering = ['nombre_iva']


class TipoPercepcionIb(ModeloBaseGenerico):
	id_tipo_percepcion_ib = models.AutoField(primary_key=True)
	estatus_tipo_percepcion_ib = models.BooleanField("Estatus", default=True,
													 choices=ESTATUS_GEN)
	descripcion_tipo_percepcion_ib = models.CharField("Descripción",
													  max_length=50)
	alicuota = models.DecimalField("Alícuota(%)", max_digits=4, decimal_places=2, 
								validators=[MinValueValidator(1), 
											MaxValueValidator(99.99)])
	monto = models.DecimalField("Monto", max_digits=15, decimal_places=2, 
							 validators=[MinValueValidator(1), 
										 MaxValueValidator(9999999999999.99)])
	minimo = models.DecimalField("Mínimo", max_digits=15, decimal_places=2, 
							  validators=[MinValueValidator(1), 
					 					  MaxValueValidator(9999999999999.99)])
	neto_total = models.BooleanField("Neto total", null=True, blank=True)

	def __str__(self):
		return self.descripcion_tipo_percepcion_ib

	class Meta:
		db_table = 'tipo_percepcion_ib'
		verbose_name = ('Tipo de Percepción IB')
		verbose_name_plural = ('Tipos de Percepción IB')
		ordering = ['descripcion_tipo_percepcion_ib']


class TipoRetencionIb(ModeloBaseGenerico):
	id_tipo_retencion_ib = models.AutoField(primary_key=True)
	estatus_tipo_retencion_ib = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)
	descripcion_tipo_retencion_ib = models.CharField("Descripción",
													 max_length=50)
	alicuota_inscripto = models.DecimalField("Alícuota Inscripto(%)",
											 max_digits=4, decimal_places=2, 
											 validators=[MinValueValidator(1), 
														 MaxValueValidator(99.99)])
	alicuota_no_inscripto = models.DecimalField("Alícuota No Inscripto(%)",
												max_digits=4, decimal_places=2, 
												validators=[MinValueValidator(1), 
															MaxValueValidator(99.99)])
	monto = models.DecimalField("Monto", max_digits=15, decimal_places=2, 
							 			 validators=[MinValueValidator(1), 
													 MaxValueValidator(9999999999999.99)])
	minimo = models.DecimalField("Mínimo", max_digits=15, decimal_places=2, 
							  			   validators=[MinValueValidator(1), 
						   							   MaxValueValidator(9999999999999.99)])

	def __str__(self):
		return self.descripcion_tipo_retencion_ib

	class Meta:
		db_table = 'tipo_retencion_ib'
		verbose_name = ('Tipo de Retención IB')
		verbose_name_plural = ('Tipos de Retención IB')
		ordering = ['descripcion_tipo_retencion_ib']


class Operario(ModeloBaseGenerico):
	id_operario = models.AutoField(primary_key=True)
	estatus_operario = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre_operario = models.CharField("Nombre", max_length=50)
	telefono_operario = models.CharField("Teléfono", max_length=15)
	email_operario = models.CharField("Correo", max_length=50)
	
	def __str__(self):
		return self.nombre_operario
	
	class Meta:
		db_table = 'operario'
		verbose_name = ('Operario')
		verbose_name_plural = ('Operarios')
		ordering = ['nombre_operario']


class MedioPago(ModeloBaseGenerico):
	id_medio_pago = models.AutoField(primary_key=True)
	estatus_medio_pago = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre_medio_pago = models.CharField(max_length=30)
	condicion_medio_pago = models.IntegerField("Condición Pago", 
										  default=True,
										  choices=CONDICION_PAGO)
	plazo_medio_pago = models.IntegerField("Plazo medio de Pago")
	
	def __str__(self):
		return self.nombre_medio_pago
	
	@property
	def condicion_medio_pago_display(self):
		return self.get_condicion_medio_pago_display()
	
	
	class Meta:
		db_table = 'medio_pago'
		verbose_name = 'Medio de Pago'
		verbose_name_plural = 'Medios de Pago'
		ordering = ['nombre_medio_pago']


class PuntoVenta(ModeloBaseGenerico):
	id_punto_venta = models.AutoField(primary_key=True)
	estatus_punto_venta = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	punto_venta = models.CharField("Punto de Venta", max_length=5)
	descripcion_punto_venta = models.CharField("Descripción Pto. Venta", 
											max_length=50, null=True, 
											blank=True)
	
	def __str__(self):
		return self.punto_venta
	
	
	class Meta:
		db_table = 'punto_venta'
		verbose_name = 'Punto de Venta'
		verbose_name_plural = 'Puntos de Venta'
		ordering = ['punto_venta']
	