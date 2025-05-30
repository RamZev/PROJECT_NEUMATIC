# neumatic\apps\maestros\models\producto_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
from .base_gen_models import ModeloBaseGenerico
from .base_models import (ProductoFamilia, ProductoMarca, ProductoModelo, ProductoCai, AlicuotaIva)
from entorno.constantes_base import ESTATUS_GEN, TIPO_PRODUCTO_SERVICIO

from .base_models import ProductoDeposito, ProductoStock, ProductoMinimo

class Producto(ModeloBaseGenerico):
	id_producto = models.AutoField(primary_key=True)
	estatus_producto = models.BooleanField("Estatus", default=True, 
										   choices=ESTATUS_GEN)
	codigo_producto = models.CharField("Código producto", max_length=7, null=True, blank=True)
	tipo_producto = models.CharField("Tipo producto", max_length=1, choices=TIPO_PRODUCTO_SERVICIO)
	id_familia = models.ForeignKey(ProductoFamilia, on_delete=models.PROTECT,
								   verbose_name="Familia")
	id_marca = models.ForeignKey(ProductoMarca, on_delete=models.PROTECT, 
								 verbose_name="Marca")
	id_modelo = models.ForeignKey(ProductoModelo, on_delete=models.PROTECT, 
								  verbose_name="Modelo")
	id_cai = models.ForeignKey(ProductoCai, on_delete=models.PROTECT,
								null=True, blank=True, verbose_name="CAI")  # CAI del producto
	cai = models.CharField("Medida", max_length=21, null=True, blank=True)  # CAI del producto
	medida = models.CharField("Medida", max_length=15)  # Medida del producto
	segmento = models.CharField("Segmento", max_length=3)  # Segmento del producto
	nombre_producto = models.CharField("Nombre producto", max_length=50)  # Nombre del producto
	unidad = models.IntegerField("Unidad", null=True, blank=True, default=0)
	fecha_fabricacion = models.CharField("Fecha fabricación", max_length=6, 
									null=True, blank=True)  # Fecha de fabricación
	costo = models.DecimalField("Costo", max_digits=15, decimal_places=2,
							default=0.00, null=True, blank=True)  # Costo del producto
	alicuota_iva = models.DecimalField("Alícuota IVA", max_digits=4, 
									   decimal_places=2, default=0.00,
									   null=True, blank=True)  # Alicuota IVA
	id_alicuota_iva = models.ForeignKey(AlicuotaIva, on_delete=models.PROTECT, verbose_name="Alíc. IVA", default=1)
	precio = models.DecimalField("Precio", max_digits=15, decimal_places=2,
							default=0.00, null=True, blank=True)  # Precio del producto
	stock = models.IntegerField("Stock", null=True, blank=True)  # Stock disponible
	minimo = models.IntegerField("Stock mínimo", null=True, default=0)  # Stock mínimo
	descuento = models.DecimalField("Descuento", max_digits=4, 
								 decimal_places=2, default=0.00,
								 null=True, blank=True)  # Descuento aplicable
	despacho_1 = models.CharField("Despacho 1", max_length=16, 
							   null=True, blank=True)  # Dirección de despacho 1
	despacho_2 = models.CharField("Despacho 2", max_length=16, 
							   null=True, blank=True)  # Dirección de despacho 2
	descripcion_producto = models.CharField("Descripción", max_length=50)  # Descripción del producto
	carrito = models.BooleanField("Carrito")  # Indica si el producto está en el carrito
	
	class Meta:
		db_table = 'producto'
		verbose_name = 'Producto'
		verbose_name_plural = 'Productos'
		ordering = ['nombre_producto']
	
	def __str__(self):
		return self.nombre_producto
	
	def save(self, *args, **kwargs):
		#-- Identificar si el registro es nuevo antes de llamar a super().
		es_nuevo = self.pk is None
		
		#-- Llamar al método save original para que se guarde el registro y se asigne el ID.
		super().save(*args, **kwargs)
		
		#-- Si no tiene código, asigna el ID con ceros a la izquierda.
		if not self.codigo_producto:
			self.codigo_producto = f'{self.id_producto:07d}'  # 7 dígitos con ceros a la izquierda
			#-- Guarda nuevamente el registro con el código asignado.
			super(Producto, self).save(*args, **kwargs)	
		
		#-- Obtén todos los depósitos.
		depositos = ProductoDeposito.objects.all()
		
		#-- Registra un ProductoStock para cada depósito si tipo_producto es Producto.
		#-- Solo registrar en ProductoStock y ProductoMinimo si es nuevo y tipo_producto es "Producto"
		if es_nuevo and self.tipo_producto == 'p':
			for deposito in depositos:
				ProductoStock.objects.get_or_create(
					id_producto=self,             # Producto actual
					id_deposito=deposito,         # Depósito en la iteración
					defaults={
						'stock': self.stock or 0,           # Valor de stock de Producto o 0
						'minimo': self.minimo or 0,         # Valor de mínimo de Producto o 0
						'fecha_producto_stock': timezone.now()  # Fecha actual
					}
				)
			
				#-- Si cai tiene datos, registra un ProductoMinimo para cada depósito.
				if self.cai:
					ProductoMinimo.objects.get_or_create(
						id_producto=self,              # Producto actual
						cai=self.cai,                  # CAI del producto
						id_deposito=deposito,          # Depósito en la iteración
						defaults={
							'minimo': self.minimo or 0  # Valor de mínimo de Producto o 0
						}
					)
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		fecha_fabricacion_str = str(self.fecha_fabricacion) if self.fecha_fabricacion else ""
		unidad_str = str(self.unidad) if self.unidad else ""
		costo_str = str(self.costo) if self.costo else ""
		descuento_str = str(self.descuento) if self.descuento else ""
		
		if not re.match(r'^$|^20\d{2}(0[1-9]|1[0-2])$', fecha_fabricacion_str):
			errors.update({'fecha_fabricacion': 'Debe indicar el dato en el formato AAAAMM (AAAA para el año, MM para el mes). Indicar año y mes válidos. El año debe iniciar en 20'})
		
		if not re.match(r'^[1-9]\d{0,2}$|^0$|^$', unidad_str):
			errors.update({'unidad': 'El valor debe ser un número entero positivo, con hasta 3 dígitos, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$', costo_str):
			errors.update({'costo': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$', descuento_str):
			errors.update({'descuento': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if errors:
			raise ValidationError(errors)
