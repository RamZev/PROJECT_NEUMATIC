# neumatic\apps\maestros\models\base_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

from utils.validator.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN, CONDICION_PAGO, TIPO_CUENTA


class Actividad(ModeloBaseGenerico):
	id_actividad = models.AutoField(primary_key=True)
	estatus_actividad = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	descripcion_actividad = models.CharField("Descripción actividad",
											 max_length=30)
	
	class Meta:
		db_table = 'actividad'
		verbose_name = ('Actividad')
		verbose_name_plural = ('Actividades')
		ordering = ['descripcion_actividad']
	
	def __str__(self):
		return self.descripcion_actividad


class ProductoDeposito(ModeloBaseGenerico):
	id_producto_deposito = models.AutoField(primary_key=True)
	estatus_producto_deposito = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)
	id_sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE,
									verbose_name="Sucursal")
	nombre_producto_deposito = models.CharField("Nombre", max_length=50)
	
	class Meta:
		db_table = 'producto_deposito'
		verbose_name = 'Producto Depósito'
		verbose_name_plural = 'Producto Depósitos'
		ordering = ['nombre_producto_deposito']
	
	def __str__(self):
		return self.nombre_producto_deposito


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
	
	class Meta:
		db_table = 'producto_familia'
		verbose_name = ('Familia de Producto')
		verbose_name_plural = ('Familias de Producto')
		ordering = ['nombre_producto_familia']
	
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
	
	class Meta:
		db_table = 'moneda'
		verbose_name = ('Moneda')
		verbose_name_plural = ('Monedas')
		ordering = ['nombre_moneda']
	
	def __str__(self):
		return self.nombre_moneda


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
	
	class Meta:
		db_table = 'producto_marca'
		verbose_name = ('Marca de Producto')
		verbose_name_plural = ('Marcas de Producto')
		ordering = ['nombre_producto_marca']
	
	def __str__(self):
		return self.nombre_producto_marca


class ProductoModelo(ModeloBaseGenerico):
	id_modelo = models.AutoField(primary_key=True)  # Clave primaria
	estatus_modelo = models.BooleanField("Estatus", default=True,
										 choices=ESTATUS_GEN)  # Estatus del modelo
	nombre_modelo = models.CharField("Nombre", max_length=50)
	
	class Meta:
		db_table = 'producto_modelo'
		verbose_name = 'Modelo de Producto'
		verbose_name_plural = 'Modelos de Producto'
		ordering = ['nombre_modelo']
	
	def __str__(self):
		return self.nombre_modelo


class ProductoCai(ModeloBaseGenerico):
	id_cai = models.AutoField(primary_key=True)
	estatus_cai = models.BooleanField("Estatus*", default=True,
										choices=ESTATUS_GEN)
	cai = models.CharField("CAI*", max_length=20, unique=True)
	descripcion_cai = models.CharField("Descripción CAI", max_length=50, 
										null=True, blank=True)
	
	class Meta:
		db_table = 'producto_cai'
		verbose_name = 'CAI'
		verbose_name_plural = 'CAIs de Productos'
		ordering = ['cai']
	
	def __str__(self):
		return self.cai


class ProductoMinimo(ModeloBaseGenerico):
	id_producto_minimo = models.AutoField(primary_key=True)
	id_cai = models.ForeignKey(ProductoCai, on_delete=models.PROTECT, 
								verbose_name="CAI")
	minimo = models.IntegerField("Mínimo", default=0)
	id_deposito = models.ForeignKey('ProductoDeposito',
									on_delete=models.CASCADE,
									verbose_name="Depósito")
	
	class Meta:
		db_table = 'producto_minimo'
		verbose_name = 'Producto Mínimo'
		verbose_name_plural = 'Productos Mínimos'
		ordering = ['id_producto_minimo']
	
	def __str__(self):
		return f'{self.id_cai} - Min: {self.minimo}'


