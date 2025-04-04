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

# Ruta de la tabla de Visual FoxPro
dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'lista.DBF')

# Abrir la tabla de Visual FoxPro usando dbfread y ordenarla por CODIGO
table = sorted(DBF(dbf_path, encoding='latin-1'), key=lambda r: r['CODIGO'])

expected_codigo = 1  # El código esperado para asegurar consecutividad
total_registros = len(table)  # Número total de registros

print(f"Total de registros a procesar: {total_registros}")

