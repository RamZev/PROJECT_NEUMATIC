# neumatic\apps\maestros\models\producto_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
from .base_models import (ProductoFamilia, ProductoMarca, ProductoModelo)
from entorno.constantes_base import ESTATUS_GEN, TIPO_PRODUCTO_SERVICIO

class Producto(ModeloBaseGenerico):
	id_producto = models.AutoField(primary_key=True)
	estatus_producto = models.BooleanField("Estatus", default=True, 
										   choices=ESTATUS_GEN)
	codigo_producto = models.IntegerField("Código producto")
	tipo_producto = models.CharField("Tipo producto", max_length=1, choices=TIPO_PRODUCTO_SERVICIO)
	id_familia = models.ForeignKey(ProductoFamilia, on_delete=models.CASCADE,
								   verbose_name="Familia")
	id_marca = models.ForeignKey(ProductoMarca, on_delete=models.CASCADE, 
								 verbose_name="Marca")
	id_modelo = models.ForeignKey(ProductoModelo, on_delete=models.CASCADE, 
								  verbose_name="Modelo")
	cai = models.CharField("CAI", max_length=20, null=True, blank=True)  # CAI del producto
	medida = models.CharField("Medida", max_length=15)  # Medida del producto
	segmento = models.CharField("Segmento", max_length=3)  # Segmento del producto
	nombre_producto = models.CharField("Nombre producto", max_length=50)  # Nombre del producto
	unidad = models.IntegerField("Unidad", null=True, blank=True)
	fecha_fabricacion = models.CharField("Fecha fabricación", max_length=6, 
									null=True, blank=True)  # Fecha de fabricación
	costo = models.DecimalField("Costo", max_digits=15, decimal_places=2,
							default=0.00, null=True, blank=True)  # Costo del producto
	alicuota_iva = models.DecimalField("Alícuota IVA", max_digits=4, 
									   decimal_places=2, default=0.00,
									   null=True, blank=True)  # Alicuota IVA
	precio = models.DecimalField("Precio", max_digits=15, decimal_places=2,
							default=0.00, null=True, blank=True)  # Precio del producto
	stock = models.IntegerField("Stock", null=True, blank=True)  # Stock disponible
	minimo = models.IntegerField("Stock mínimo", null=True, blank=True)  # Stock mínimo
	descuento = models.DecimalField("Descuento", max_digits=4, 
								 decimal_places=2, default=0.00,
								 null=True, blank=True)  # Descuento aplicable
	despacho_1 = models.CharField("Despacho 1", max_length=16, 
							   null=True, blank=True)  # Dirección de despacho 1
	despacho_2 = models.CharField("Despacho 2", max_length=16, 
							   null=True, blank=True)  # Dirección de despacho 2
	descripcion_producto = models.CharField("Descripción", max_length=50)  # Descripción del producto
	carrito = models.BooleanField("Carrito")  # Indica si el producto está en el carrito
	
	def __str__(self):
		return self.nombre_producto
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		fecha_fabricacion_str = str(self.fecha_fabricacion) if self.fecha_fabricacion else ""
		unidad_str = str(self.unidad) if self.unidad else ""
		costo_str = str(self.costo) if self.costo else ""
		descuento_str = str(self.descuento) if self.descuento else ""
		dalicuota_iva_str = str(self.alicuota_iva) if self.alicuota_iva else ""
		
		if not re.match(r'^\d{1,5}$', str(self.codigo_producto)):
			errors.update({'codigo_producto': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 5.'})
		
		if not re.match(r'^$|^20\d{2}(0[1-9]|1[0-2])$', fecha_fabricacion_str):
			errors.update({'fecha_fabricacion': 'Debe indicar el dato en el formato AAAAMM (AAAA para el año, MM para el mes). Indicar año y mes válidos. El año debe iniciar en 20'})
		
		if not re.match(r'^[1-9]\d{0,2}$|^0$|^$', unidad_str):
			errors.update({'unidad': 'El valor debe ser un número entero positivo, con hasta 3 dígitos, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$', costo_str):
			errors.update({'costo': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$', descuento_str):
			errors.update({'descuento': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$|^$', dalicuota_iva_str):
			errors.update({'alicuota_iva': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		#-- Valida que mínimo sea: 0.01 y hasta 99.99
		# if not re.match(r'^(0?[1-9]\.\d{2}|[1-9]\d\.\d{2}|0?0\.[1-9]\d|0?0\.0[1-9])$', str(self.alicuota_iva)):
		# 	errors.update({'alicuota_iva': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'producto'
		verbose_name = 'Producto'
		verbose_name_plural = 'Productos'
		ordering = ['nombre_producto']
