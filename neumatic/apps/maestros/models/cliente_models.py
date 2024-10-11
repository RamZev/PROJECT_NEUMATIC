# neumatic\apps\maestros\models\cliente_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
	estatus_cliente = models.BooleanField("Estatus", default=True, 
										  choices=ESTATUS_GEN)
	nombre_cliente = models.CharField("Nombre Cliente", max_length=50)
	domicilio_cliente = models.CharField("Domicilio Cliente", 
										 max_length=50)
	codigo_postal = models.CharField("Código Postal", max_length=5)
	id_provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, 
									 verbose_name="Provincia",
									 null=True, blank=True)
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT,
									 verbose_name="Localidad")
	tipo_persona = models.CharField("Tipo de Persona", max_length=1,
									default="N", 
									choices=TIPO_PERSONA)
	id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.PROTECT,
									verbose_name="Tipo de Iva")
	id_tipo_documento_identidad = models.ForeignKey(
		TipoDocumentoIdentidad, 
		on_delete=models.PROTECT,
		verbose_name="Tipo Doc. Identidad ")
	cuit = models.IntegerField("CUIT", 
							validators=[MinValueValidator(20000000000), 
				   						MaxValueValidator(34999999999)])
	condicion_venta = models.IntegerField("Condición Venta", 
										  default=True,
										  choices=CONDICION_VENTA)
	telefono_cliente = models.CharField("Teléfono", 
										max_length=15)
	fax_cliente = models.CharField("Fax", max_length=15)
	movil_cliente = models.CharField("Móvil", max_length=15)
	email_cliente = models.EmailField("Email", max_length=50)
	email2_cliente = models.EmailField("Email 2", max_length=50)
	transporte_cliente = models.CharField("Transporte", max_length=50)
	id_vendedor = models.ForeignKey(Vendedor, 
									on_delete=models.PROTECT,
									verbose_name="Vendedor")
	fecha_nacimiento = models.DateField("Fecha Nacimiento")
	fecha_alta = models.DateField("Fecha Alta")
	sexo = models.CharField("Sexo", max_length=1, 
							default="M", 
							choices=SEXO)
	id_actividad = models.ForeignKey(Actividad, 
									 on_delete=models.PROTECT,
									 verbose_name="Actividad")
	id_sucursal = models.ForeignKey(Sucursal, 
									on_delete=models.CASCADE,
									verbose_name="Sucursal")
	id_percepcion_ib = models.ForeignKey(TipoPercepcionIb, 
										 on_delete=models.PROTECT, 
										 verbose_name="Percepción IB")
	numero_ib = models.CharField("Número IB", max_length=15)
	vip = models.BooleanField("Cliente VIP", 
							  default=False,
							  choices=CLIENTE_VIP)
	mayorista = models.BooleanField("Mayorista", 
									default=False,
									choices=CLIENTE_MAYORISTA)
	sub_cuenta = models.IntegerField("Sub Cuenta", 
									 validators=[MinValueValidator(1), 
												 MaxValueValidator(999999)])
	observaciones_cliente = models.TextField("Observaciones", 
											 blank=True, null=True)
	# id_usuario = models.IntegerField()  # El usuario que creó el cliente
	black_list = models.BooleanField("Black List", default=False, 
										  choices=BLACK_LIST)
	black_list_motivo = models.CharField("Motivo Black List", 
										   max_length=50)
	black_list_usuario = models.CharField("Usuario Black List", 
										  max_length=20)
	fecha_baja = models.DateField("Fecha de Baja")
	
	def __str__(self):
		return self.nombre_cliente
	
	
	class Meta:
		db_table = 'cliente'
		verbose_name = ('Cliente')
		verbose_name_plural = ('Clientes')
		ordering = ['nombre_cliente']
