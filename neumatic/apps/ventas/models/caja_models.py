from django.db import models
from django.forms import ValidationError

from apps.maestros.models.base_gen_models import ModeloBaseGenerico
from apps.usuarios.models import User 
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.base_models import FormaPago
from entorno.constantes_base import ESTATUS_GEN


class Caja(ModeloBaseGenerico):
	id_caja = models.AutoField(
		primary_key=True,
		verbose_name='ID Caja'
	)
	estatus_caja = models.BooleanField(
		verbose_name="Estatus",
		default=True,
		choices=ESTATUS_GEN
	)
	numero_caja = models.IntegerField(
		verbose_name='Número Caja',
		null=True,
		blank=True
	)
	fecha_caja = models.DateField(
		verbose_name='Fecha'
	)
	saldoanterior = models.DecimalField(
		verbose_name='Saldo Anterior',
		max_digits=12,
		decimal_places=2,
		default=0,
	)
	ingresos = models.DecimalField(
		verbose_name='Ingresos',
		max_digits=12,
		decimal_places=2, 
		default=0,
	)
	egresos = models.DecimalField(
		verbose_name='Egresos',
		max_digits=12, 
		decimal_places=2, 
		default=0,
	)
	saldo = models.DecimalField(
		verbose_name='Saldo',
		max_digits=12,
		decimal_places=2,
		default=0,
	)
	caja_cerrada = models.BooleanField(
		verbose_name='Cerrada',
		default=False,
	)
	recuento = models.DecimalField(
		verbose_name='Recuento',
		max_digits=12,
		decimal_places=2,
		default=0,
	)
	diferencia = models.DecimalField(
		verbose_name='Diferencia',
		max_digits=12,
		decimal_places=2,
		default=0,
	)
	id_sucursal = models.ForeignKey(
		Sucursal,
		on_delete=models.PROTECT,
		verbose_name="Sucursal",
		null=True,
		blank=True
	)
	hora_cierre = models.DateTimeField(
		verbose_name='Hora Cierre/Apertura',
		null=True, 
		blank=True
	)
	observacion_caja = models.CharField(
		verbose_name='Observaciones',
		max_length=50, 
		blank=True, 
		null=True
	)
	id_usercierre = models.ForeignKey(
		User, 
		on_delete=models.PROTECT, 
		verbose_name="Usuario", 
		related_name="usuario_cierre",
		null=True, 
		blank=True
	)
	
	class Meta:
		db_table = 'caja'
		verbose_name = 'Caja'
		verbose_name_plural = 'Cajas'

	def __str__(self):
		return f'{self.numero_caja}'
	
	def clean(self):
		"""Validaciones básicas del modelo"""
		super().clean()
		
		errors = {}
		
		# Solo validar numero_caja para registros existentes
		if self.pk and not self.numero_caja:
			errors['numero_caja'] = 'El número de caja es requerido'
		
		# Validar que id_sucursal tenga máximo 2 dígitos
		if self.id_sucursal and self.id_sucursal.id_sucursal > 99:
			errors['id_sucursal'] = 'El ID de sucursal debe ser de máximo 2 dígitos'
		
		if errors:
			raise ValidationError(errors)
	
	@property
	def nombre_sucursal(self):
		"""Propiedad para mostrar el nombre de la sucursal"""
		return self.id_sucursal.nombre_sucursal if self.id_sucursal else ""


class CajaDetalle(ModeloBaseGenerico):
	TIPOS_MOVIMIENTO = [
		(1, 'Ingreso'),
		(2, 'Egreso'),
	]

	id_caja_detalle = models.AutoField(
		verbose_name='ID Caja Detalle',
		primary_key=True,
	)
	id_caja = models.ForeignKey(
		Caja,
		on_delete=models.PROTECT,
		verbose_name="Caja Detalle",
		null=True,
		blank=True
	) 
	
	# Relaciones típicas (ajusta los modelos relacionados según tu proyecto)
	idventas = models.SmallIntegerField(
		null=True,
		blank=True,
	)
	idcompras = models.SmallIntegerField(
		null=True,
		blank=True,
	)
	idbancos = models.SmallIntegerField(
		null=True,
		blank=True,
	)
	
	tipo_movimiento = models.IntegerField(
		verbose_name="Tipo de Movimiento",
		choices=TIPOS_MOVIMIENTO,
		default=1,
	)
	id_forma_pago = models.ForeignKey(
		FormaPago,
		on_delete=models.PROTECT,
		verbose_name="Forma de Pago",
		null=True,
		blank=True
	) 
	importe = models.DecimalField(
		verbose_name="Importe",
		max_digits=12,
		decimal_places=2,
		help_text="Importe del movimiento (puede ser positivo o negativo)"
	)
	observacion = models.CharField(
		verbose_name="Observación",
		max_length=50,
		blank=True,
		help_text="Observaciones del movimiento"
	)
	
	class Meta:
		db_table = 'caja_detalle'
		verbose_name = 'Detalle de Caja'
		verbose_name_plural = 'Detalle de Cajas'
		ordering = ['-id_caja']

	def __str__(self):
		return f"{self.id_caja}"