class ProductoStock(ModeloBaseGenerico):
	id_producto_stock = models.AutoField(primary_key=True)
	id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE,
									verbose_name="Producto")
	id_deposito = models.ForeignKey('ProductoDeposito', on_delete=models.CASCADE,
									verbose_name="Depósito")
	stock = models.IntegerField("Stock", default=0)
	minimo = models.IntegerField("Mínimo",default=0)
	fecha_producto_stock = models.DateField("Fecha Stock")
	
	class Meta:
		db_table = 'producto_stock'
		verbose_name = 'Producto Stock'
		verbose_name_plural = 'Productos Stock'
		ordering = ['id_producto_stock']
	
	def __str__(self):
		return f'Producto {self.id_producto} - Stock: {self.stock} - \
			Depósito: {self.id_deposito}'


class ProductoEstado(ModeloBaseGenerico):
	id_producto_estado = models.AutoField(primary_key=True)
	estatus_producto_estado = models.BooleanField("Estatus", default=True,
												choices=ESTATUS_GEN)
	estado_producto = models.CharField("Estado Producto", max_length=1, 
										unique=True)
	nombre_producto_estado = models.CharField("Nombre", max_length=15)
	
	class Meta:
		db_table = 'producto_estado'
		verbose_name = 'Estado de Producto'
		verbose_name_plural = 'Estados de Productos'
		ordering = ['nombre_producto_estado']
	
	def __str__(self):
		return self.nombre_producto_estado
	
	def clean(self):
		errors = {}
		
		if not self.estado_producto.isupper():
			errors.update({'estado_producto': 'Debe ingresar solo mayúsculas.'})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class ComprobanteVenta(ModeloBaseGenerico):
	id_comprobante_venta = models.AutoField(primary_key=True)
	estatus_comprobante_venta = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)
	codigo_comprobante_venta = models.CharField("Cód. Comprob.",
												max_length=3, unique=True)
	nombre_comprobante_venta = models.CharField("Nombre Comprobante", 
												max_length=30)
	nombre_impresion = models.CharField("Nombre Impresión", max_length=20,
									 	null=True, blank=True, default="")
	compro_asociado = models.CharField("Comprobate Asociado", 
										max_length=20, null=True, blank=True)
	mult_venta = models.IntegerField("Mult. Venta")
	mult_saldo = models.IntegerField("Mult. Saldo")
	mult_stock = models.IntegerField("Mult. Stock")
	mult_comision = models.IntegerField("Mult. Comisión")
	mult_caja = models.IntegerField("Mult. Caja")
	mult_estadistica = models.IntegerField("Mult. Estadísticas")
	libro_iva = models.BooleanField("Libro IVA", default=False)
	estadistica = models.BooleanField("Estadísticas", default=False)
	electronica = models.BooleanField("Electrónica", default=False)
	presupuesto = models.BooleanField("Presupuesto", default=False)
	pendiente = models.BooleanField("Pendiente", default=False)
	info_michelin_auto = models.BooleanField("Info. Michelin auto", 
												default=False)
	info_michelin_camion = models.BooleanField("Info. Michelin camión", 
												default=False)
	codigo_afip_a = models.CharField("Código AFIP A", max_length=3)
	codigo_afip_b = models.CharField("Código AFIP B", max_length=3)
	remito = models.BooleanField("Remito", default=False, blank=True, null=True)
	recibo = models.BooleanField("Recibo", default=False, blank=True, null=True)
	
	class Meta:
		db_table = 'comprobante_venta'
		verbose_name = 'Comprobante de Venta'
		verbose_name_plural = 'Comprobantes de Venta'
		ordering = ['nombre_comprobante_venta']
	
	def __str__(self):
		return self.nombre_comprobante_venta
	
	def clean(self):
		errors = {}
		
		if not self.codigo_comprobante_venta.isupper():
			errors.update({'codigo_comprobante_venta': 'Debe ingresar solo mayúsculas.'})
		
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


