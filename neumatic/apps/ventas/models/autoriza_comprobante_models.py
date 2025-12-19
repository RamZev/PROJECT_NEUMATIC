# neumatic\apps\ventas\models\autoriza_comprobante_models.py
from django.db import models

from apps.maestros.models.base_gen_models import ModeloBaseGenerico
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.cliente_models import Cliente


class AutorizaComprobante(ModeloBaseGenerico):
	id_autoriza_comprobante = models.AutoField(
		primary_key=True
	)
	id_sucursal = models.ForeignKey(
		Sucursal,
		on_delete=models.PROTECT,
		verbose_name="Sucursal",
		null=True,
		blank=True
	)
	fecha_autorizacion = models.DateField(
		verbose_name="Fecha Autorización",
		null=True,
		blank=True
	)
	hora_autorizacion = models.TimeField(
		verbose_name="Hora Autorización",
		null=True,
		blank=True
	)
	solicitante = models.CharField(
		verbose_name="Solicitante",
		max_length=20,
		null=True,
		blank=True
	)
	comentario = models.CharField(
		verbose_name="Solicitante",
		max_length=50,
		null=True,
		blank=True
	)
	id_cliente = models.ForeignKey(
		Cliente,
		on_delete=models.PROTECT,
		verbose_name="Cliente",
		null=True,
		blank=True
	)
	numero_comprobante = models.IntegerField(
		verbose_name="Número Comprobante",
		null=True,
		blank=True
	)
	hora_comprobante = models.TimeField(
		verbose_name="Hora Comprobante",
		null=True, blank=True
	)
	validacion = models.CharField(
		verbose_name="Validación",
		max_length=4,
		null=True,
		blank=True
	)
	
	class Meta:
		db_table = "autoriza_comprobante"
		verbose_name = 'Autoriza Comprobante'
		verbose_name_plural = 'Autoriza Comprobantes'
		# ordering = ['id_factura']
	
	def __str__(self):
		return f"{self.id_autoriza_comprobante}"
