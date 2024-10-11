# neumatic\apps\maestros\models\numero_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
# from .sucursal_models import Sucursal
from entorno.constantes_base import ESTATUS_GEN


class Numero(ModeloBaseGenerico):
	id_numero = models.AutoField(primary_key=True)
	estatus_numero = models.BooleanField("Estatus", default=True, 
										 choices=ESTATUS_GEN)
	id_sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE, 
									verbose_name="Sucursal")
	punto_venta = models.IntegerField("Punto de Venta", 
								   validators=[MinValueValidator(1), 
					   						   MaxValueValidator(999)])
	comprobante = models.CharField("Comprobante", max_length=3)
	letra = models.CharField("Letra", max_length=1)
	numero = models.IntegerField("Número", 
							  	 validators=[MinValueValidator(1), 
					   						 MaxValueValidator(9999999999999)])
	lineas = models.IntegerField("Líneas", 
							  	 validators=[MinValueValidator(1), 
					   						 MaxValueValidator(999)])
	copias = models.IntegerField("Copias", 
							  	 validators=[MinValueValidator(1), 
					   						 MaxValueValidator(999)])
	
	def __str__(self):
		return self.comprobante
	
	
	class Meta:
		db_table = 'numero'
		verbose_name = 'Número de Comprobante'
		verbose_name_plural = 'Números de Comprobante'
		ordering = ['punto_venta', 'comprobante']


''' Solo para cuadrar plantilla del form
	
	Línea 1
		estatus_numero = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
		id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, verbose_name="Sucursal")
		punto_venta = models.IntegerField("Punto de Venta", validators=[MinValueValidator(1), MaxValueValidator(999)])
	
	Línea 2
		comprobante = models.CharField("Comprobante", max_length=3)
		letra = models.CharField("Letra", max_length=1)
		numero = models.IntegerField("Número", validators=[MinValueValidator(1), MaxValueValidator(999)])
		lineas = models.IntegerField("Líneas", validators=[MinValueValidator(1), MaxValueValidator(999)])
		copias = models.IntegerField("Copias", validators=[MinValueValidator(1), MaxValueValidator(999)])
	
'''