class ComprobanteCompra(ModeloBaseGenerico):
	id_comprobante_compra = models.AutoField(primary_key=True)
	estatus_comprobante_compra = models.BooleanField("Estatus", default=True,
													 choices=ESTATUS_GEN)
	codigo_comprobante_compra = models.CharField("Código comprobante",
												 max_length=3, unique=True)
	nombre_comprobante_compra = models.CharField("Nombre", max_length=30)
	nombre_impresion = models.CharField("Nombre Impresión", max_length=20,
									 	default="")
	mult_compra = models.IntegerField("Mult. Compra")
	mult_saldo = models.IntegerField("Mult. Saldo")
	mult_stock = models.IntegerField("Mult. Stock")
	mult_caja = models.IntegerField("Mult. IVA")
	libro_iva = models.BooleanField("Libreo IVA", default=False)
	codigo_afip_a = models.CharField("Código AFIP A", max_length=3)
	codigo_afip_b = models.CharField("Código AFIP B", max_length=3)
	codigo_afip_c = models.CharField("Código AFIP C", max_length=3)
	codigo_afip_m = models.CharField("Código AFIP M", max_length=3)
	
	class Meta:
		db_table = 'comprobante_compra'
		verbose_name = 'Comprobante de Compra'
		verbose_name_plural = 'Comprobantes de Compra'
		ordering = ['nombre_comprobante_compra']
	
	def __str__(self):
		return self.nombre_comprobante_compra
	
	def clean(self):
		errors = {}
		
		if not self.codigo_comprobante_compra.isupper():
			errors.update({'codigo_comprobante_compra': 'Debe ingresar solo mayúsculas.'})
		
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


class Provincia(ModeloBaseGenerico):
	id_provincia = models.AutoField(primary_key=True)
	estatus_provincia = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	codigo_provincia = models.CharField("Código", max_length=2, unique=True)
	nombre_provincia = models.CharField("Nombre", max_length=30)
	
	class Meta:
		db_table = 'provincia'
		verbose_name = ('Provincia')
		verbose_name_plural = ('Provincias')
		ordering = ['nombre_provincia']
	
	def __str__(self):
		return self.nombre_provincia


class Localidad(ModeloBaseGenerico):
	id_localidad = models.AutoField(primary_key=True)
	estatus_localidad = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	nombre_localidad = models.CharField("Nombre Localidad", max_length=30)
	codigo_postal = models.CharField("Código Postal", max_length=5)
	id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE,
									 verbose_name="Provincia")
	
	class Meta:
		db_table = 'localidad'
		verbose_name = ('Localidad')
		verbose_name_plural = ('Localidades')
		ordering = ['codigo_postal']
	
	def __str__(self):
		return self.nombre_localidad


class TipoDocumentoIdentidad(ModeloBaseGenerico):
	id_tipo_documento_identidad = models.AutoField(primary_key=True)
	estatus_tipo_documento_identidad = models.BooleanField("Estatus",
															 default=True,
															 choices=ESTATUS_GEN)
	nombre_documento_identidad = models.CharField("Nombre", max_length=20)
	tipo_documento_identidad = models.CharField("Tipo", max_length=4, 
												unique=True)
	codigo_afip = models.CharField("Código AFIP", max_length=2)
	ws_afip = models.CharField("WS AFIP", max_length=2)
	
	class Meta:
		db_table = 'tipo_documento_identidad'
		verbose_name = ('Tipo de Documento de Identidad')
		verbose_name_plural = ('Tipos de Documentos de Identidad')
		ordering = ['tipo_documento_identidad']
	
	def __str__(self):
		return self.nombre_documento_identidad


