# neumatic\apps\maestros\models\proveedor_models.py
from django.db import models
from .base_gen_models import ModeloBaseGenerico
from .base_models import Localidad  # Importar modelo Localidad
from .base_models import TipoIva  # Importar modelo TipoIVA
from .base_models import TipoRetencionIb  # Importar modelo TipoRetencionIB
from entorno.constantes_base import ESTATUS_GEN


class Proveedor(ModeloBaseGenerico):
    id_proveedor = models.AutoField(primary_key=True)
    estatus_proveedor = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
    nombre_proveedor = models.CharField(max_length=50)
    domicilio_proveedor = models.CharField(max_length=50)
    id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)
    codigo_postal = models.CharField(max_length=5)
    id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.CASCADE)
    cuit = models.BigIntegerField()
    id_tipo_retencion_ib = models.ForeignKey(TipoRetencionIb, on_delete=models.CASCADE)  
    ib_numero = models.CharField(max_length=15)
    ib_exento = models.BooleanField()
    ib_alicuota = models.DecimalField(max_digits=6, decimal_places=2)
    multilateral = models.BooleanField()
    telefono_proveedor = models.CharField(max_length=15)
    movil_proveedor = models.CharField(max_length=15)
    email_proveedor = models.EmailField(max_length=50)
    observacion_proveedor = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre_proveedor']

    def __str__(self):
        return self.nombre_proveedor
