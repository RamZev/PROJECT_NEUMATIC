# neumatic\apps\maestros\models\vendedor_comision_models.py
from django.db import models
from django.core.exceptions import ValidationError

from datetime import date

from .base_gen_models import ModeloBaseGenerico
from ..models.vendedor_models import Vendedor
from ..models.base_models import ProductoMarca, ProductoFamilia
from entorno.constantes_base import ESTATUS_GEN


class VendedorComision(ModeloBaseGenerico):
	id_vendedor_comision = models.AutoField(primary_key=True)
	estatus_vendedor_comision = models.BooleanField(
		"Estatus", default=True, 
		choices=ESTATUS_GEN
	)
	id_vendedor = models.ForeignKey(
		Vendedor, 
		on_delete=models.PROTECT,
		verbose_name="Vendedor"
	)
	fecha_registro = models.DateField(
		"Fecha Registro", default=date.today
	)
	
	def __str__(self):
		return f'{self.id_vendedor}'
	
	
	class Meta:
		db_table = "vendedor_comision"
		verbose_name = ('Vendedor Comisión')
		verbose_name_plural = ('Vendedor Comisiones')


class DetalleVendedorComision(ModeloBaseGenerico):
	id_detalle_vendedor_comision = models.AutoField(primary_key=True)
	id_vendedor_comision = models.ForeignKey(
		VendedorComision,
		on_delete=models.CASCADE,
	)
	id_familia = models.ForeignKey(
		ProductoFamilia, 
		on_delete=models.PROTECT,
		verbose_name="Familia"
	)
	id_marca = models.ForeignKey(
		ProductoMarca, 
		on_delete=models.PROTECT,
		verbose_name="Marca"
	)
	comision_porcentaje = models.DecimalField(
		verbose_name="% Comisión",
		max_digits=4,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0)
	
	def __str__(self):
		return f'{self.id_detalle_vendedor_comision}'
	
	
	class Meta:
		db_table = "detalle_vendedor_comision"
		verbose_name = ('Detalle Vendedor Comisión')
		verbose_name_plural = ('Detalles Vendedor Comisiones')
