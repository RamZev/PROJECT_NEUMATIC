from django.db import models

from apps.maestros.models.base_gen_models import ModeloBaseGenerico
from apps.usuarios.models import User 
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.base_models import FormaPago
from entorno.constantes_base import ESTATUS_GEN


class Caja(ModeloBaseGenerico):
    id_caja = models.AutoField(primary_key=True, verbose_name='ID Caja')
    estatus_caja = models.BooleanField(
		verbose_name="Estatus",
		default=True,
		choices=ESTATUS_GEN)
    numero_caja = models.IntegerField(verbose_name='Número')
    fecha_caja = models.DateField(verbose_name='Fecha')
    saldoanterior = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Saldo Anterior'
    )
    ingresos = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Ingresos'
    )
    egresos = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Egresos'
    )
    saldo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Saldo'
    )
    caja_cerrada = models.BooleanField(default=False, verbose_name='Cerrada')
    recuento = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Recuento'
    )
    diferencia = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Diferencia'
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
        blank=True)
    observacion_caja = models.CharField(
        max_length=50, 
        verbose_name='Observaciones',
        blank=True, 
        null=True
    )
    id_usercierre = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name="Usuario", 
        related_name="usuario_cierre",
        null=True, 
        blank=True)
    
    @property
    def nombre_sucursal(self):
        """Propiedad para mostrar el nombre de la sucursal"""
        return self.id_sucursal.nombre_sucursal if self.id_sucursal else ""

    class Meta:
        db_table = 'caja'
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return f'Caja {self.numero_caja} - {self.fecha_caja}'
    


class CajaDetalle(ModeloBaseGenerico):
    id_caja_detalle = models.AutoField(primary_key=True, verbose_name='ID Caja Detalle')
    id_caja = models.ForeignKey(
		Caja,
		on_delete=models.PROTECT,
		verbose_name="Caja Detalle",
		null=True,
		blank=True
	) 

    caja = models.PositiveIntegerField(
        db_index=True,
        help_text="Código de caja o sucursal"
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

    id_forma_pago = models.ForeignKey(
        FormaPago,
		on_delete=models.PROTECT,
		verbose_name="Forma de Pago",
		null=True,
		blank=True
	) 

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Importe del movimiento (puede ser positivo o negativo)"
    )

    observacion = models.CharField(
        max_length=50,
        blank=True,
        help_text="Observaciones del movimiento"
    )

    # Opcional: si tienes fecha/hora del movimiento (no aparece en la estructura pero es muy común)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'caja_detalle'
        verbose_name = 'Detalle de Caja'
        verbose_name_plural = 'Detalle de Cajas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Caja {self.caja} - {self.importe} ({self.get_formapago_display() or self.formapago})"