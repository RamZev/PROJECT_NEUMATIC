# neumatic\data_load\actualiza_producto_cai.py
import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.producto_models import Producto, ProductoCai

# Ruta de la tabla de Visual FoxPro
dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'lista.DBF')

def asignar_cai_a_productos():
    start_time = time.time()  # Registrar el tiempo inicial

    # Abrir la tabla DBF
    print("Cargando datos desde la tabla DBF...")
    table = DBF(dbf_path, encoding='latin-1')

    # Crear un diccionario para buscar rápidamente por CODIGO en la tabla DBF
    dbf_data = {
        record['CODIGO']: record['CODFABRICA'].strip()
        for record in table
        if record['CODFABRICA'] and record['CODFABRICA'].strip()  # Ignorar valores vacíos
    }
    print(f"Total registros en lista.DBF con CAI válido: {len(dbf_data)}")

    # Recorrer los registros del modelo Producto
    productos_actualizados = 0
    for producto in Producto.objects.all():
        # Buscar en la tabla DBF usando el campo CODIGO
        codigo = producto.id_producto  # Asumimos que id_producto corresponde a CODIGO
        valor_cai = dbf_data.get(codigo)

        if valor_cai:
            # Buscar el valor en el modelo ProductoCai
            try:
                producto_cai = ProductoCai.objects.get(cai=valor_cai)
                # Asignar el id_cai al producto
                producto.id_cai = producto_cai
                producto.save()  # Guardar los cambios en el producto
                productos_actualizados += 1
            except ProductoCai.DoesNotExist:
                print(f"CAI '{valor_cai}' no encontrado en ProductoCai para el producto {codigo}")

    print(f"Total productos actualizados: {productos_actualizados}")
    print(f"Proceso completado en {time.time() - start_time:.2f} segundos.")

if __name__ == '__main__':
    asignar_cai_a_productos()
