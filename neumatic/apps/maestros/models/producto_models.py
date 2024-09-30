# neumatic\apps\maestros\models\producto_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
from .base_models import (ProductoFamilia, ProductoMarca,
                          ProductoModelo)
from entorno.constantes_base import ESTATUS_GEN, TIPO_PRODUCTO_SERVICIO

class Producto(ModeloBaseGenerico):
    id_producto = models.AutoField(primary_key=True)
    estatus_producto = models.BooleanField("Estatus", default=True, 
                                           choices=ESTATUS_GEN)
    codigo_producto = models.IntegerField("Código producto", 
                                          validators=[MinValueValidator(1), 
                                                      MaxValueValidator(999)])
    tipo_producto = models.CharField("Tipo producto", max_length=1, choices=TIPO_PRODUCTO_SERVICIO)
    id_familia = models.ForeignKey(ProductoFamilia, on_delete=models.CASCADE,                          #-- no está en captura
                                   verbose_name="Familia")
    id_marca = models.ForeignKey(ProductoMarca, on_delete=models.CASCADE, 
                                 verbose_name="Marca")
    id_modelo = models.ForeignKey(ProductoModelo, on_delete=models.CASCADE, 
                                  verbose_name="Modelo")
    cai = models.CharField("CAI", max_length=20)  # CAI del producto
    medida = models.CharField("Medida", max_length=15)  # Medida del producto
    segmento = models.CharField("Segmento", max_length=3)  # Segmento del producto
    nombre_producto = models.CharField("Nombre producto", max_length=50)  # Nombre del producto
    unidad = models.IntegerField("Unidad",                                                             #-- no está en captura
                                 validators=[MinValueValidator(1), 
                                             MaxValueValidator(999)])
    fecha_fabricacion = models.CharField("Fecha fabricación", max_length=6)  # Fecha de fabricación
    costo = models.DecimalField("Costo", max_digits=18, decimal_places=2)  # Costo del producto
    alicuota_iva = models.DecimalField("Alícuota IVA", max_digits=6, 
                                       decimal_places=2)  # Alicuota IVA
    precio = models.DecimalField("Precio", max_digits=18, decimal_places=2)  # Precio del producto
    stock = models.IntegerField("Stock",                                                               #-- no está en captura
                                validators=[MinValueValidator(1), 
                                            MaxValueValidator(999)])  # Stock disponible
    minimo = models.IntegerField("Stock mínimo", 
                                 validators=[MinValueValidator(1), 
                                             MaxValueValidator(999)])  # Stock mínimo
    descuento = models.DecimalField("Descuento", max_digits=6, 
                                    decimal_places=2)  # Descuento aplicable
    despacho_1 = models.CharField("Despacho 1", max_length=16)  # Dirección de despacho 1
    despacho_2 = models.CharField("Despacho 2", max_length=16)  # Dirección de despacho 2
    descripcion_producto = models.CharField("Descripción", max_length=50)  # Descripción del producto  #-- no está en captura
    carrito = models.BooleanField("Carrito")  # Indica si el producto está en el carrito               #-- no está en captura
    
    def __str__(self):
        return self.nombre_producto
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre_producto']


''' Solo para cuadrar plantilla del form
	Línea 1
		estatus_producto = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
		codigo_producto = models.IntegerField("Código producto", validators=[MinValueValidator(1), MaxValueValidator(999)])
		nombre_producto = models.CharField("Nombre producto", max_length=50)  # Nombre del producto
		tipo_producto = models.CharField("Tipo producto", choices=TIPO)
    
	Línea 2
		id_familia = models.ForeignKey(ProductoFamilia, on_delete=models.CASCADE, verbose_name="Familia")
		id_marca = models.ForeignKey(ProductoMarca, on_delete=models.CASCADE, verbose_name="Marca")
		id_modelo = models.ForeignKey(ProductoModelo, on_delete=models.CASCADE, verbose_name="Modelo")
    
	Línea 3
		cai = models.CharField("CAI", max_length=20)  # CAI del producto
		medida = models.CharField("Medida", max_length=15)  # Medida del producto
		segmento = models.CharField("Segmento", max_length=3)  # Segmento del producto
		unidad = models.IntegerField("Unidad", validators=[MinValueValidator(1), MaxValueValidator(999)])                                  #-- no está en captura
		fecha_fabricacion = models.CharField("Fecha fabricación", max_length=6)  # Fecha de fabricación
    
	Línea 4
		costo = models.DecimalField("Costo", max_digits=18, decimal_places=2)  # Costo del producto
		alicuota_iva = models.DecimalField("Alícuota IVA", max_digits=6, decimal_places=2)  # Alicuota IVA
		precio = models.DecimalField("Precio", max_digits=18, decimal_places=2)  # Precio del producto
		descuento = models.DecimalField("Descuento", max_digits=6, decimal_places=2)  # Descuento aplicable
    
	Línea 5
		stock = models.IntegerField("Stock", validators=[MinValueValidator(1), MaxValueValidator(999)])  # Stock disponible                #-- no está en captura
		minimo = models.IntegerField("Stock mínimo", validators=[MinValueValidator(1), MaxValueValidator(999)])  # Stock mínimo
		despacho_1 = models.CharField("Despacho 1", max_length=16)  # Dirección de despacho 1
		despacho_2 = models.CharField("Despacho 2", max_length=16)  # Dirección de despacho 2
    
	Línea 6
		descripcion_producto = models.CharField("Descripción", max_length=50)  # Descripción del producto                                  #-- no está en captura
		carrito = models.BooleanField("Carrito")  # Indica si el producto está en el carrito                                               #-- no está en captura
'''