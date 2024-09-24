# D:\PROJECT_NEUMATIC\neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .base_models import *

# -- Datos estándares aplicables a los modelos base
ESTATUS_GEN = [
    (True, 'Activo'),
    (False, 'Inactivo'),
]

class Empresa(ModeloBaseGenerico):
    id_empresa = models.AutoField(primary_key=True)
    estatus_empresa = models.BooleanField("Estatus", default=True,
                                          choices=ESTATUS_GEN)
    nombre_fiscal = models.CharField(max_length=50)
    nombre_comercial = models.CharField(max_length=50)
    domicilio_empresa = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=4)
    id_localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE)
    id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE)
    iva = models.CharField(max_length=3)
    cuit = models.DecimalField(max_digits=11, decimal_places=0)
    ingresos_bruto = models.CharField(max_length=15)
    inicio_actividad = models.DateField()
    cbu = models.BigIntegerField()
    cbu_alias = models.CharField(max_length=50)
    cbu_vence = models.DateField()
    telefono = models.CharField(max_length=20)
    email_empresa = models.CharField(max_length=50)
    web_empresa = models.CharField(max_length=50)
    logo_empresa = models.BinaryField()  # Para el campo 'image'
    ws_archivo_crt = models.CharField(max_length=50)
    ws_archivo_key = models.CharField(max_length=50)
    ws_token = models.TextField()
    ws_sign = models.TextField()
    ws_expiracion = models.DateField()
    ws_modo = models.DecimalField(max_digits=1, decimal_places=0)
    ws_vence = models.DateField()

    class Meta:
        db_table = 'empresa'
        verbose_name = ('Empresa')
        verbose_name_plural = ('Empresas')
        ordering = ['nombre_fiscal']
