# neumatic\apps\maestros\models\parametro_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
# from .empresa_models import Empresa
from entorno.constantes_base import ESTATUS_GEN


class Parametro(ModeloBaseGenerico):
	id_parametro = models.AutoField(primary_key=True)  # Clave primaria
	estatus_parametro = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)  # Estatus del parámetro
	id_empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE,
								   verbose_name="Empresa")
	
	interes = models.DecimalField("Intereses(%)", max_digits=6,
								  decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(99)])
	interes_dolar = models.DecimalField("Intereses Dólar(%)", max_digits=6,
										decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(99)])
	cotizacion_dolar = models.DecimalField("Cotización Dólar",
										   max_digits=18, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(9999999999999999)])
	
	dias_vencimiento = models.IntegerField("Días Vcto.",
										   validators=[MinValueValidator(0),
													   MaxValueValidator(999)])
	descuento_maximo = models.DecimalField("Descuento Máximo(%)",
										   max_digits=6, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(99)])
	
	class Meta:
		db_table = 'parametro'
		verbose_name = 'Parámetro'
		verbose_name_plural = 'Parámetros'
		ordering = ['id_empresa']


''' Solo para cuadrar plantilla del form
	
	estatus_parametro = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)  # Estatus del parámetro
	id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
	
	interes = models.DecimalField("Intereses", max_digits=6, decimal_places=2)
	interes_dolar = models.DecimalField("Intereses Dólar", max_digits=6, decimal_places=2)
	cotizacion_dolar = models.DecimalField("Cotización Dólar", max_digits=18, decimal_places=2)
	dias_vencimiento = models.IntegerField("Días Vcto.", validators=[MinValueValidator(1), MaxValueValidator(999)])
	descuento_maximo = models.DecimalField("Intereses Dólar", max_digits=6, decimal_places=2)

'''
