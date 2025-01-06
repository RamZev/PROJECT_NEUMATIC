from django.contrib import admin

from . models.facturas_models import Factura, DetalleFactura

admin.site.register(Factura)
admin.site.register(DetalleFactura)