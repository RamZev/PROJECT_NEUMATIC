# neumatic\data_load\localidad_migra.py
import csv
import os
import sys
import django
from django.db import connection

# Añadir el directorio base del proyecto al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neumatic.settings')
django.setup()

from apps.maestros.models.base_models import Localidad, Provincia

def cargar_localidades_desde_csv(archivo_csv):
    """Carga los datos de localidades desde un archivo CSV y los migra al modelo Localidad."""
    # Abrir el archivo CSV y leer su contenido
    with open(archivo_csv, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        # Inicializar contador de filas procesadas
        filas_procesadas = 0

        # Resetear la tabla Localidad (eliminar los datos existentes)
        reset_localidades()

        # Iterar sobre cada fila del archivo CSV
        for row in reader:
            # Limpiar las claves del diccionario del CSV para evitar caracteres extraños
            row = {key.strip(): value for key, value in row.items()}

            # Asegurar que las claves existen en el diccionario del CSV
            if 'CP' in row and 'Localidad' in row and 'Cod_Provincia' in row:
                nombre_localidad = row['Localidad'].strip()
                codigo_postal = row['CP'].strip()
                codigo_provincia_csv = row['Cod_Provincia'].strip()

                # Obtener el objeto Provincia sumando 1 al código de provincia del CSV
                id_provincia = int(codigo_provincia_csv) + 1

                try:
                    #print("id_provincia try", id_provincia)
                    #provincia = Provincia.objects.get(codigo_provincia=str(id_provincia))
                    provincia = Provincia.objects.get(id_provincia=id_provincia)
                except Provincia.DoesNotExist:
                    print(f"Provincia con código {id_provincia} no encontrada. Fila omitida.")
                    continue  # Si no encuentra la provincia, saltar esta fila

                # Crear el registro de Localidad
                Localidad.objects.create(
                    estatus_localidad=True,  # Estatus en True
                    nombre_localidad=nombre_localidad,
                    id_provincia=provincia,
                    codigo_postal=codigo_postal
                )

                # Incrementar el contador de filas procesadas
                filas_procesadas += 1

                # Mostrar mensaje cada 100 filas procesadas
                if filas_procesadas % 100 == 0:
                    print(f"{filas_procesadas} filas procesadas...")
            else:
                print(f"Encabezados faltantes en la fila: {row}")

    print(f"Se han migrado {filas_procesadas} localidades de forma exitosa.")

def reset_localidades():
    """Elimina los datos existentes en la tabla Localidad y resetea su ID en SQLite."""
    # Eliminar los datos existentes en la tabla
    Localidad.objects.all().delete()

    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='localidad';")  # Ajustar el nombre de la tabla si es necesario

    print("Datos de la tabla Localidad eliminados y autoincremento reseteado.")

if __name__ == '__main__':
    # Ruta del archivo CSV
    archivo_csv = os.path.join(BASE_DIR, 'data_load', 'Codigos-Postales-Argentina.csv')

    # Ejecutar la migración
    cargar_localidades_desde_csv(archivo_csv)
