# neumatic\data_load\producto_estado_migra.py
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

from apps.maestros.models.base_models import ProductoEstado  # Asegúrate de que esta ruta sea correcta

def reset_tabla():
    """Elimina los datos existentes en la tabla Actividad y resetea su ID en SQLite."""
    ProductoEstado.objects.all().delete()  # Eliminar los datos existentes
    print("Tabla Actividad limpiada.")

    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='producto_estado';")
    print("Secuencia de ID reseteada.")

def cargar_datos():
    """Lee los datos de la tabla actividad.DBF, verifica consecutividad de códigos,
    migra los registros al modelo Actividad y añade pendientes si hay saltos en los códigos."""
    reset_tabla()  # Limpiar datos existentes

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'listaestados.DBF')

    # Abrir la tabla de Visual FoxPro y ordenarla por CODIGO
    # table = sorted(DBF(dbf_path, encoding='latin-1'), key=lambda r: r['CODIGO'])
    table = DBF(dbf_path, encoding='latin-1')

    # Recorrer la tabla e insertar los registros
    for record in table:
        estatus = True
        estado = record['ESTADO'].strip()
        nombre = record['NOMBRE'].strip()

        # Crear el registro actual
        ProductoEstado.objects.create(
            estatus_producto_estado=estatus,
            estado_producto=estado,
            nombre_producto_estado=nombre
        )

    print(f"Se han migrado {len(table)} registros de Actividad de forma exitosa.")

if __name__ == '__main__':
    cargar_datos()
    print("Migración de Actividad completada.")

