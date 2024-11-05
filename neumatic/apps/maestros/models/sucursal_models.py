# neumatic\apps\maestros\models\sucursal_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
from .base_models import Provincia, Localidad
from entorno.constantes_base import ESTATUS_GEN


class Sucursal(ModeloBaseGenerico):
	id_sucursal = models.AutoField(primary_key=True)
	estatus_sucursal = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre_sucursal = models.CharField("Nombre sucursal", max_length=50)
	codigo_michelin = models.IntegerField("Código Michelin")
	domicilio_sucursal = models.CharField("Domicilio", max_length=50)
	codigo_postal = models.CharField("Código Postal*", max_length=5)
	id_provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, 
								  verbose_name="Provincia")
	id_localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, 
								  verbose_name="Localidad")
	telefono_sucursal = models.CharField("Teléfono", max_length=15)
	email_sucursal = models.EmailField("Correo", max_length=50)
	inicio_actividad = models.DateField("Inicio actividad")
	
	
	def __str__(self):
		return self.nombre_sucursal

	def clean(self):
		super().clean()
		
		errors = {}
		
		codigo_michelin_str = str(self.codigo_michelin) if self.codigo_michelin else ""
		
		if not re.match(r'^\d{1,5}$', codigo_michelin_str):
			errors.update({'codigo_michelin': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 5.'})
		
		if not re.match(r'^\+?\d[\d ]{0,14}$', str(self.telefono_sucursal)):
			errors.update({'telefono_sucursal': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if errors:
			raise ValidationError(errors)
	
	
	class Meta:
		db_table = 'sucursal'
		verbose_name = ('Sucursal')
		verbose_name_plural = ('Sucursales')
		ordering = ['nombre_sucursal']
