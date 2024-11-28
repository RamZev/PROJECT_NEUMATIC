# neumatic\apps\maestros\models\cliente_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from datetime import date

from utils.validatos.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
from .base_models import (Actividad, Localidad, Provincia, TipoIva, 
						  TipoDocumentoIdentidad, TipoPercepcionIb)
from .vendedor_models import Vendedor
from .sucursal_models import Sucursal
from entorno.constantes_base import (
	ESTATUS_GEN, CONDICION_VENTA, SEXO, 
	CLIENTE_VIP, CLIENTE_MAYORISTA,
	TIPO_PERSONA, BLACK_LIST)


class Cliente(ModeloBaseGenerico):
	id_cliente = models.AutoField(primary_key=True)
	estatus_cliente = models.BooleanField("Estatus*", default=True, 
										  choices=ESTATUS_GEN)
	codigo_cliente = models.SmallIntegerField("Código", null=True, blank=True)
	nombre_cliente = models.CharField("Nombre Cliente*", max_length=50)
	domicilio_cliente = models.CharField("Domicilio Cliente*", 
										 max_length=50)
	codigo_postal = models.CharField("Código Postal*", max_length=5)
	id_provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, 
									 verbose_name="Provincia*")
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT,
									 verbose_name="Localidad*")
	tipo_persona = models.CharField("Tipo de Persona*", max_length=1,
									default="N", 
									choices=TIPO_PERSONA)
	id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT,
									verbose_name="Tipo de Iva*")
	id_tipo_documento_identidad = models.ForeignKey(TipoDocumentoIdentidad, 
										on_delete=models.PROTECT, 
										verbose_name="Tipo Doc. Identidad*")
	cuit = models.IntegerField("CUIT*")
	condicion_venta = models.IntegerField("Condición Venta*", 
										  default=True,
										  choices=CONDICION_VENTA)
	telefono_cliente = models.CharField("Teléfono*", max_length=15)
	fax_cliente = models.CharField("Fax", max_length=15, null=True, blank=True)
	movil_cliente = models.CharField("Móvil", max_length=15, null=True, blank=True)
	email_cliente = models.EmailField("Email*", max_length=50)
	email2_cliente = models.EmailField("Email 2", max_length=50, 
									null=True, blank=True)
	transporte_cliente = models.CharField("Transporte", max_length=50, 
									   null=True, blank=True)
	id_vendedor = models.ForeignKey(Vendedor, 
									on_delete=models.PROTECT,
									null=True, blank=True,
									verbose_name="Vendedor")
	fecha_nacimiento = models.DateField("Fecha Nacimiento", 
									 null=True, blank=True)
	fecha_alta = models.DateField("Fecha Alta", default=date.today)
	sexo = models.CharField("Sexo*", max_length=1, 
							default="M", 
							choices=SEXO)
	id_actividad = models.ForeignKey(Actividad, 
									 on_delete=models.PROTECT,
									 verbose_name="Actividad*")
	id_sucursal = models.ForeignKey(Sucursal, 
									on_delete=models.CASCADE,
									verbose_name="Sucursal*")
	id_percepcion_ib = models.ForeignKey(TipoPercepcionIb, 
										 on_delete=models.PROTECT, 
										 verbose_name="Percepción IB*")
	numero_ib = models.CharField("Número IB", max_length=15, null=True, blank=True)
	vip = models.BooleanField("Cliente VIP*", 
							  default=False,
							  choices=CLIENTE_VIP)
	mayorista = models.BooleanField("Mayorista*", 
									default=False,
									choices=CLIENTE_MAYORISTA)
	sub_cuenta = models.CharField("Sub Cuenta",max_length=6,  
							   null=True, blank=True)
	observaciones_cliente = models.TextField("Observaciones", 
											 blank=True, null=True)
	black_list = models.BooleanField("Black List", default=False, 
										  choices=BLACK_LIST)
	black_list_motivo = models.CharField("Motivo Black List", max_length=50, 
										   null=True, blank=True)
	black_list_usuario = models.CharField("Usuario Black List", 
										  max_length=20, null=True, blank=True)
	fecha_baja = models.DateField("Fecha de Baja", null=True, blank=True)
	
	def __str__(self):
		return self.nombre_cliente
	
	def clean(self):
		super().clean()
		
		# Diccionario contenedor de errores
		errors = {}
		
		# Convertir a string los valores de los campos previo a la validación
		telefono_str = str(self.telefono_cliente) if self.telefono_cliente else ''
		movil_cliente_str = str(self.movil_cliente) if self.movil_cliente else ''
		sub_cuenta_str = str(self.sub_cuenta) if self.sub_cuenta else ''
		
		try:
			validar_cuit(self.cuit)
		except ValidationError as e:
			# Agrego el error al dicciobario errors
			errors['cuit'] = e.messages
		
		if not re.match(r'^\+?\d[\d ]{0,14}$', telefono_str):
			errors.update({'telefono_cliente': 'Debe indicar sólo dígitos numéricos positivos, \
       			mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if movil_cliente_str and not re.match(r'^\+?\d[\d ]{0,14}$', movil_cliente_str):
			errors.update({'movil_cliente': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo +, espacios o vacío.'})
		
		if sub_cuenta_str and not re.match(r'^\d{0,6}$', sub_cuenta_str):
			errors.update({'sub_cuenta': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 6.'})
		
		
		if errors:
			# Lanza el conjunto de excepciones
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'cliente'
		verbose_name = ('Cliente')
		verbose_name_plural = ('Clientes')
		ordering = ['nombre_cliente']
