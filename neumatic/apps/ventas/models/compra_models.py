# neumatic\apps\ventas\models\compra_models.py
from django.db import models

from apps.maestros.models.base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN, CONDICION_VENTA
from apps.maestros.models.base_models import (ComprobanteVenta, 
											  ProductoDeposito, 
											  Provincia, 
											  PuntoVenta,)
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.proveedor_models import Proveedor
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.valida_models import Valida


class Compra(ModeloBaseGenerico):
    id_comprovante = models.AutoField(
        primary_key=True
    )
    estatus_comprabante = models.BooleanField(
        verbose_name="Estatus",
        default=True,
        choices=ESTATUS_GEN
    )
    id_sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        verbose_name="Sucursal",
        null=True,
        blank=True
    )
    id_punto_venta = models.ForeignKey(
		PuntoVenta,
		on_delete=models.PROTECT,
		verbose_name="Punto de Venta",
		null=True,
		blank=True
	)
    id_deposito = models.ForeignKey(
        ProductoDeposito,
        on_delete=models.PROTECT,
        verbose_name="Depósito",
        null=True,
        blank=True
    )
    id_comprobante_compra = models.ForeignKey(
		ComprobanteVenta,
		on_delete=models.PROTECT,
		verbose_name="Comprobante",
		null=True,
		blank=True
	)
    compro = models.CharField(
		verbose_name="Compro",
		max_length=3,
		null=True,
		blank=True
	) 
    letra_comprobante = models.CharField(
        verbose_name="Letra",
        max_length=1,
        null=True,
        blank=True
    )
    numero_comprobante = models.IntegerField(
		verbose_name="Número",
		null=True,
		blank=True
	)
    fecha_comprobante = models.DateField(
        verbose_name="Fecha Emisión",
        null=True,
        blank=True
    )
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        verbose_name="Proveedor",
        null=True,
        blank=True
    )
    id_provincia = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        verbose_name="Provincia",
        null=True,
        blank=True
    )
    condicion_comprobante = models.IntegerField(
		verbose_name="Condición de Compra",
		default=1,
		choices=CONDICION_VENTA
	)
    fecha_registro = models.DateField(
        verbose_name="Fecha Registro",
        null=True,
        blank=True
    )
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha Vencimiento",
        null=True,
        blank=True
    )
    gravado = models.DecimalField(
		verbose_name="Gravado",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    no_gravado = models.DecimalField(
		verbose_name="No Gravado",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    no_inscripto = models.DecimalField(
		verbose_name="No Inscripto",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    exento = models.DecimalField(
		verbose_name="Exento",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    retencion_iva = models.DecimalField(
		verbose_name="Retención IVA",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    retencion_ganancia = models.DecimalField(
		verbose_name="Retención Ganancia",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    retencion_ingreso_bruto = models.DecimalField(
		verbose_name="Retención Ingreso Bruto",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    sellado = models.DecimalField(
		verbose_name="Sellado",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    percepcion_iva = models.DecimalField(
		verbose_name="Percepción IVA",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    percepcion_ingreso_bruto = models.DecimalField(
		verbose_name="Percepción Ingreso Bruto",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    iva = models.DecimalField(
		verbose_name="Iva",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    total = models.DecimalField(
		verbose_name="Total",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    entrega = models.DecimalField(
		verbose_name="Entrega",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    documento_asociado = models.CharField(
		verbose_name="Documento Asociado",
		max_length=2,
		default="",
		null=True,
		blank=True
	)
    alicuota_iva = models.DecimalField(
		verbose_name="Alicuota IVA",
		max_digits=14,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.0
	)
    observa_comprobante = models.TextField(
		verbose_name="Observaciones",
		null=True,
		blank=True
	)


    class Meta:
        db_table = "compra"
        verbose_name = ('Compra')
        verbose_name_plural = ('Compras')

    def __str__(self):
        numero = str(self.numero_comprobante).strip().zfill(12)
        return f"{self.id_comprobante_compra.codigo_comprobante_compra} {self.letra_comprobante} {numero[:4]}-{numero[4:]}"
