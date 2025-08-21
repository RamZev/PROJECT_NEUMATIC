# neumatic/data_load/actualizar_usuario_admin.py
import os
import sys
import django

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.usuarios.models import User
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.base_models import PuntoVenta
from apps.maestros.models.vendedor_models import Vendedor


def actualizar_usuario_administrador():
    """Actualiza el usuario con ID=1 con los valores específicos"""
    try:
        # Obtener el usuario con ID=1
        usuario = User.objects.get(id=1)

        print("pasó 1")
        
        # Obtener las instancias relacionadas
        punto_venta = PuntoVenta.objects.get(id_punto_venta=2)
        sucursal = Sucursal.objects.get(id_sucursal=2)
        vendedor = Vendedor.objects.get(id_vendedor=1)

        print("pasó 2")
        
        # Actualizar los campos
        usuario.id_punto_venta = punto_venta
        usuario.id_sucursal = sucursal
        usuario.id_vendedor = vendedor

        print("pasó 3")
        
        # Guardar los cambios
        usuario.save()
        
        print("✅ Usuario actualizado correctamente:")
        print(f"ID: {usuario.id}")
        print(f"Username: {usuario.username}")
        print(f"Punto de Venta: {punto_venta.id_punto_venta} - {punto_venta}")
        print(f"Sucursal: {sucursal.id_sucursal} - {sucursal}")
        print(f"Vendedor: {vendedor.id_vendedor} - {vendedor}")
        
    except User.DoesNotExist:
        print("❌ Error: No existe un usuario con ID=1")
    except PuntoVenta.DoesNotExist:
        print("❌ Error: No existe el Punto de Venta con ID=2")
    except Sucursal.DoesNotExist:
        print("❌ Error: No existe la Sucursal con ID=2")
    except Vendedor.DoesNotExist:
        print("❌ Error: No existe el Vendedor con ID=1")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == '__main__':
    print("Iniciando actualización del usuario administrador...")
    actualizar_usuario_administrador()