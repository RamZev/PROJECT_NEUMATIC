# neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re

from utils.validator.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
from .base_models import Localidad, Provincia, TipoIva
from entorno.constantes_base import ESTATUS_GEN, WS_MODO


class Empresa(ModeloBaseGenerico):
	id_empresa = models.AutoField(
		primary_key=True
	)
	estatus_empresa = models.BooleanField(
		verbose_name="Estatus*",
		default=True,
		choices=ESTATUS_GEN
	)
	nombre_fiscal = models.CharField(
		verbose_name="Nombre Fiscal*",
		max_length=50
	)
	nombre_comercial = models.CharField(
		verbose_name="Nombre Comercial*",
		max_length=50
	)
	domicilio_empresa = models.CharField(
		verbose_name="Domicilio*",
		max_length=50
	)
	codigo_postal = models.CharField(
		verbose_name="Código postal*",
		max_length=4
	)
	id_localidad = models.ForeignKey(
		Localidad,
		on_delete=models.PROTECT,
		verbose_name="Localidad*"
	)
	id_provincia = models.ForeignKey(
		Provincia,
		on_delete=models.PROTECT,
		verbose_name="Provincia*"
	)
	id_iva = models.ForeignKey(
		TipoIva,
		on_delete=models.PROTECT,
		verbose_name="Tipo I.V.A.",
		null=True,
		blank=True
	)
	cuit = models.IntegerField(
		verbose_name="C.U.I.T.*"
	)
	ingresos_bruto = models.CharField(
		verbose_name="Ing. Bruto*",
		max_length=15
	)
	inicio_actividad = models.DateField(
		verbose_name="Inicio de actividad*"
	)
	cbu = models.CharField(
		verbose_name="CBU Bancaria*",
		max_length=22
	)
	cbu_alias = models.CharField(
		verbose_name="CBU Alias*",
		max_length=50
	)
	cbu_vence = models.DateField(
		verbose_name="Vcto. CBU*"
	)
	telefono = models.CharField(
		verbose_name="Teléfono*",
		max_length=20
	)
	email_empresa = models.EmailField(
		verbose_name="Correo*",
		max_length=50
	)
	web_empresa = models.CharField(
		verbose_name="Web",
		max_length=50,
		null=True, blank=True
	)
	
	logo_empresa = models.BinaryField()  # Para el campo 'image'
	
	ws_archivo_crt2 = models.TextField(
		verbose_name="CRT Homologación",
		null=True,
		blank=True
	)
	ws_archivo_key2 = models.TextField(
		verbose_name="KEY Homologación",
		null=True,
		blank=True
	)
	ws_vence_h = models.DateTimeField(
		verbose_name="Vcto. Certificado H",
		null=True,
		blank=True
	)
	ws_archivo_crt_p = models.TextField(
		verbose_name="CRT Producción",
		null=True,
		blank=True
	)
	ws_archivo_key_p = models.TextField(
		verbose_name="KEY Producción",
		null=True,
		blank=True
	)
	ws_vence_p = models.DateTimeField(
		verbose_name="Vcto. Certificado P",
		null=True,
		blank=True
	)
	ws_token_h = models.TextField(
		verbose_name="Token Homologación",
		null=True,
		blank=True
	)
	ws_sign_h = models.TextField(
		verbose_name="Sign Homologación",
		null=True,
		blank=True
	)
	ws_expiracion_h = models.DateTimeField(
		verbose_name="Expiración Ticket WS H",
		null=True,
		blank=True
	)
	ws_token_p = models.TextField(
		verbose_name="Token Producción",
		null=True,
		blank=True
	)
	ws_sign_p = models.TextField(
		verbose_name="Sign Producción",
		null=True,
		blank=True
	)
	ws_expiracion_p = models.DateTimeField(
		verbose_name="Expiración Ticket WS P",
		null=True,
		blank=True
	)
	ws_modo = models.IntegerField(
		verbose_name="Modo*",
		choices=WS_MODO
	)
	
	#-- Parámetros.
	interes = models.DecimalField(
		verbose_name="Intereses(%)",
		max_digits=5,
		decimal_places=2,
		default=0.00,
		blank=True
	)
	interes_dolar = models.DecimalField(
		verbose_name="Intereses Dólar(%)",
		max_digits=5,
		decimal_places=2,
		default=0.00,
		blank=True
	)
	cotizacion_dolar = models.DecimalField(
		verbose_name="Cotización Dólar",
		max_digits=15,
		decimal_places=2,
		default=0.00,
		blank=True
	)
	dias_vencimiento = models.IntegerField(
		verbose_name="Días Vcto.",
		default=0,
		blank=True
	)
	descuento_maximo = models.DecimalField(
		verbose_name="Dcto. Máximo(%)",
		max_digits=5,
		decimal_places=2,
		default=0.00,
		blank=True
	)
	
	class Meta:
		db_table = 'empresa'
		verbose_name = 'Empresa'
		verbose_name_plural = 'Empresas'
		ordering = ['nombre_fiscal']
	
	def __str__(self):
		return self.nombre_fiscal
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		interes_str = str(self.interes) if self.interes is not None else ""
		interes_dolar_str = str(self.interes_dolar) if self.interes_dolar is not None else ""
		cotizacion_dolar_str = str(self.cotizacion_dolar) if self.cotizacion_dolar is not None else ""
		dias_vencimiento_str = str(self.dias_vencimiento) if self.dias_vencimiento is not None else ""
		descuento_maximo_str = str(self.descuento_maximo) if self.descuento_maximo is not None else ""
		
		try:
			validar_cuit(self.cuit)
		except ValidationError as e:
			errors['cuit'] = e.messages
		
		if not re.match(r'^\d{1,22}$', str(self.cbu)):
			errors.update({'cbu': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 22.'})
		
		if not re.match(r'^\+?\d[\d ]{0,19}$', str(self.telefono)):
			errors.update({'telefono': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 20, el signo + y espacios.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', interes_str):
			errors.update({'interes': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', interes_dolar_str):
			errors.update({'interes_dolar': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', cotizacion_dolar_str):
			errors.update({'cotizacion_dolar': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^[1-9]\d{0,2}$|^0$', dias_vencimiento_str):
			errors.update({'dias_vencimiento': 'El valor debe ser un número entero positivo, con hasta 3 dígitos o cero.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', descuento_maximo_str):
			errors.update({'descuento_maximo': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if errors:
			raise ValidationError(errors)
	
	@property
	def cuit_formateado(self):
		cuit = str(self.cuit)
		return f"{cuit[:2]}-{cuit[2:-1]}-{cuit[-1:]}"

