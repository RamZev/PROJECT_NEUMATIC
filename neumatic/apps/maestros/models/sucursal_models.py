# D:\PROJECT_NEUMATIC\neumatic\apps\maestros\models\sucursal_models.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .base_models import *

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
    (True, 'Activo'),
    (False, 'Inactivo'),
]


class Sucursal(ModeloBaseGenerico):
    id_sucursal = models.AutoField(primary_key=True)
    estatus_sucursal = models.BooleanField("Estatus", default=True,
                                           choices=ESTATUS_GEN)
    nombre_sucursal = models.CharField(max_length=50)
    domicilio_sucursal = models.CharField(max_length=50)
    id_localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE)
    id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE)
    telefono_sucursal = models.CharField(max_length=15)
    email_sucursal = models.CharField(max_length=50)
    inicio_actividad = models.DateField()
    codigo_michelin = models.IntegerField()

    class Meta:
        db_table = 'sucursal'
        verbose_name = ('Sucursal')
        verbose_name_plural = ('Sucursales')
        ordering = ['nombre_sucursal']

