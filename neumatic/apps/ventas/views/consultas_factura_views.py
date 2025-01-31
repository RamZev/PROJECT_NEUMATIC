# D:\SIG_PROJECTS\SIGCOERP\apps\facturacion\views\consultas_factura_views.py
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import F

from apps.maestros.models.producto_models import Producto
from apps.maestros.models.cliente_models import Cliente

import json

def buscar_producto(request):
    # Capturar parámetros de la solicitud
    medida = request.GET.get('medida', '')
    nombre = request.GET.get('nombre', '')
    cai = request.GET.get('cai', '')

    # Realizar la consulta inicial
    productos = Producto.objects.all()

    # Aplicar filtros dinámicamente
    if medida:
        productos = productos.filter(medida__icontains=medida)
    if nombre:
        productos = productos.filter(nombre_producto__icontains=nombre)
    if cai:
        productos = productos.filter(id_cai__descripcion_cai__icontains=cai)

    # Preparar los datos de respuesta
    resultados = [
        {
            'marca': producto.id_marca.nombre_producto_marca if producto.id_marca else 'Sin marca',
            'medida': producto.medida,
            'nombre': producto.nombre_producto,
            'precio': producto.precio,
            'stock': 0,  # Valor fijo
            'minimo': 0,  # Valor fijo
            'estatus': ''  # Cadena vacía
        }
        for producto in productos
    ]

    # Devolver los resultados como JSON
    return JsonResponse(resultados, safe=False)


def validar_documento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Validando!")
        
        nro_doc_identidad = data.get('nro_doc_identidad')
        print(nro_doc_identidad)

        # Busca el documento en el modelo Cliente
        try:
            agenda = Cliente.objects.filter(cuit=nro_doc_identidad).first()
            
            if agenda:
                print("Aquí es cliente:", agenda.nombre_cliente)
                print("Aquí es domicilio:", agenda.domicilio_cliente)
                
                response_data = {
                    'exists': True,
                    'nombre_receptor': agenda.nombre_cliente,
                    'domicilio_receptor': agenda.domicilio_cliente
                }
            else:
                response_data = {
                    'exists': False
                }
        except Exception as e:
            print(f"Error al validar documento: {e}")
            response_data = {
                'exists': False,
                'error': 'Error al validar el documento'
            }

        return JsonResponse(response_data)
    
# Búsqueda en Agenda para la ventana Modal de Factura
def buscar_agenda(request):
    busqueda_general = request.GET.get('busqueda_general', '')

    try:
        id_cliente = int(busqueda_general)
        clientes = Cliente.objects.filter(
            Q(id_cliente=id_cliente) |
            Q(nombre_cliente__icontains=busqueda_general)
        )
    except ValueError:
        clientes = Cliente.objects.filter(
            Q(nombre_cliente__icontains=busqueda_general)
        )

    resultados = clientes.values(
        'id_cliente',
        'cuit',
        'nombre_cliente',
        'domicilio_cliente',
        'codigo_postal',
        'movil_cliente',
        'email_cliente',
        'id_vendedor',
        'id_vendedor__nombre_vendedor',
        'id_sucursal',
        'vip',
        'mayorista',
        'sub_cuenta',
        'observaciones_cliente',
        'black_list',
        'black_list_motivo',
    )
    
    #print("resultados", resultados)

    return JsonResponse(list(resultados), safe=False)