# neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re

from utils.validator.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
from .base_models import Localidad, Provincia, TipoIva
from entorno.constantes_base import ESTATUS_GEN, WS_MODO


class Empresa(ModeloBaseGenerico):
	id_empresa = models.AutoField(primary_key=True)
	estatus_empresa = models.BooleanField("Estatus*", default=True,
										  choices=ESTATUS_GEN)
	nombre_fiscal = models.CharField("Nombre Fiscal*", max_length=50)
	nombre_comercial = models.CharField("Nombre Comercial*", max_length=50)
	domicilio_empresa = models.CharField("Domicilio*", max_length=50)
	codigo_postal = models.CharField("Código postal*", max_length=4)
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, 
								  verbose_name="Localidad*")
	id_provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, 
								  verbose_name="Provincia*")
	id_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT, 
						 verbose_name="Tipo I.V.A.", null=True, blank=True)
	cuit = models.IntegerField("C.U.I.T.*", )
	ingresos_bruto = models.CharField("Ing. Bruto*", max_length=15)
	inicio_actividad = models.DateField("Inicio de actividad*")
	cbu = models.CharField("CBU Bancaria*", max_length=22)
	cbu_alias = models.CharField("CBU Alias*", max_length=50)
	cbu_vence = models.DateField("Vcto. CBU*")
	telefono = models.CharField("Teléfono*", max_length=20)
	email_empresa = models.EmailField("Correo*", max_length=50)
	web_empresa = models.CharField("Web", max_length=50, 
								   null=True, blank=True)
	
	logo_empresa = models.BinaryField()  # Para el campo 'image'
	
	ws_archivo_crt = models.CharField("Archivo CRT WSAFIP*", max_length=50)
	ws_archivo_key = models.CharField("Archivo KEY WSAFIP*", max_length=50)
	ws_archivo_crt2 = models.TextField("CRT", null=True, blank=True)
	ws_archivo_key2 = models.TextField("KEY", null=True, blank=True)
	ws_token = models.TextField("Token", null=True, blank=True)
	ws_sign = models.TextField("Sign", null=True, blank=True)
	ws_expiracion = models.DateField("Expiración Ticket WS", null=True, blank=True)
	ws_modo = models.IntegerField("Modo*", choices=WS_MODO)
	ws_vence = models.DateField("Vcto. Certificado*")
	
	#-- Parámetros.
	interes = models.DecimalField("Intereses(%)", max_digits=5,
								decimal_places=2, default=0.00, blank=True)
	interes_dolar = models.DecimalField("Intereses Dólar(%)", max_digits=5,
										decimal_places=2, default=0.00,
										blank=True)
	cotizacion_dolar = models.DecimalField("Cotización Dólar",
										max_digits=15, decimal_places=2, 
										default=0.00, blank=True)
	dias_vencimiento = models.IntegerField("Días Vcto.", default=0, 
										blank=True)
	descuento_maximo = models.DecimalField("Dcto. Máximo(%)",
										max_digits=5, decimal_places=2, 
										default=0.00, blank=True)
	
	class Meta:
		db_table = 'empresa'
		verbose_name = ('Empresa')
		verbose_name_plural = ('Empresas')
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

