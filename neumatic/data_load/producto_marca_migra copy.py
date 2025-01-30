# neumatic\data_load\producto_marca_migra.py
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

from apps.maestros.models.base_models import ProductoMarca

def reset_producto_marca():
    """Elimina los datos existentes en la tabla ProductoMarca y resetea su ID en SQLite."""
    ProductoMarca.objects.all().delete()  # Eliminar los datos existentes
    
    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='producto_marca';")

def cargar_datos():
    """Lee los datos de la tabla marcas.dbf, asegura que el código sea consecutivo,
    migra los datos al modelo ProductoMarca y elimina los registros marcados como pendientes."""
    reset_producto_marca()  # Eliminar datos existentes antes de migrar

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'marcas.DBF')

    # Abrir la tabla de Visual FoxPro usando dbfread y ordenarla por CODIGO
    table = sorted(DBF(dbf_path, encoding='latin-1'), key=lambda r: r['CODIGO'])

    expected_codigo = 1  # El código esperado para asegurar consecutividad

    for record in table:
        codigo = record['CODIGO']

        # Revisar si el código es consecutivo
        while expected_codigo < codigo:
            # Insertar un registro pendiente si hay un salto en el código
            ProductoMarca.objects.create(
                estatus_producto_marca=True,
                nombre_producto_marca="PENDIENTE DE ELIMINACIÓN",
                principal=False,
                info_michelin_auto=False,
                info_michelin_camion=False,
                id_moneda=1  # Moneda por defecto
            )
            expected_codigo += 1

        # Crear el registro actual
        moneda = record['MONEDA'].strip()
        id_moneda = 1 if moneda == "P" else 2 if moneda == "D" else 4

        ProductoMarca.objects.create(
            estatus_producto_marca=True,
            nombre_producto_marca=record['NOMBRE'].strip(),
            principal=False,
            info_michelin_auto=False,
            info_michelin_camion=False,
            id_moneda=id_moneda
        )

        expected_codigo += 1

    # Eliminar los registros marcados como "PENDIENTE DE ELIMINACIÓN"
    ProductoMarca.objects.filter(nombre_producto_marca="PENDIENTE DE ELIMINACIÓN").delete()

if __name__ == '__main__':
    cargar_datos()
    print("Migración de ProductoMarca completada.")
