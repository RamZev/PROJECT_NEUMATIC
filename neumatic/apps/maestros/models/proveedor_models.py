# neumatic\apps\maestros\models\proveedor_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
from .base_models import Localidad, TipoIva, TipoRetencionIb
from entorno.constantes_base import ESTATUS_GEN


class Proveedor(ModeloBaseGenerico):
	id_proveedor = models.AutoField(primary_key=True)
	estatus_proveedor = models.BooleanField("Estatus", default=True, 
										 choices=ESTATUS_GEN)
	nombre_proveedor = models.CharField("Nombre proveedor", max_length=50)
	domicilio_proveedor = models.CharField("Domicilio", max_length=50)
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, 
								  verbose_name="Localidad")
	codigo_postal = models.CharField("Código postal", max_length=5)
	id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT, 
								 verbose_name="Tipo IVA")
	cuit = models.IntegerField("C.U.I.T.")
	id_tipo_retencion_ib = models.ForeignKey(TipoRetencionIb, 
										  on_delete=models.PROTECT, 
										  verbose_name="Tipo de Retención Ib")
	ib_numero = models.CharField("Ingreso Bruto*", max_length=15)
	ib_exento = models.BooleanField("Exento Ret. Ing. Bruto")
	ib_alicuota = models.DecimalField("Alíc. Ing. B.", max_digits=4, 
								   decimal_places=2)
	multilateral = models.BooleanField("Contrib. Conv. Multilateral")
	telefono_proveedor = models.CharField("Taléfono", max_length=15)
	movil_proveedor = models.CharField("Móvil", max_length=15)
	email_proveedor = models.EmailField("Correo", max_length=50)
	observacion_proveedor = models.TextField("Observaciones", blank=True, 
										  null=True)
	
	def __str__(self):
		return self.nombre_proveedor
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		if not re.match(r'^(20|23|24|25|26|27|30|33|34|35|36)\d{9}$', str(self.cuit)):
			errors.update({'cuit': 'El CUIT debe comenzar con 20, 23, 24, 25, 26, 27, 30, 33, 34, 35 o 36 y tener 11 dígitos en total.'})
		
		if not re.match(r'^(0?[1-9]\.\d{2}|[1-9]\d\.\d{2}|0?0\.[1-9]\d|0?0\.0[1-9])$', str(self.ib_alicuota)):
			errors.update({'ib_alicuota': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales.'})
		
		if not re.match(r'^\+?\d[\d ]{0,14}$', str(self.telefono_proveedor)):
			errors.update({'telefono_proveedor': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if not re.match(r'^\+?\d[\d ]{0,14}$', str(self.movil_proveedor)):
			errors.update({'movil_proveedor': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'proveedor'
		verbose_name = 'Proveedor'
		verbose_name_plural = 'Proveedores'
		ordering = ['nombre_proveedor']
