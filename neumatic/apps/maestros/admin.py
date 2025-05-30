# neumatic\apps\maestros\admin.py
from django.contrib import admin

from .models.cliente_models import Cliente
from .models.empresa_models import Empresa
from .models.numero_models import Numero
from .models.parametro_models import Parametro
from .models.producto_models import Producto
from .models.proveedor_models import Proveedor
from .models.sucursal_models import Sucursal
from .models.vendedor_models import Vendedor
from .models.base_models import *

# Registramos los modelos independientes
admin.site.register(Cliente)
admin.site.register(Empresa)
admin.site.register(Numero)
admin.site.register(Parametro)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(Sucursal)
admin.site.register(Vendedor)

# Registramos los modelos base
admin.site.register(Actividad)
admin.site.register(ComprobanteCompra)
admin.site.register(ComprobanteVenta)
admin.site.register(Localidad)
admin.site.register(Moneda)
admin.site.register(Operario)
admin.site.register(ProductoDeposito)
admin.site.register(ProductoEstado)
admin.site.register(ProductoFamilia)
admin.site.register(ProductoMarca)
admin.site.register(ProductoModelo)
admin.site.register(ProductoStock)
admin.site.register(Provincia)
admin.site.register(TipoDocumentoIdentidad)
admin.site.register(TipoIva)
admin.site.register(TipoPercepcionIb)
admin.site.register(TipoRetencionIb)
admin.site.register(Banco)
admin.site.register(Tarjeta)
admin.site.register(CodigoRetencion)
admin.site.register(ConceptoBanco)
