# neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
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
	# iva = models.CharField(max_length=3)
	id_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT, 
						 verbose_name="Tipo I.V.A.", null=True, blank=True)
	cuit = models.IntegerField("C.U.I.T.*")
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
	ws_token = models.TextField("Token", null=True, blank=True)
	ws_sign = models.TextField("Sign", null=True, blank=True)
	ws_expiracion = models.DateField("Expiración Ticket WS", null=True, blank=True)
	ws_modo = models.IntegerField("Modo*", choices=WS_MODO)
	ws_vence = models.DateField("Vcto. Certificado*")
	
	def __str__(self):
		return self.nombre_fiscal
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		cuit_str = str(self.cuit)
		cbu_str = str(self.cbu)
		telefono_str = str(self.telefono)
		
		if not re.match(r'^(20|23|24|25|26|27|30|33|34|35|36)\d{9}$', cuit_str):
			errors.update({'cuit': 'El CUIT debe comenzar con 20, 23, 24, 25, 26, 27, 30, 33, 34, 35 o 36 y tener 11 dígitos en total.'})
		
		if not re.match(r'^\d{1,22}$', cbu_str):
			errors.update({'cbu': 'El CBU debe contener sólo dígitos numéricos y hasta 22 dígitos en total.'})
		
		if not re.match(r'^\d{1,22}$', telefono_str):
			errors.update({'telefono': 'El Teléfono debe contener sólo dígitos numéricos y hasta 20 dígitos en total.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'empresa'
		verbose_name = ('Empresa')
		verbose_name_plural = ('Empresas')
		ordering = ['nombre_fiscal']
