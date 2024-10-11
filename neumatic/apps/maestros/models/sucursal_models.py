# neumatic\apps\maestros\models\sucursal_models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_gen_models import ModeloBaseGenerico
from .base_models import Provincia, Localidad
from entorno.constantes_base import ESTATUS_GEN


class Sucursal(ModeloBaseGenerico):
	id_sucursal = models.AutoField(primary_key=True)
	estatus_sucursal = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre_sucursal = models.CharField("Nombre sucursal", max_length=50)
	codigo_michelin = models.IntegerField("Código Michelin", 
									   validators=[MinValueValidator(1), 
												MaxValueValidator(99999)])
	domicilio_sucursal = models.CharField("Domicilio", max_length=50)
	id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, 
								  verbose_name="Localidad")
	id_provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, 
								  verbose_name="Provincia")
	telefono_sucursal = models.CharField("Teléfono", max_length=15)
	email_sucursal = models.EmailField("Correo", max_length=50)
	inicio_actividad = models.DateField("Inicio actividad")
	
	def __str__(self):
		return self.nombre_sucursal
	
	
	class Meta:
		db_table = 'sucursal'
		verbose_name = ('Sucursal')
		verbose_name_plural = ('Sucursales')
		ordering = ['nombre_sucursal']


''' Solo para cuadrar plantilla del form
	
	Línea 1
		estatus_sucursal = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
		nombre_sucursal = models.CharField("Nombre sucursal", max_length=50)
	
	Línea 2
		domicilio_sucursal = models.CharField("Domicilio", max_length=50)
		id_localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE, verbose_name="Localidad")
		id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE, verbose_name="Provincia")
	
	Línea 3
		telefono_sucursal = models.CharField("Teléfono", max_length=15)
		email_sucursal = models.EmailField("Correo", max_length=50)
		inicio_actividad = models.DateField("Inicio actividad")
		codigo_michelin = models.IntegerField("Código Michelin", validators=[MinValueValidator(1), MaxValueValidator(9999999999)])
	
'''