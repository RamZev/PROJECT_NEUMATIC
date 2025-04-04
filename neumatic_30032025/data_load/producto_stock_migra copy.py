# neumatic\data_load\producto_stock_migra.py
import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF
from django.db import connection
from datetime import date
from django.db import transaction

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

# Importación de los modelos
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.base_models import ProductoStock, ProductoDeposito


# Tabla origen y modelo destino
tabla_origen = 'stock.DBF'
modelo_dest = ProductoStock

# Ruta de la tabla de Visual FoxPro
dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', tabla_origen)

# Abrir la tabla de Visual FoxPro usando dbfread
# table = DBF(dbf_path, encoding='latin-1')
table = sorted(DBF(dbf_path, encoding='latin-1'), key=lambda r: (r['CODIGO'] or 0, r['DEPOSITO'] or 0))

total_registros = len(table)
print(f"{tabla_origen}: Total de registros a procesar: {total_registros}")

# Migrar los datos al modelo
registros_creados = 0
inicio = time.time()  # Registrar tiempo inicial

###
# Procesar registros
for idx, record in enumerate(table):
    codigo = int(record.get('CODIGO', 0))  # Convertir CODIGO a entero
    deposito = int(record.get('DEPOSITO', 0))  # Convertir DEPOSITO a entero    
    
    id_producto_instancia = Producto.objects.filter(id_producto=codigo).first()
    id_deposito_instancia = ProductoDeposito.objects.filter(id_producto_deposito=deposito).first()

    # Crear registro
    try:
        modelo_dest.objects.create(
            id_producto=id_producto_instancia,
            id_deposito=id_deposito_instancia,
            stock=record.get('STOCK', 0) or 0,
            #minimo=record.get('MINIMO', 0),  # Si MINIMO no existe, usar 0
            fecha_producto_stock=record.get('FECHA', date.today()),  # Si FECHA no existe, usar la fecha actual
        )

        # print(f"Registro de {tabla_origen} creado exitosamente.")
    except Exception as e:
        print(f"Error al crear el Registro {tabla_origen}: {e}")
        continue
    

###

fin = time.time()  # Registrar tiempo final
print(f"Total de registros procesados: {registros_creados}")
print(f"Tiempo total: {fin - inicio:.2f} segundos")



'''
stock.DBF ---> ProductoStock

id_producto_stock: automatico
id_producto: instanciar CODIGO
id_deposito: instanciar DEPOSITO
stock: STOCK
minimo: MINIMO
fecha_producto_stock: FECHA

SELECT * from stock order BY codigo, deposito
'''