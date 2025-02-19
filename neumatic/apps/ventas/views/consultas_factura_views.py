# D:\SIG_PROJECTS\SIGCOERP\apps\facturacion\views\consultas_factura_views.py
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import F
from django.shortcuts import get_object_or_404


from apps.maestros.models.producto_models import Producto
from apps.maestros.models.cliente_models import Cliente
from apps.maestros.models.base_models import (ProductoStock, 
                                              ProductoMinimo)
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.descuento_vendedor_models import DescuentoVendedor

import json

def buscar_producto(request):
    # Capturar parámetros de la solicitud
    medida = request.GET.get('medida', '')
    nombre = request.GET.get('nombre', '')
    cai = request.GET.get('cai', '')
    filtro_marca = request.GET.get('filtro_marca', 'primeras')  # Valor por defecto
    id_cliente = request.GET.get('id_cliente', None)
    
    print("id_cliente", id_cliente)
    # Obtener el vendedor asociado al cliente
    vendedor = None
    col_descuento = 0  # Valor por defecto
    if id_cliente:
        cliente = Cliente.objects.filter(id_cliente=id_cliente).select_related("id_vendedor").first()
        if cliente and cliente.id_vendedor:
            vendedor = cliente.id_vendedor
            col_descuento = vendedor.col_descuento  # Obtener columna de descuento
            
            print("col_descuento", col_descuento)

    # Realizar la consulta inicial
    productos = Producto.objects.all()

    # Aplicar filtros dinámicamente
    if medida:
        productos = productos.filter(medida__icontains=medida)
    if nombre:
        productos = productos.filter(nombre_producto__icontains=nombre)
    if cai:
        productos = productos.filter(id_cai__descripcion_cai__icontains=cai)
        
    # Aplicar filtro de marcas o stock
    if filtro_marca == "primeras":
        productos = productos.filter(id_marca__principal=True)
    elif filtro_marca == "otras":
        print("Entró a otras")
        productos = productos.filter(id_marca__principal__in=[False, None])
    elif filtro_marca == "stock":
        print("stock")
        productos = productos.annotate(total_stock=Sum("productostock__stock")).filter(total_stock__gt=0)

    
    # Preparar los datos de respuesta usando lista por comprensión
    resultados = [
        {
            'id': producto.id_producto,
            'marca': producto.id_marca.nombre_producto_marca if producto.id_marca else 'Sin marca',
            'medida': producto.medida,
            'cai': producto.id_cai.descripcion_cai if producto.id_cai else 'Sin CAI',
            'nombre': producto.nombre_producto,
            'precio': producto.precio,
            'stock': ProductoStock.objects.filter(id_producto=producto).aggregate(total_stock=Sum('stock'))['total_stock'] or 0,
            'minimo': ProductoMinimo.objects.filter(id_cai=producto.id_cai).aggregate(total_minimo=Sum('minimo'))['total_minimo'] or 0,
            'id_marca': producto.id_marca_id if producto.id_marca else None,
            'id_familia': producto.id_familia_id if producto.id_familia else None,
            'descuento_vendedor': (
                DescuentoVendedor.objects.filter(id_marca=producto.id_marca, id_familia=producto.id_familia)
                .values(f"desc{col_descuento}").first().get(f"desc{col_descuento}", 0) if col_descuento > 0 else 0
            )
        }
        for producto in productos
    ]

    # print(resultados)

    # Devolver los resultados como JSON
    return JsonResponse(resultados, safe=False)


def detalle_producto(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    # Obtener stock por depósito
    stock_por_deposito = ProductoStock.objects.filter(id_producto=producto).select_related('id_deposito')
    stock_data = [
        {
            'deposito': stock.id_deposito.nombre_producto_deposito,
            'stock': stock.stock
        }
        for stock in stock_por_deposito
    ]
    
    # Obtener mínimos por depósito (usando id_cai)
    minimos_por_deposito = ProductoMinimo.objects.filter(id_cai=producto.id_cai).select_related('id_deposito')
    minimos_data = [
        {
            'deposito': minimo.id_deposito.nombre_producto_deposito,
            'minimo': minimo.minimo
        }
        for minimo in minimos_por_deposito
    ]

    return JsonResponse({'stock': stock_data, 'minimos': minimos_data})


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
            Q(cuit=id_cliente) |
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
        'id_vendedor__tipo_venta',
        'id_tipo_iva__discrimina_iva',
        'condicion_venta',
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

def buscar_cliente(request):
    busqueda = request.GET.get('busqueda', '').strip()
    
    print("busqueda", busqueda)

    # Si el input está vacío, no hacer búsqueda
    if not busqueda:
        return JsonResponse({'error': 'No se proporcionó un criterio de búsqueda'}, status=400)

    try:
        # Intentamos convertir a entero para buscar por ID o CUIT
        busqueda_num = int(busqueda)
        cliente = Cliente.objects.filter(
            Q(id_cliente=busqueda_num) | Q(cuit=busqueda_num)
        ).first()
    except ValueError:
        # Si no es un número, devolvemos error
        return JsonResponse({'error': 'Solo se permiten valores numéricos'}, status=400)

    if cliente:
        response_data = {
            'id_cliente': cliente.id_cliente,
            'nombre': cliente.nombre_cliente,
            'direccion': cliente.domicilio_cliente,
            'cuit': cliente.cuit,
            'movil': cliente.movil_cliente,
            'email': cliente.email_cliente,
            'id_vendedor': cliente.id_vendedor.id_vendedor if cliente.id_vendedor else None,
            'nombre_vendedor': cliente.id_vendedor.nombre_vendedor if cliente.id_vendedor else "Sin asignar",
            'id_sucursal': cliente.id_sucursal.id_sucursal,
            'vip': cliente.vip,
        }
    else:
        response_data = {'error': 'No se encontraron resultados'}
        
    # print("response_data", response_data)

    return JsonResponse(response_data)
