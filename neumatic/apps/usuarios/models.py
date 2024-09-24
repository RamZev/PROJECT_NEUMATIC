# D:\PROJECT_NEUMATIC\neumatic\apps\usuarios\models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
  email = models.EmailField("Correo electrónico")
  email_alt = models.EmailField("Correo alternativo", max_length=50, 
                               null=True, blank=True)
  telefono = models.CharField("Teléfono", max_length=9, 
                             null=True, blank=True)
  
  iniciales = models.CharField("Iniciales", max_length=3, 
                             null=True, blank=True)
  jerarquia = models.CharField("Jerarquía", max_length=1, 
                             null=True, blank=True)
  vendedor = models.BooleanField(default=False, null=True, blank=True)
 
	# [id_vendedor] [int] NOT NULL,
	# [id_sucursal] [int] NOT NULL,
	# [punto_venta] [int] NOT NULL,

#-- Al crear un nuevo usuario este quede activo por defecto.
@receiver(post_save, sender=User)
def set_user_active(sender, instance, created, **kwargs):
	if created and not instance.is_active:
		instance.is_active = True
		instance.save()
