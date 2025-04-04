# neumatic\data_load\descuento_vendedor_migra.py
import os
import sys
import django
from dbfread import DBF
from django.db import connection

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from neumatic.apps.maestros.models.descuento_vendedor_models import DescuentoVendedor 
from apps.maestros.models.base_models import ProductoMarca, ProductoFamilia

def reset_actividad():
    """Elimina los datos existentes en la tabla Actividad y resetea su ID en SQLite."""
    DescuentoVendedor.objects.all().delete()  # Eliminar los datos existentes
    print("Tabla Actividad limpiada.")

    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='descuento_vendedor';")
    print("Secuencia de ID reseteada.")

def cargar_datos():
    """Lee los datos de la tabla actividad.DBF, verifica consecutividad de códigos,
    migra los registros al modelo Actividad y añade pendientes si hay saltos en los códigos."""
    reset_actividad()  # Limpiar datos existentes

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'descvend.DBF')

    # Abrir la tabla de Visual FoxPro y ordenarla por CODIGO
    table = DBF(dbf_path, encoding='latin-1')

    expected_codigo = 1  # Código esperado para verificar consecutividad

    for record in table:
        marca = int(record.get('MARCA'))
        familia = int(record.get('ARTICULO'))
        
        try:
            # Intentar obtener las instancias de ProductoMarca y ProductoFamilia
            id_marca_instancia = ProductoMarca.objects.get(id_producto_marca=marca)
            id_familia_instancia = ProductoFamilia.objects.get(id_producto_familia=familia)
        except ProductoMarca.DoesNotExist:
            print(f"Advertencia: No se encontró ProductoMarca con id_producto_marca={marca}. Saltando registro.")
            continue  # Saltar al siguiente registro
        except ProductoFamilia.DoesNotExist:
            print(f"Advertencia: No se encontró ProductoFamilia con id_producto_familia={familia}. Saltando registro.")
            continue  # Saltar al siguiente registro
        
        # Crear el registro actual
        DescuentoVendedor.objects.create(
            estatus_descuento_vendedor=True,
            id_marca = id_marca_instancia,
            id_familia = id_familia_instancia,
            desc1 = float(record.get('DESC1') or 0),    
            desc2 = float(record.get('DESC2') or 0),    
            desc3 = float(record.get('DESC3') or 0),    
            desc4 = float(record.get('DESC4') or 0),    
            desc5 = float(record.get('DESC5') or 0),    
            desc6 = float(record.get('DESC6') or 0),    
            desc7 = float(record.get('DESC7') or 0),    
            desc8 = float(record.get('DESC8') or 0),    
            desc9 = float(record.get('DESC9') or 0),    
            desc10 = float(record.get('DESC10') or 0),
            desc11 = float(record.get('DESC11') or 0),    
            desc12 = float(record.get('DESC12') or 0),    
            desc13 = float(record.get('DESC13') or 0),    
            desc14 = float(record.get('DESC14') or 0),    
            desc15 = float(record.get('DESC15') or 0),    
            desc16 = float(record.get('DESC16') or 0),    
            desc17 = float(record.get('DESC17') or 0),    
            desc18 = float(record.get('DESC18') or 0),    
            desc19 = float(record.get('DESC19') or 0),    
            desc20 = float(record.get('DESC20') or 0),
            desc21 = float(record.get('DESC21') or 0),    
            desc22 = float(record.get('DESC22') or 0),    
            desc23 = float(record.get('DESC23') or 0),    
            desc24 = float(record.get('DESC24') or 0),    
            desc25 = float(record.get('DESC25') or 0),    
        )

    print(f"Se han migrado {len(table)} registros de Descuento de forma exitosa.")

if __name__ == '__main__':
    cargar_datos()
    print("Migración de Descuento Proveedor completada.")

