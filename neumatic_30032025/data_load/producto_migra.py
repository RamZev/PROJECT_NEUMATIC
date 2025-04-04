# neumatic\data_load\producto_migra.py
import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF
from django.db import connection

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import ProductoFamilia
from apps.maestros.models.base_models import ProductoMarca
from apps.maestros.models.base_models import ProductoModelo

def reset_producto():
    """Elimina los datos existentes en la tabla Producto y resetea su ID en SQLite."""
    Producto.objects.all().delete()  # Eliminar los datos existentes
    
    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='producto';")

def cargar_datos():
    """Lee los datos de la tabla lista.dbf, asegura que el código sea consecutivo,
    migra los datos al modelo Producto y elimina los registros marcados como pendientes."""
    reset_producto()  # Eliminar datos existentes antes de migrar

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'lista.DBF')

    # Abrir la tabla de Visual FoxPro usando dbfread y ordenarla por CODIGO
    table = sorted(DBF(dbf_path, encoding='latin-1'), key=lambda r: r['CODIGO'])

    expected_codigo = 1  # El código esperado para asegurar consecutividad
    total_registros = len(table)  # Número total de registros

    print(f"Total de registros a procesar: {total_registros}")

    for idx, record in enumerate(table):
        codigo = int(record['CODIGO'])

        # Obtener instancias relacionadas para ProductoFamilia, ProductoMarca y ProductoModelo
        try:
            familia = ProductoFamilia.objects.get(pk=record.get('ARTICULO'))
            marca = ProductoMarca.objects.get(pk=record.get('MARCA'))
            modelo = ProductoModelo.objects.get(pk=record.get('MODELO'))
        except ProductoFamilia.DoesNotExist:
            print(f"Código {codigo}: Error en articulo {record.get('ARTICULO')}")
            continue
        except ProductoMarca.DoesNotExist:
            print(f"Código {codigo}: Error en marca {record.get('MARCA')}")
            continue
        except ProductoModelo.DoesNotExist:
            print(f"Código {codigo}: Error en modelo {record.get('MODELO')}")
            continue

        # Validar y obtener valores con predeterminados si son nulos
        tipo_producto = record.get('TIPO', '').strip()
        cai = record.get('CODFABRICA', '').strip()
        medida = record.get('MEDIDA', '').strip()
        segmento = record.get('SEGMENTO', '').strip()
        nombre_producto = record.get('NOMBRE', 'Sin Nombre').strip()
        unidad = record.get('UNIDAD', 0) or 0
        fecha_fabricacion = record.get('FECHA', '').strip()
        costo = record.get('COSTO', 0.00) or 0.00
        alicuota_iva = record.get('IVA', 0.00) or 0.00
        precio = record.get('PRECIO', 0.00) or 0.00
        stock = record.get('STOCK', 0) or 0
        minimo = record.get('MINIMO', 0) or 0
        descuento = record.get('DESCUENTO', 0.00) or 0.00
        despacho_1 = record.get('DESPACHO1', '').strip()
        despacho_2 = record.get('DESPACHO2', '').strip()
        descripcion_producto = record.get('DETALLE', '').strip()
        carrito = record.get('CARRITO', False) or False

        # Crear el registro actual
        Producto.objects.create(
            id_producto=codigo,
            estatus_producto=True,
            codigo_producto=str(codigo).strip(),
            tipo_producto=tipo_producto,
            id_familia=familia,
            id_marca=marca,
            id_modelo=modelo,
            cai=cai,
            medida=medida,
            segmento=segmento,
            nombre_producto=nombre_producto,
            unidad=unidad,
            fecha_fabricacion=fecha_fabricacion,
            costo=costo,
            alicuota_iva=alicuota_iva,
            precio=precio,
            stock=stock,
            minimo=minimo,
            descuento=descuento,
            despacho_1=despacho_1,
            despacho_2=despacho_2,
            descripcion_producto=descripcion_producto,
            carrito=carrito
        )

        expected_codigo += 1

        # Mostrar mensaje cada 100 registros procesados
        if (idx + 1) % 100 == 0:
            print(f"{idx + 1} registros procesados...")



if __name__ == '__main__':
    start_time = time.time()  # Empezar el control de tiempo
    cargar_datos()
    end_time = time.time()  # Terminar el control de tiempo

    # Calcular el tiempo total en minutos y segundos
    elapsed_time = end_time - start_time
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    print(f"Migración de Producto completada.")
    print(f"Tiempo de procesamiento: {int(minutes)} minutos y {int(seconds)} segundos.")
