# neumatic\apps\maestros\models\vendedor_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
# from .base_models import *
# from .sucursal_models import Sucursal
from entorno.constantes_base import ESTATUS_GEN, TIPO_VENTA


class Vendedor(ModeloBaseGenerico):
	id_vendedor = models.AutoField(primary_key=True)
	estatus_vendedor = models.BooleanField("Estatus", default=True, 
										   choices=ESTATUS_GEN)
	nombre_vendedor = models.CharField("Nombre vendedor", max_length=30)
	domicilio_vendedor = models.CharField("Domicilio", max_length=30)
	email_vendedor = models.EmailField("Correo", max_length=50)
	telefono_vendedor = models.CharField("Teléfono", max_length=15)
	pje_auto = models.DecimalField("% auto", max_digits=6, decimal_places=2)
	pje_camion = models.DecimalField("% camión", max_digits=6, decimal_places=2)
	vence_factura = models.IntegerField("Días vcto. Fact.", 
										validators=[MinValueValidator(1), 
													MaxValueValidator(999)])
	vence_remito = models.IntegerField("Días vcto. Remito", 
										validators=[MinValueValidator(1), 
													MaxValueValidator(999)])
	id_sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE, 
									verbose_name="Sucursal")  # Relación con sucursal
	tipo_venta = models.CharField("Tipo", max_length=1, choices=TIPO_VENTA)
	col_descuento = models.IntegerField("Columna Dcto.", 
										validators=[MinValueValidator(1), 
													MaxValueValidator(999)])
	email_venta = models.BooleanField("Enviar correos con Comprobantes", default=False)
	info_saldo = models.BooleanField("Mostrar Saldo en Correos Electrónicos", default=False)
	info_estadistica = models.BooleanField("Mostrar Saldos en Comp. Sin Estadísticas", default=False)

	class Meta:
		db_table = 'vendedor'
		verbose_name = ('Vendedor')
		verbose_name_plural = ('Vendedores')
		ordering = ['nombre_vendedor']


''' Solo para cuadrar plantilla del form
	
	Línea 1
		estatus_vendedor = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
		nombre_vendedor = models.CharField("Nombre vendedor", max_length=30)
	Línea 2
		telefono_vendedor = models.CharField("Teléfono", max_length=15)
		domicilio_vendedor = models.CharField("Domicilio", max_length=30)
		email_vendedor = models.CharField("Correo", max_length=50)
	Línea 3
		pje_auto = models.DecimalField("% auto", max_digits=6, decimal_places=2)
		pje_camion = models.DecimalField("% camión", max_digits=6, decimal_places=2)
		vence_factura = models.IntegerField("Días vcto. Fact.")
		vence_remito = models.IntegerField("Días vcto. Remito")
	Línea 4
		id_sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE, verbose_name="Sucursal")  # Relación con sucursal
		tipo_venta = models.CharField("Tipo", max_length=1, choices=TIPO_VENTA)
		col_descuento = models.IntegerField("Columna Dcto.", validators=[MinValueValidator(1), MaxValueValidator(999)])
	Línea 5
		email_venta = models.BooleanField("Enviar correos con Comprobantes", default=False)
		info_saldo = models.BooleanField("Mostrar Saldo en Correos Electrónicos", default=False)
		info_estadistica = models.BooleanField("Mostrar Saldos en Comp. Sin Estadísticas", default=False)
	
'''