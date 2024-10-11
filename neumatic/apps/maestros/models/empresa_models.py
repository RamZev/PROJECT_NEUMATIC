# neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
from .base_models import *
from entorno.constantes_base import ESTATUS_GEN, WS_MODO


class Empresa(ModeloBaseGenerico):
	id_empresa = models.AutoField(primary_key=True)
	estatus_empresa = models.BooleanField("Estatus", default=True,
										  choices=ESTATUS_GEN)
	nombre_fiscal = models.CharField("Nombre Fiscal", max_length=50)
	nombre_comercial = models.CharField("Nombre Comercial", max_length=50)
	domicilio_empresa = models.CharField("Domicilio", max_length=50)
	codigo_postal = models.CharField("Código postal", max_length=4)
	id_localidad = models.ForeignKey('Localidad', on_delete=models.PROTECT, 
								  verbose_name="Localidad")
	id_provincia = models.ForeignKey('Provincia', on_delete=models.PROTECT, 
								  verbose_name="Provincia")
	# iva = models.CharField(max_length=3)
	id_iva = models.ForeignKey('TipoIva', on_delete=models.PROTECT, 
						 verbose_name="Tipo I.V.A.", null=True, blank=True)
	cuit = models.IntegerField("C.U.I.T.", 
							validators=[MinValueValidator(20000000000), 
				   						MaxValueValidator(34999999999)])
	ingresos_bruto = models.CharField("Ing. Bruto", max_length=15)
	inicio_actividad = models.DateField("Inicio de actividad")
	cbu = models.CharField("CBU Bancaria", max_length=22)
	cbu_alias = models.CharField("CBU Alias", max_length=50)
	cbu_vence = models.DateField("Vcto. CBU")
	telefono = models.CharField("Teléfono", max_length=20)
	email_empresa = models.EmailField("Correo", max_length=50)
	web_empresa = models.CharField("Web", max_length=50)
	
	logo_empresa = models.BinaryField()  # Para el campo 'image'
	
	ws_archivo_crt = models.CharField("Archivo CRT WSAFIP", max_length=50)
	ws_archivo_key = models.CharField("Archivo KEY WSAFIP", max_length=50)
	ws_token = models.TextField("Token", null=True, blank=True)
	ws_sign = models.TextField("Sign", null=True, blank=True)
	ws_expiracion = models.DateField("Expiración Ticket WS", null=True, blank=True)
	ws_modo = models.DecimalField("Modo", max_digits=1, decimal_places=0, 
							   choices=WS_MODO)
	ws_vence = models.DateField("Vcto. Certificado")
	
	def __str__(self):
		return self.nombre_fiscal
	
	class Meta:
		db_table = 'empresa'
		verbose_name = ('Empresa')
		verbose_name_plural = ('Empresas')
		ordering = ['nombre_fiscal']


''' Solo para cuadrar plantilla del form
	
	Línea 1
		estatus_empresa = models.BooleanField("Estatus", default=True,choices=ESTATUS_GEN)
		nombre_fiscal = models.CharField("Nombre Fiscal", max_length=50)
		nombre_comercial = models.CharField("Nombre Comercial", max_length=50)
	
	Línea 2
		domicilio_empresa = models.CharField("Domicilio", max_length=50)
		codigo_postal = models.CharField("Código postal", max_length=4)
		id_localidad = models.ForeignKey('Localidad', on_delete=models.PROTECT, verbose_name="Localidad")
		id_provincia = models.ForeignKey('Provincia', on_delete=models.PROTECT, verbose_name="Provincia")
	
	Línea 3
		telefono = models.CharField("Teléfono", max_length=20)
		email_empresa = models.EmailField("Correo", max_length=50)
		web_empresa = models.CharField("Web", max_length=50)
		logo_empresa = models.BinaryField()  # Para el campo 'image'
	
	Línea 4
		id_iva = models.ForeignKey('TipoIva', on_delete=models.PROTECT, verbose_name="Tipo I.V.A.")
		cuit = models.DecimalField("C.U.I.T.", max_digits=11, decimal_places=0)
		ingresos_bruto = models.CharField("Ing. Bruto", max_length=15)
		inicio_actividad = models.DateField("Inicio de actividad")
	
	Línea 5
		cbu = models.BigIntegerField("CBU Bancaria", validators=[MinValueValidator(1), MaxValueValidator(9999999999999999999999)])
		cbu_alias = models.CharField("CBU Alias", max_length=50)
		cbu_vence = models.DateField("Vcto. CBU")
	
	Línea 6
		ws_archivo_crt = models.CharField("Archivo CRT WSAFIP", max_length=50)
		ws_archivo_key = models.CharField("Archivo KEY WSAFIP", max_length=50)
		ws_vence = models.DateField("Vcto. Certificado")
	
	Línea 7
		ws_expiracion = models.DateField("Expiración Ticket WS")
		ws_token = models.TextField("Token")
		ws_sign = models.TextField("Sign")
	
	Línea 8
		ws_modo = models.DecimalField("Modo", max_digits=1, decimal_places=0, choices=WS_MODO)
		
		
		
		
		
	
'''