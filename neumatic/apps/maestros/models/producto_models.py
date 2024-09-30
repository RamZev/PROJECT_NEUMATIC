# neumatic\apps\maestros\models\producto_models.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .base_models import (ProductoFamilia, ProductoMarca,
                          ProductoModelo)
from entorno.entorno_base import ESTATUS_GEN


class Producto(ModeloBaseGenerico):
    id_producto = models.AutoField(primary_key=True)
    estatus_producto = models.BooleanField("Estatus", default=True, 
                                           choices=ESTATUS_GEN)
    codigo_producto = models.IntegerField()
    tipo_producto = models.CharField(max_length=1)
    id_familia = models.ForeignKey(ProductoFamilia, on_delete=models.CASCADE)
    id_marca = models.ForeignKey(ProductoMarca, on_delete=models.CASCADE)
    id_modelo = models.ForeignKey(ProductoModelo, on_delete=models.CASCADE)
    cai = models.CharField(max_length=20)  # CAI del producto
    medida = models.CharField(max_length=15)  # Medida del producto
    segmento = models.CharField(max_length=3)  # Segmento del producto
    nombre_producto = models.CharField(max_length=50)  # Nombre del producto
    unidad = models.IntegerField()
    fecha_fabricacion = models.CharField(max_length=6)  # Fecha de fabricación
    costo = models.DecimalField(max_digits=18, decimal_places=2)  # Costo del producto
    alicuota_iva = models.DecimalField(max_digits=6, decimal_places=2)  # Alicuota IVA
    precio = models.DecimalField(max_digits=18, decimal_places=2)  # Precio del producto
    stock = models.IntegerField()  # Stock disponible
    minimo = models.IntegerField()  # Stock mínimo
    descuento = models.DecimalField(max_digits=6, decimal_places=2)  # Descuento aplicable
    despacho_1 = models.CharField(max_length=16)  # Dirección de despacho 1
    despacho_2 = models.CharField(max_length=16)  # Dirección de despacho 2
    descripcion_producto = models.CharField(max_length=50)  # Descripción del producto
    carrito = models.BooleanField()  # Indica si el producto está en el carrito
    
    def __str__(self):
        return self.nombre_producto
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre_producto']
