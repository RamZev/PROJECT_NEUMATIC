# D:\SIG_PROJECTS\SIGCOERP\apps\facturacion\views\consultas_factura_views.py
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import F
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.cliente_models import Cliente

import json

def buscar_producto(request):
    codigo = request.GET.get('codigo', '')
    nombre_producto = request.GET.get('descripcion', '')  # Nombre del campo en el modelo
    id_marca = request.GET.get('marca', '')  # Ajusta aquí si el nombre del campo es diferente

    productos = Producto.objects.all()

    if codigo:
        productos = productos.filter(codigo_producto__icontains=codigo)
    if nombre_producto:
        productos = productos.filter(nombre_producto__icontains=nombre_producto)
    if id_marca:
        productos = productos.filter(id_marca__nombre_marca__icontains=id_marca)  # Usar campo relacionado

    resultados = [
        {
            'codigo': producto.codigo_producto,
            'descripcion': producto.nombre_producto,
            'unidad': producto.id_unidad.nombre_unidad if producto.id_unidad else '',
            'marca': producto.id_marca.nombre_marca if producto.id_marca else '',
            'modelo': producto.id_modelo.nombre_modelo if producto.id_modelo else '',
            'cantidad': producto.stock_maximo,  # Ajusta según tu modelo
            'precio': producto.precio_promedio,  # Ajusta según tu modelo
            'stock': producto.stock_minimo,  # Ajusta según tu modelo
        }
        for producto in productos
    ]

    return JsonResponse(resultados, safe=False)


def validar_documento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Validando!")
        
        nro_doc_identidad = data.get('nro_doc_identidad')

        # Busca el documento en el modelo Cliente
        try:
            agenda = Cliente.objects.filter(nro_doc_identidad=nro_doc_identidad).first()
            
            if agenda:
                print("Aquí es:", agenda.nombre_cliente)
                
                response_data = {
                    'exists': True,
                    'nombre_receptor': agenda.nombre_cliente
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
    

def buscar_agenda(request):
    print("Se entró a la búsqueda de Clientes!")
    print("Parámetros GET recibidos:", request.GET)
    
    busqueda_general = request.GET.get('busqueda_general', '')

    # Iniciar la consulta
    clientes = Cliente.objects.all()

    # Aplicar filtros de búsqueda
    if busqueda_general:
        clientes = clientes.filter(
            Q(nombre_cliente__icontains=busqueda_general)
        )

    # Serializar los resultados con los campos requeridos
    resultados = clientes.values(
        'id_cliente',
        'cuit',
        'nombre_cliente',
        'domicilio_cliente',
        'codigo_postal'
    )

    return JsonResponse(list(resultados), safe=False)
