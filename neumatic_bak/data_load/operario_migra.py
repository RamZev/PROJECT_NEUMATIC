import os
import sys
import django
import time  # Para medir el tiempo de procesamiento
from dbfread import DBF
from django.db import connection
from datetime import date

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

# Importación de los modelos
from apps.maestros.models.base_models import Operario


# Tabla origen y modelo destino
tabla_origen = 'operario.DBF'
modelo_dest = Operario

# Ruta de la tabla de Visual FoxPro
dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', tabla_origen)

# Abrir la tabla de Visual FoxPro usando dbfread
table = DBF(dbf_path, encoding='latin-1')

# Rango de registros 
codigo_inicio = 1
codigo_final = None     # Hasta el final

# Nombre de variable id en la tabla origen
codigo_id = "CODIGO"

# Filtrar y ordenar la tabla DBF
table = sorted(
    [
        record
        for record in table
        if int(record.get(codigo_id, 0)) >= codigo_inicio and 
           (codigo_final is None or int(record.get(codigo_id, 0)) <= codigo_final)
    ],
    key=lambda record: int(record.get(codigo_id, 0))
)

total_registros = len(table)
print(f"{tabla_origen}: Total de registros a procesar: {total_registros}")

# Datos de ajuste


# Ejemplos base para asignar valores 
''' ejemplos base para asignar valores 
    record.get('NOMBRE', '').strip(),   # String
    int(record.get('MICHELIN', 0)),     # Integer
    float(record.get('EXENTO') or 0)    # Float
    record.get('INICIOACT', None)       # Date
    bool(record.get('PROMO', False))    # Boolean
'''

# Procesar registros
for idx, record in enumerate(table):
    id_origen = int(record.get(codigo_id, 0))
    # print(f"Procesando {tabla_origen} con ID: {id_origen}")

    # Evitar duplicados
    if modelo_dest.objects.filter(id_operario=id_origen).exists():
        print(f"{tabla_origen} con ID {id_origen} ya existe. Saltando registro.")
        continue

    # Crear registro
    try:
        modelo_dest.objects.create(
            id_operario=id_origen,
            estatus_operario=True,
            nombre_operario=record.get('NOMBRE', '').strip(),
            telefono_operario="sin-telefono",
            email_operario="sin-email@dominio.com",

        )
        print(f"{tabla_origen} con ID {id_origen} creado exitosamente.")
    except Exception as e:
        print(f"Error al crear {tabla_origen} con ID {id_origen}: {e}")
        continue
    
print(f"La migración de la tabla {tabla_origen} terminó con éxito!")
