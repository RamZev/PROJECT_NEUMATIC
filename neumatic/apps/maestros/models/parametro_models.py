# D:\PROJECT_NEUMATIC\neumatic\apps\maestros\models\parametro.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .empresa_models import Empresa

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
    (True, 'Activo'),
    (False, 'Inactivo'),
]

class Parametro(ModeloBaseGenerico):
    id_parametro = models.AutoField(primary_key=True)  # Clave primaria
    estatus_parametro = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)  # Estatus del parámetro
    id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 
    interes = models.DecimalField(max_digits=6, decimal_places=2)
    dolar = models.DecimalField(max_digits=10, decimal_places=4)
    cierreventas = models.DateField()
    bonificacion = models.BooleanField(default=False)
    precios = models.BooleanField(default=False)
    descripcion_parametro = models.BooleanField(default=False)

    class Meta:
        db_table = 'parametro'
        verbose_name = 'Parámetro'
        verbose_name_plural = 'Parámetros'
        ordering = ['id_empresa']
