# neumatic\apps\maestros\models\proveedor_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
# from .base_models import Localidad  # Importar modelo Localidad
# from .base_models import TipoIva  # Importar modelo TipoIVA
# from .base_models import TipoRetencionIb  # Importar modelo TipoRetencionIB
from entorno.constantes_base import ESTATUS_GEN


class Proveedor(ModeloBaseGenerico):
	id_proveedor = models.AutoField(primary_key=True)
	estatus_proveedor = models.BooleanField("Estatus", default=True, 
										 choices=ESTATUS_GEN)
	nombre_proveedor = models.CharField("Nombre proveedor", max_length=50)
	domicilio_proveedor = models.CharField("Domicilio", max_length=50)
	id_localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE, 
								  verbose_name="Localidad")
	codigo_postal = models.CharField("Código postal", max_length=5)
	id_tipo_iva = models.ForeignKey('TipoIva', on_delete=models.CASCADE, 
								 verbose_name="Tipo IVA")
	cuit = models.IntegerField("C.U.I.T.", 
							validators=[MinValueValidator(20000000000), 
				   						MaxValueValidator(34999999999)])
	id_tipo_retencion_ib = models.ForeignKey('TipoRetencionIb', 
										  on_delete=models.CASCADE, 
										  verbose_name="Tipo de Retención Ib")
	ib_numero = models.CharField("Ingreso Bruto*", max_length=15)
	ib_exento = models.BooleanField("Exento Ret. Ing. Bruto")
	ib_alicuota = models.DecimalField("Alíc. Ing. B.", max_digits=6, 
								   decimal_places=2)
	multilateral = models.BooleanField("Contrib. Conv. Multilateral")
	telefono_proveedor = models.CharField("Taléfono", max_length=15)
	movil_proveedor = models.CharField("Móvil", max_length=15)
	email_proveedor = models.EmailField("Correo", max_length=50)
	observacion_proveedor = models.TextField("Observaciones", blank=True, 
										  null=True)

	class Meta:
		db_table = 'proveedor'
		verbose_name = 'Proveedor'
		verbose_name_plural = 'Proveedores'
		ordering = ['nombre_proveedor']

	def __str__(self):
		return self.nombre_proveedor

''' Solo para cuadrar plantilla del form
	
	Línea 1
		estatus_proveedor = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
		nombre_proveedor = models.CharField("Nombre proveedor", max_length=50)
	
	Línea 2
		domicilio_proveedor = models.CharField("Domicilio", max_length=50)
		id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, verbose_name="Localidad")
		codigo_postal = models.CharField("Código postal", max_length=5)
	
	Línea 3
		telefono_proveedor = models.CharField("Taléfono", max_length=15)
		movil_proveedor = models.CharField("Móvil", max_length=15)
		email_proveedor = models.EmailField("Correo", max_length=50)
	
	Línea 4
		ib_numero = models.CharField("Ingreso Bruto*", max_length=15)
		cuit = models.IntegerField("C.U.I.T.")
		id_tipo_iva = models.ForeignKey(TipoIva, on_delete=models.CASCADE, verbose_name="Tipo IVA")
		
	Línea 5
		id_tipo_retencion_ib = models.ForeignKey(TipoRetencionIb, on_delete=models.CASCADE, verbose_name="Tipo de Retención Ib")
		ib_alicuota = models.DecimalField("Alíc. Ing. B.", max_digits=6, decimal_places=2)
		ib_exento = models.BooleanField("Exento Ret. Ing. Bruto")
		multilateral = models.BooleanField("Contrib. Conv. Multilateral")
		
	Línea 6
		observacion_proveedor = models.TextField("Observaciones", blank=True, null=True)

'''