class TipoIva(ModeloBaseGenerico):
	id_tipo_iva = models.AutoField(primary_key=True)
	estatus_tipo_iva = models.BooleanField("Estatus", default=True,
											 choices=ESTATUS_GEN)
	codigo_iva = models.CharField("Código IVA", max_length=4, unique=True)
	nombre_iva = models.CharField("Nombre", max_length=25)
	discrimina_iva = models.BooleanField("Discrimina IVA", null=True,
										 blank=True)
	
	class Meta:
		db_table = 'tipo_iva'
		verbose_name = ('Tipo de IVA')
		verbose_name_plural = ('Tipos de IVA')
		ordering = ['nombre_iva']
	
	def __str__(self):
		return self.nombre_iva
	
	def clean(self):
		errors = {}
		
		if not self.codigo_iva.isupper():
			errors.update({'codigo_iva': 'Debe ingresar solo mayúsculas.'})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class TipoPercepcionIb(ModeloBaseGenerico):
	id_tipo_percepcion_ib = models.AutoField(primary_key=True)
	estatus_tipo_percepcion_ib = models.BooleanField("Estatus", default=True,
													 choices=ESTATUS_GEN)
	descripcion_tipo_percepcion_ib = models.CharField("Descripción",
														max_length=50)
	alicuota = models.DecimalField("Alícuota(%)", max_digits=4, decimal_places=2, 
								null=True, blank=True, default=0.00)
	monto = models.DecimalField("Monto", max_digits=15, decimal_places=2, 
								null=True, blank=True, default=0.00)
	minimo = models.DecimalField("Mínimo", max_digits=15, decimal_places=2, 
								null=True, blank=True, default=0.00)
	neto_total = models.BooleanField("Neto total", null=True, blank=True)
	
	class Meta:
		db_table = 'tipo_percepcion_ib'
		verbose_name = ('Tipo de Percepción IB')
		verbose_name_plural = ('Tipos de Percepción IB')
		ordering = ['descripcion_tipo_percepcion_ib']
	
	def __str__(self):
		return self.descripcion_tipo_percepcion_ib
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		alicuota_str = str(self.alicuota) if self.alicuota is not None else ""
		monto_str = str(self.monto) if self.monto is not None else ""
		minimo_str = str(self.minimo) if self.minimo is not None else ""
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$', alicuota_str):
			errors.update({'alicuota': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', monto_str):
			errors.update({'monto': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', minimo_str):
			errors.update({'minimo': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if errors:
			raise ValidationError(errors)


class TipoRetencionIb(ModeloBaseGenerico):
	id_tipo_retencion_ib = models.AutoField(primary_key=True)
	estatus_tipo_retencion_ib = models.BooleanField("Estatus", default=True,
													choices=ESTATUS_GEN)
	descripcion_tipo_retencion_ib = models.CharField("Descripción",
													 max_length=50)
	alicuota_inscripto = models.DecimalField("Alícuota Inscripto(%)", 
											max_digits=4, decimal_places=2, 
											null=True, blank=True, default=0.00)
	alicuota_no_inscripto = models.DecimalField("Alícuota No Inscripto(%)", 
												max_digits=4, decimal_places=2, 
												null=True, blank=True, default=0.00)
	monto = models.DecimalField("Monto", max_digits=15, decimal_places=2, 
								null=True, blank=True, default=0.00)
	minimo = models.DecimalField("Mínimo", max_digits=15, decimal_places=2, 
								null=True, blank=True, default=0.00)
	
	class Meta:
		db_table = 'tipo_retencion_ib'
		verbose_name = ('Tipo de Retención IB')
		verbose_name_plural = ('Tipos de Retención IB')
		ordering = ['descripcion_tipo_retencion_ib']
	
	def __str__(self):
		return self.descripcion_tipo_retencion_ib
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		alicuota_inscripto_str = str(self.alicuota_inscripto) if self.alicuota_inscripto is not None else ""
		alicuota_no_inscripto_str = str(self.alicuota_no_inscripto) if self.alicuota_no_inscripto is not None else ""
		monto_str = str(self.monto) if self.monto is not None else ""
		minimo_str = str(self.minimo) if self.minimo is not None else ""
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$', alicuota_inscripto_str):
			errors.update({'alicuota_inscripto': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$', alicuota_no_inscripto_str):
			errors.update({'alicuota_no_inscripto': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', monto_str):
			errors.update({'monto': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', minimo_str):
			errors.update({'minimo': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if errors:
			raise ValidationError(errors)


class Operario(ModeloBaseGenerico):
	id_operario = models.AutoField(primary_key=True)
	estatus_operario = models.BooleanField("Estatus", default=True,
											 choices=ESTATUS_GEN)
	nombre_operario = models.CharField("Nombre", max_length=50)
	telefono_operario = models.CharField("Teléfono", max_length=15)
	email_operario = models.CharField("Correo", max_length=50)
	
	class Meta:
		db_table = 'operario'
		verbose_name = ('Operario')
		verbose_name_plural = ('Operarios')
		ordering = ['nombre_operario']
	
	def __str__(self):
		return self.nombre_operario


class MedioPago(ModeloBaseGenerico):
	id_medio_pago = models.AutoField(primary_key=True)
	estatus_medio_pago = models.BooleanField("Estatus", default=True,
											 choices=ESTATUS_GEN)
	nombre_medio_pago = models.CharField(max_length=30)
	condicion_medio_pago = models.IntegerField("Condición Pago", 
											default=True,
											choices=CONDICION_PAGO)
	plazo_medio_pago = models.IntegerField("Plazo medio de Pago")
	
	class Meta:
		db_table = 'medio_pago'
		verbose_name = 'Medio de Pago'
		verbose_name_plural = 'Medios de Pago'
		ordering = ['nombre_medio_pago']
	
	def __str__(self):
		return self.nombre_medio_pago
	
	@property
	def condicion_medio_pago_display(self):
		return self.get_condicion_medio_pago_display()


class PuntoVenta(ModeloBaseGenerico):
	id_punto_venta = models.AutoField(primary_key=True)
	estatus_punto_venta = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	id_sucursal = models.ForeignKey('Sucursal', on_delete=models.PROTECT,
									verbose_name="Sucursal",
									null=True, blank=True)
	punto_venta = models.CharField("Punto de Venta", max_length=5)
	descripcion_punto_venta = models.CharField("Descripción Pto. Venta",
												max_length=50, 
												null=True, blank=True)
	
	class Meta:
		db_table = 'punto_venta'
		verbose_name = 'Punto de Venta'
		verbose_name_plural = 'Puntos de Venta'
		ordering = ['punto_venta']
	
	def __str__(self):
		return f'{self.id_sucursal} {self.punto_venta}'
	
	def clean(self):
		errors = {}
		
		#-- Limpiar y formatear el valor de `punto_venta` con ceros a la izquierda.
		if self.punto_venta:
			try:
				#-- Convertir a entero y luego a string para evitar ceros iniciales no deseados.
				self.punto_venta = str(int(self.punto_venta)).zfill(5)
			except ValueError:
				errors.update({'punto_venta': 'Debe ser un número entero positivo.'})
		
		#-- Validar el formato después de formatear el valor.
		if not re.match(r'^\d{5}$', self.punto_venta):
			errors.update({'punto_venta': 'Debe indicar un número de hasta 5 dígitos.'})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class AlicuotaIva(ModeloBaseGenerico):
	id_alicuota_iva = models.AutoField(primary_key=True)
	estatus_alicuota_iva = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)
	codigo_alicuota = models.CharField("Cód. Alíc. IVA", max_length=4, unique=True)
	alicuota_iva = models.DecimalField("Alícuota IVA(%)", unique=True, 
										max_digits=5, decimal_places=2, 
										default=0.0)
	descripcion_alicuota_iva = models.CharField("Descripción Alíc. IVA", 
											max_length=50, null=True, 
											blank=True)
	
	class Meta:
		db_table = 'codigo_alicuota'
		verbose_name = 'Alícuota IVA'
		verbose_name_plural = 'Alícuotas IVA'
		ordering = ['alicuota_iva']
	
	def __str__(self):
		return f"{self.alicuota_iva:3.2f}%"
	
	def clean(self):
		errors = {}
		
		#-- Limpiar y formatear el valor de `codigo_alicuota` con ceros a la izquierda.
		if self.codigo_alicuota:
			try:
				#-- Convertir a entero y luego a string para evitar ceros iniciales no deseados.
				self.codigo_alicuota = str(int(self.codigo_alicuota)).zfill(4)
			except ValueError:
				errors.update({'codigo_alicuota': 'Debe ser un número entero positivo.'})
		
		#-- Validar el formato después de formatear el valor.
		if not re.match(r'^\d{4}$', self.codigo_alicuota):
			errors.update({'codigo_alicuota': 'Debe indicar un número de hasta 4 dígitos.'})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class Banco(ModeloBaseGenerico):
	id_banco = models.AutoField(primary_key=True)
	estatus_banco = models.BooleanField("Estatus", default=True,
										choices=ESTATUS_GEN)
	nombre_banco = models.CharField("Nombre Banco", max_length=50,
										  	null=True, blank=True)
	codigo_banco = models.SmallIntegerField("Código Banco")
	cuit_banco = models.IntegerField("CUIT")
	
	class Meta:
		db_table = 'banco'
		verbose_name = 'Banco'
		verbose_name_plural = 'Bancos'
		ordering = ['nombre_banco']
	
	def __str__(self):
		return self.nombre_banco
	
	def clean(self):
		super().clean()
		
		#-- Diccionario contenedor de errores.
		errors = {}
		
		try:
			validar_cuit(self.cuit_banco)
		except ValidationError as e:
			#-- Agrego el error al dicciobario errors.
			errors['cuit_banco'] = e.messages
		
		if not self.nombre_banco:
			errors.update({'nombre_banco': "Debe indicar un Nombre de Banco."})
		
		if errors:
			#-- Lanza el conjunto de excepciones.
			raise ValidationError(errors)


class CuentaBanco(ModeloBaseGenerico):
	id_cuenta_banco = models.AutoField(primary_key=True)
	estatus_cuenta_banco = models.BooleanField("Estatus", default=True,
										choices=ESTATUS_GEN)
	id_banco = models.ForeignKey(Banco, on_delete=models.PROTECT,
							  	verbose_name="Banco", null=True, blank=True)
	numero_cuenta = models.CharField("Número Cuenta", max_length=15,
									null=True, blank=True)
	tipo_cuenta = models.SmallIntegerField("Tipo de Cta.", choices=TIPO_CUENTA,
										null=True, blank=True)
	cbu = models.CharField("CBU", max_length=22, null=True, blank=True)
	sucursal = models.IntegerField("Sucursal",
									null=True, blank=True)
	codigo_postal = models.IntegerField("Código Postal",
										null=True, blank=True)
	codigo_imputacion = models.IntegerField("Cód. Imputación",
									null=True, blank=True)
	tope_negociacion = models.DecimalField("Tope Negociación", max_digits=12, decimal_places=2,
								null=True, blank=True, default=0.00)
	reporte_reques = models.CharField("Reporte Cheques", max_length=20,
								null=True, blank=True)
	id_proveedor = models.ForeignKey("Proveedor", on_delete=models.PROTECT,
									verbose_name="Proveedor", null=True, blank=True,)
	id_moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT,
									verbose_name="Moneda", null=True, blank=True)
	
	class Meta:
		db_table = 'cuenta_banco'
		verbose_name = ('Cuentas Banco')
		verbose_name_plural = ('Cuentas de Bancos')
		ordering = ['numero_cuenta']
	
	def __str__(self):
		return self.numero_cuenta
	
	def clean(self):
		super().clean()
		
		# Diccionario contenedor de errores
		errors = {}
		
		if not self.numero_cuenta:
			errors.update({'numero_cuenta': "Debe indicar un Número de Cuenta."})
		
		if not self.id_banco:
			errors.update({'id_banco': "Debe indicar un Banco."})
		
		if not self.id_moneda:
			errors.update({'id_moneda': "Debe indicar una Moneda."})
		
		if not self.tipo_cuenta:
			errors.update({'tipo_cuenta': "Debe indicar un Tipo de Cuenta."})
		
		if errors:
			#-- Lanza el conjunto de excepciones.
			raise ValidationError(errors)
	
	@property
	def tipo_cuenta_display(self):
		return self.get_tipo_cuenta_display()


class Tarjeta(ModeloBaseGenerico):
	id_tarjeta = models.AutoField(primary_key=True)
	estatus_tarjeta = models.BooleanField("Estatus", default=True,
										choices=ESTATUS_GEN)
	nombre_tarjeta = models.CharField("Nombre Tarjeta", max_length=30,
								   null=True, blank=True)
	imputacion = models.IntegerField("Cód. Imputación",
									null=True, blank=True)
	banco_acreditacion = models.IntegerField("Banco",
									null=True, blank=True)
	propia = models.BooleanField("Propia", default=False)
	
	class Meta:
		db_table = 'tarjeta'
		verbose_name = ('Tarjeta')
		verbose_name_plural = ('Tarjetas')
		ordering = ['nombre_tarjeta']    
	
	def __str__(self):
		return self.nombre_tarjeta
	
	def clean(self):
		errors = {}
		
		if not self.nombre_tarjeta:
			errors.update({'nombre_tarjeta': "Debe indicar un nombre."})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class CodigoRetencion(ModeloBaseGenerico):
	# id_codigo_retencion = models.CharField(primary_key=True, max_length=2)
	id_codigo_retencion = models.AutoField(primary_key=True)
	estatus_cod_retencion = models.BooleanField("Estatus", default=True,
												choices=ESTATUS_GEN)
	nombre_codigo_retencion = models.CharField("Nombre Cód. Ret.", max_length=30,
												null=True, blank=True)
	imputacion = models.IntegerField("Cód. Imputación", default=0,
									null=True, blank=True)
	
	class Meta:
		db_table = 'codigo_retencion'
		verbose_name = ('Codigo Retención')
		verbose_name_plural = ('Codigos Retención')
		ordering = ['nombre_codigo_retencion']
	
	def __str__(self):
		return self.nombre_codigo_retencion
	
	def clean(self):
		errors = {}
		
		if not self.nombre_codigo_retencion:
			errors.update({'nombre_codigo_retencion': "Debe indicar un nombre."})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class ConceptoBanco(ModeloBaseGenerico):
	id_concepto_banco = models.AutoField(primary_key=True)
	estatus_concepto_banco = models.BooleanField("Estatus", default=True,
												choices=ESTATUS_GEN)
	nombre_concepto_banco = models.CharField("Descripción", max_length=30,
										  	null=True, blank=True)
	factor = models.IntegerField("Factor")
	
	class Meta:
		db_table = 'concepto_banco'
		verbose_name = 'Concepto Bancario'
		verbose_name_plural = 'Conceptos Bancarios'
		ordering = ['nombre_concepto_banco']
	
	def __str__(self):
		return self.nombre_concepto_banco
	
	def clean(self):
		errors = {}
		
		if not self.nombre_concepto_banco:
			errors.update({'nombre_concepto_banco': "Debe indicar un nombre."})
		
		if self.factor != -1 and self.factor != 0 and self.factor != 1:
			errors.update({'factor': "Los valores permitidos son: -1, 0 y 1"})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class MarketingOrigen(ModeloBaseGenerico):
	id_marketing_origen = models.AutoField(primary_key=True)
	estatus_marketing_origen = models.BooleanField("Estatus", default=True,
												choices=ESTATUS_GEN)
	nombre_marketing_origen = models.CharField("Descripción", max_length=30,
										  	null=True, blank=True)
	
	class Meta:
		db_table = 'marketing_origen'
		verbose_name = 'Marketing Origen'
		verbose_name_plural = 'Marketing Origen'
		ordering = ['id_marketing_origen']
	
	def __str__(self):
		return self.nombre_marketing_origen
	
	def clean(self):
		errors = {}
		
		if not self.nombre_marketing_origen:
			errors.update({'nombre_marketing_origen': "Debe indicar una Descripción."})
		
		if errors:
			raise ValidationError(errors)
		
		return super().clean()


class Leyenda(ModeloBaseGenerico):
	id_leyenda = models.AutoField(
		primary_key=True
	)
	estatus_leyenda = models.BooleanField(
		"Estatus",
		default=True,
		choices=ESTATUS_GEN
	)
	nombre_leyenda = models.CharField(
		"Nombre",
		max_length=30,
		null=True, blank=True
	)
	leyenda = models.CharField(
		"Leyenda",
		max_length=250,
		null=True, blank=True
	)
	
	class Meta:
		db_table = 'leyenda'
		verbose_name = 'Leyenda'
		verbose_name_plural = 'Leyendas'
		ordering = ['nombre_leyenda']
	
	def __str__(self):
		return self.nombre_leyenda
