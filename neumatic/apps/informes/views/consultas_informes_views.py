# D:\SIG_PROJECTS\SIGCOERP\apps\facturacion\views\consultas_factura_views.py
from django.http import JsonResponse
from django.db.models import Q

from apps.maestros.models.cliente_models import Cliente
# from apps.maestros.models.producto_models import Producto


#-- Buscar un cliente por su id.
def buscar_cliente_id(request):
	id_cliente = request.GET.get('id_cliente', '')
	print("Entra a buscar el cliente por su id", id_cliente)
	
	if id_cliente:
		try:
			cliente = Cliente.objects.get(id_cliente=id_cliente)
			return JsonResponse({'id_cliente': cliente.id_cliente, 'nombre_cliente': cliente.nombre_cliente})
		except Cliente.DoesNotExist:
			return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
	
	return JsonResponse({'error': 'Código del Cliente no proporcionado'}, status=400)

#-- Búsqueda en Agenda para la ventana Modal de Informes.
def buscar_cliente(request):
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
	)
	
	return JsonResponse(list(resultados), safe=False)
