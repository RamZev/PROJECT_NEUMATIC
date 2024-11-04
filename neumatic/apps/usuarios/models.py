# D:\PROJECT_NEUMATIC\neumatic\apps\usuarios\models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import re

# from apps.maestros.models.vendedor_models import Vendedor
# from apps.maestros.models.sucursal_models import Sucursal


class User(AbstractUser):
	email = models.EmailField("Correo electrónico")
	email_alt = models.EmailField("Correo alternativo", max_length=50,
								null=True, blank=True)
	telefono = models.CharField("Teléfono", max_length=15,
								null=True, blank=True)
	
	iniciales = models.CharField("Iniciales", max_length=3,
								null=True, blank=True)
	jerarquia = models.CharField("Jerarquía", max_length=1,
								null=True, blank=True)
	# vendedor = models.BooleanField(default=False, null=True, blank=True)
	id_vendedor = models.ForeignKey('maestros.Vendedor', on_delete=models.PROTECT,
									null=True, blank=True,
									verbose_name="Vendedor")
	id_sucursal = models.ForeignKey('maestros.Sucursal', on_delete=models.PROTECT,
									verbose_name="Sucursal", null=True, blank=True)
	punto_venta = models.IntegerField("Punto de Venta", null=True, blank=True)

	def clean(self):
		super().clean()
		
		errors = {}
		
		punto_venta_str = str(self.punto_venta) if self.punto_venta is not None else ""
		
		if not re.match(r'^[1-9]\d{0,4}$|^0$|^$', punto_venta_str):
			errors.update({'punto_venta': 'El valor debe ser un número entero positivo, con hasta 5 dígitos, cero o vacío.'})
		
		if errors:
			raise ValidationError(errors)

# -- Al crear un nuevo usuario este quede activo por defecto.
@receiver(post_save, sender=User)
def set_user_active(sender, instance, created, **kwargs):
	if created and not instance.is_active:
		instance.is_active = True
		instance.save()
