# neumatic\apps\maestros\models\proveedor_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re

from utils.validator.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
from .base_models import Provincia, Localidad, TipoIva, TipoRetencionIb
from entorno.constantes_base import ESTATUS_GEN


class Proveedor(ModeloBaseGenerico):
	id_proveedor = models.AutoField(primary_key=True)
	estatus_proveedor = models.BooleanField("Estatus", default=True, 
										 choices=ESTATUS_GEN)
	nombre_proveedor = models.CharField("Nombre proveedor", max_length=50)
	domicilio_proveedor = models.CharField("Domicilio", max_length=50)
	codigo_postal = models.CharField("Código Postal*", max_length=5)
	id_provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, 
									 verbose_name="Provincia*")
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT,
									 verbose_name="Localidad*")
	id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT, 
								 verbose_name="Tipo IVA")
	cuit = models.IntegerField("C.U.I.T.", unique=True)
	id_tipo_retencion_ib = models.ForeignKey(TipoRetencionIb, 
										  on_delete=models.PROTECT, 
										  verbose_name="Tipo de Retención Ib")
	ib_numero = models.CharField("Ingreso Bruto*", max_length=15)
	ib_exento = models.BooleanField("Exento Ret. Ing. Bruto")
	ib_alicuota = models.DecimalField("Alíc. Ing. B.", max_digits=4, 
								   decimal_places=2, default=0.00)
	multilateral = models.BooleanField("Contrib. Conv. Multilateral")
	telefono_proveedor = models.CharField("Taléfono", max_length=15)
	movil_proveedor = models.CharField("Móvil", max_length=15, 
										null=True, blank=True)
	email_proveedor = models.EmailField("Correo", max_length=50)
	observacion_proveedor = models.TextField("Observaciones", blank=True, 
											null=True)
	
	def __str__(self):
		return self.nombre_proveedor
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		ib_alicuota_str = str(self.ib_alicuota) if self.ib_alicuota is not None else ""
		
		try:
			validar_cuit(self.cuit)
		except ValidationError as e:
			errors['cuit'] = e.messages
		
		if not re.match(r'^(0|[1-9]\d{0,1})(\.\d{1,2})?$', ib_alicuota_str):
			errors.update({'ib_alicuota': 'El valor debe ser positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^\+?\d[\d ]{0,14}$', str(self.telefono_proveedor)):
			errors.update({'telefono_proveedor': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if self.movil_proveedor and not re.match(r'^\+?\d[\d ]{0,14}$', str(self.movil_proveedor)):
			errors.update({'movil_proveedor': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo +, espacios o vacío.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'proveedor'
		verbose_name = 'Proveedor'
		verbose_name_plural = 'Proveedores'
		ordering = ['nombre_proveedor']
