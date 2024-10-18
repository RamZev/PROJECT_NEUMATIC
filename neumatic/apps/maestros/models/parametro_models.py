# neumatic\apps\maestros\models\parametro_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
from .empresa_models import Empresa
from entorno.constantes_base import ESTATUS_GEN


class Parametro(ModeloBaseGenerico):
	id_parametro = models.AutoField(primary_key=True)  # Clave primaria
	estatus_parametro = models.BooleanField("Estatus", default=True,
											choices=ESTATUS_GEN)  # Estatus del parámetro
	id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE,
								   verbose_name="Empresa")
	interes = models.DecimalField("Intereses(%)", max_digits=4,
								decimal_places=2, default=0.00, 
								null=True, blank=True)
	interes_dolar = models.DecimalField("Intereses Dólar(%)", max_digits=4,
										decimal_places=2, default=0.00,
										null=True, blank=True)
	cotizacion_dolar = models.DecimalField("Cotización Dólar",
										max_digits=15, decimal_places=2, 
										default=0.00, null=True, blank=True)
	dias_vencimiento = models.IntegerField("Días Vcto.", default=0, 
										null=True, blank=True)
	descuento_maximo = models.DecimalField("Descuento Máximo(%)",
										max_digits=4, decimal_places=2, 
										default=0.00, null=True, blank=True)
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		interes_str = str(self.interes) if self.interes else ""
		interes_dolar_str = str(self.interes_dolar) if self.interes_dolar else ""
		cotizacion_dolar_str = str(self.cotizacion_dolar) if self.cotizacion_dolar else ""
		dias_vencimiento_str = str(self.dias_vencimiento) if self.dias_vencimiento else ""
		descuento_maximo_str = str(self.descuento_maximo) if self.descuento_maximo else ""
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$|^$', interes_str):
			errors.update({'interes': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$|^$', interes_dolar_str):
			errors.update({'interes_dolar': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$|^$', cotizacion_dolar_str):
			errors.update({'cotizacion_dolar': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if not re.match(r'^[1-9]\d{0,2}$|^0$|^$', dias_vencimiento_str):
			errors.update({'dias_vencimiento': 'El valor debe ser un número entero positivo, con hasta 3 dígitos, o estar en blanco o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$|^$', descuento_maximo_str):
			errors.update({'descuento_maximo': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales, o estar en blanco o cero.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'parametro'
		verbose_name = 'Parámetro'
		verbose_name_plural = 'Parámetros'
		ordering = ['id_empresa']
