# D:\PROJECT_NEUMATIC\neumatic\apps\ventas\models\numero.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .sucursal_models import Sucursal

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
    (True, 'Activo'),
    (False, 'Inactivo'),
]


class Numero(ModeloBaseGenerico):
    id_numero = models.AutoField(primary_key=True)
    estatus_numero = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    punto_venta = models.IntegerField()
    comprobante = models.CharField(max_length=3)
    letra = models.CharField(max_length=1)
    numero = models.IntegerField()
    lineas = models.IntegerField()
    copias = models.IntegerField()

    class Meta:
        db_table = 'numero'
        verbose_name = 'Número de Comprobante'
        verbose_name_plural = 'Números de Comprobante'
        ordering = ['punto_venta', 'comprobante']


