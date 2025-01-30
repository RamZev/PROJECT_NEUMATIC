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

from apps.maestros.models.cliente_models import Cliente, Vendedor, Sucursal
from apps.maestros.models.base_models import *

def reset_cliente():
    """Elimina los datos existentes en la tabla Cliente y resetea su ID en SQLite."""
    # Cliente.objects.all().delete()  # Eliminar los datos existentes
    
    # Reiniciar el autoincremento en SQLite
    with connection.cursor() as cursor:
        pass
        # cursor.execute("DELETE FROM sqlite_sequence WHERE name='cliente';")
        # cursor.execute("UPDATE sqlite_sequence SET seq = 1033 WHERE name = 'cliente';")

def cargar_datos():
    """Lee los datos de la tabla clientes.dbf, asegura que el código sea consecutivo,
    migra los datos al modelo Cliente y elimina los registros marcados como pendientes."""
    reset_cliente()  # Eliminar datos existentes antes de migrar

    # Ruta de la tabla de Visual FoxPro
    dbf_path = os.path.join(BASE_DIR, 'data_load', 'datavfox', 'clientes.DBF')

    # Abrir la tabla de Visual FoxPro usando dbfread
    table = DBF(dbf_path, encoding='latin-1')
    
    table = sorted(table, key=lambda x: x['CODIGO'])

    total_registros = len(table)  # Número total de registros
    print(f"Total de registros a procesar: {total_registros}")

    codigo_inicio = 1034
    # codigo_inicio = 69025
    # codigo_inicio = 119961
    # codigo_inicio = 132780
    # codigo_inicio = 136688
    # codigo_inicio = 142170
    # codigo_inicio = 144339
    # codigo_inicio = 145266
    # codigo_inicio = 147762 # son 2
    
    # Filtrar los registros a partir del código inicial
    table = [record for record in table if int(record['CODIGO']) >= codigo_inicio]

    # Obtener instancias predeterminadas para claves foráneas
    try:
        id_tipo_iva_instancia = TipoIva.objects.get(pk=1)
    except (TipoIva.DoesNotExist, ValueError):
        id_tipo_iva_instancia = None

    try:
        id_tipo_documento_identidad_instancia = TipoDocumentoIdentidad.objects.get(pk=1)
    except (TipoDocumentoIdentidad.DoesNotExist, ValueError):
        id_tipo_documento_identidad_instancia = None
    
    try:
        id_vendedor_instancia = Vendedor.objects.get(pk=1)
    except Vendedor.DoesNotExist:
        id_vendedor_instancia = None

    try:
        id_actividad_instancia = Actividad.objects.get(pk=1)
    except (Actividad.DoesNotExist, ValueError):
        id_actividad_instancia = None

    try:
        id_sucursal_instancia = Sucursal.objects.get(pk=11)
    except (Sucursal.DoesNotExist, ValueError):
        id_sucursal_instancia = None

    try:
        id_percepcion_ib_instancia = TipoPercepcionIb.objects.get(pk=1)
    except (TipoPercepcionIb.DoesNotExist, ValueError):
        id_percepcion_ib_instancia = None

    for idx, record in enumerate(table):
        # Omitir registros marcados como pendientes
        if record.get('PENDIENTE', False):
            continue
        
        ######################
        # Obtener el código de la tabla origen
        codigo_origen = int(record.get('CODIGO', 0))  # Suponiendo que 'CODIGO' es el campo del ID en la tabla origen
        

        # Ejecutar la consulta con un marcador de posición
        nuevo_id = codigo_origen - 1
        # print(f"Executing: UPDATE sqlite_sequence SET seq = {nuevo_id} WHERE name = 'cliente';")

        sql_consult = f"UPDATE sqlite_sequence SET seq = {nuevo_id} WHERE name = 'cliente';"
        # Reiniciar el autoincremento en SQLite
        with connection.cursor() as cursor:
            # cursor.execute("DELETE FROM sqlite_sequence WHERE name='cliente';")
            cursor.execute(sql_consult)
        
        #######################
        

        # Extraer y procesar los datos según las reglas
        codigo_postal = str(record.get('CODPOSTAL', ''))[:4]  # Tomar las primeras 4 posiciones del código postal
        try:
            localidades = Localidad.objects.filter(codigo_postal=codigo_postal)
            if localidades.count() > 1:
                pass
            
            localidad = localidades.first()
            
            if not localidad:
                # print(f"Error: No se encontró localidad para el código postal {codigo_postal}. Saltando cliente.")
                continue  # Saltar el registro problemático
            
            # Instanciar id_localidad e id_provincia
            id_localidad_instancia = Localidad.objects.get(pk=localidad.id_localidad) if localidad else None
            id_provincia_instancia = Provincia.objects.get(pk=localidad.id_provincia.id_provincia) if localidad else None
        except Localidad.DoesNotExist:
            id_localidad_instancia = None
            id_provincia_instancia = None

        # Asegurarse de que 'CONVTA' es de tipo cadena antes de aplicarle strip()
        condicion_venta = str(record.get('CONVTA')).strip() if isinstance(record.get('CONVTA'), str) else ""
        
        observaciones_cliente = record.get('OBSERVACIO', "") or ""
        observaciones_cliente = observaciones_cliente.strip() if isinstance(observaciones_cliente, str) else ""
        
        fecha_alta = record.get('FECHAING')
        # print('fecha_alta', fecha_alta)

        # Crear el registro en el modelo Cliente
        Cliente.objects.create(
            # Crear el registro en el modelo Cliente
            estatus_cliente=True,
            codigo_cliente=codigo_origen,
            nombre_cliente=record.get('NOMBRE', '').strip(),
            domicilio_cliente=record.get('DOMICILIO', '').strip(),
            codigo_postal=codigo_postal,
            id_localidad=id_localidad_instancia,
            id_provincia=id_provincia_instancia,
            tipo_persona=record.get('TIPOCLI', '').strip(),
            id_tipo_iva=id_tipo_iva_instancia,
            id_tipo_documento_identidad=id_tipo_documento_identidad_instancia,
            cuit = 0 if record.get('CUIT') is None or str(record.get('CUIT')).strip() == '' else int(str(record.get('CUIT')).strip()),
            condicion_venta = int(record.get('CONDCIONVENTA', 0)) if record.get('CONDCIONVENTA') else 0,
            telefono_cliente=record.get('TELEFONO', '').strip() if record.get('TELEFONO') else '',
            fax_cliente=record.get('FAX', '').strip() if record.get('FAX') else '',
            movil_cliente=record.get('MOVIL', '').strip() if record.get('MOVIL') else '',
            email_cliente=record.get('MAIL', '').strip() if record.get('MAIL') else '',
            email2_cliente="",
            transporte_cliente=record.get('TRANSPORTE', '').strip() if record.get('TRANSPORTE') else '',
            id_vendedor=id_vendedor_instancia,
            fecha_nacimiento = record.get('FECHANAC', '2024-01-01') if record.get('FECHANAC') is not None else None,
            fecha_alta = record.get('FECHAING', '2024-01-01') if record.get('FECHAING') is not None else '2024-01-01',
            sexo=int(record.get('SEXO', 0)) if record.get('SEXO') else 0,  # Tipo entero en modelo
            id_actividad=id_actividad_instancia,
            id_sucursal=id_sucursal_instancia,
            id_percepcion_ib=id_percepcion_ib_instancia,
            numero_ib="",
            mayorista = record.get('MAYORISTA', None) or False,
            # sub_cuenta=record.get('SUBCUENTA', '').strip() if record.get('SUBCUENTA') is not None else '',
            sub_cuenta = str(record.get('SUBCUENTA', '')).strip() if record.get('SUBCUENTA') is not None else '',
            observaciones_cliente = str(record.get('OBSERVACIO', "")).strip(),

            black_list=False,
            black_list_motivo="",
            black_list_usuario="",
            fecha_baja=None
        )

        # Mostrar mensaje cada 1000 registros procesados
        if (idx + 1) % 1000 == 0:
            print(f"{idx + 1} registros procesados...")

if __name__ == '__main__':
    start_time = time.time()  # Empezar el control de tiempo
    cargar_datos()
    end_time = time.time()  # Terminar el control de tiempo

    # Calcular el tiempo total en minutos y segundos
    elapsed_time = end_time - start_time
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    print(f"Migración de Cliente completada.")
    print(f"Tiempo de procesamiento: {int(minutes)} minutos y {int(seconds)} segundos.")
