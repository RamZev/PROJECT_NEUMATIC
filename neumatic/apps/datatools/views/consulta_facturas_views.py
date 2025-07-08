# neumatic\apps\datatools\views\consulta_facturas_views.py
from django.views.generic import TemplateView
from django.db.models import Q, Sum
from django.shortcuts import render
from django.core.paginator import Paginator

from apps.maestros.models.cliente_models import Cliente
from apps.ventas.models.factura_models import Factura, DetalleFactura
from apps.maestros.models.producto_models import Producto, ProductoStock
from apps.maestros.models.base_models import ProductoDeposito


class ConsultaFacturasClienteView(TemplateView):
    template_name = 'datatools/consulta_factura_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buscar_por = self.request.GET.get('buscar_por', '').strip()
        facturas = []
        detalles_factura = {}
        cliente = None
        error = None

        if buscar_por:
            try:
                # Buscar cliente por ID, CUIT o nombre
                if buscar_por.isdigit():
                    # Si es numérico, buscar por ID o CUIT
                    if len(buscar_por) == 11:  # Asumiendo que CUIT tiene 11 dígitos
                        cliente = Cliente.objects.filter(
                            Q(cuit=int(buscar_por))
                        ).first()
                    else:
                        cliente = Cliente.objects.filter(
                            Q(id_cliente=int(buscar_por))
                        ).first()
                        
                    if not cliente and len(buscar_por) < 11:
                        # Si no se encontró por ID, intentar por CUIT aunque no tenga 11 dígitos
                        cliente = Cliente.objects.filter(
                            Q(cuit=int(buscar_por))
                        ).first()
                else:
                    # Búsqueda por nombre (no numérico)
                    cliente = Cliente.objects.filter(
                        Q(nombre_cliente__icontains=buscar_por)
                    ).first()
                
                if cliente:
                    facturas = Factura.objects.filter(
                        id_cliente=cliente,
                        id_comprobante_venta__libro_iva=True
                    ).select_related(
                        'id_comprobante_venta',
                        'id_cliente'
                    ).order_by('-fecha_comprobante')

                    # Paginación
                    paginator = Paginator(facturas, 10)  # 10 facturas por página
                    page_number = self.request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    
                    # Pre-cargar detalles para las facturas encontradas
                    if facturas:
                        facturas_ids = [f.id_factura for f in facturas]
                        detalles = DetalleFactura.objects.filter(
                            id_factura__in=facturas_ids
                        ).select_related('id_producto')
                        
                        # Organizar detalles por factura
                        detalles_factura = {
                            factura.id_factura: [
                                d for d in detalles 
                                if d.id_factura_id == factura.id_factura
                            ] 
                            for factura in facturas
                        }
                else:
                    error = "No se encontró ningún cliente con ese criterio de búsqueda"
            
            except ValueError as ve:
                error = f"Error en el formato de búsqueda: {str(ve)}"
            except Exception as e:
                error = f"Error inesperado al realizar la búsqueda: {str(e)}"
        
        context.update({
            'cliente': cliente,
            'facturas': page_obj,  # Ahora contiene solo las facturas de la página actual
            'page_obj': page_obj,
            'detalles_factura': detalles_factura,
            'buscar_por': buscar_por,
            'error': error,
        })
        return context
    
    def get(self, request, *args, **kwargs):
        # Manejo personalizado para mostrar errores
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return render(request, self.template_name, {
                'error': f"Error al procesar la solicitud: {str(e)}"
            })



class ConsultaProductosView(TemplateView):
    template_name = 'datatools/consulta_productos_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Parámetros de búsqueda
        medida = self.request.GET.get('medida', '').strip()
        nombre = self.request.GET.get('nombre', '').strip()
        cai = self.request.GET.get('cai', '').strip()
        filtro_marca = self.request.GET.get('filtro_marca', 'primeras')
        
        productos = []
        stock_por_producto = {}
        error = None

        try:
            # Consulta base con select_related para optimización
            productos = Producto.objects.select_related(
                'id_marca', 'id_cai', 'id_familia', 'id_alicuota_iva'
            ).all()
            
            # Aplicar filtros
            if medida:
                productos = productos.filter(medida__icontains=medida)
            if nombre:
                productos = productos.filter(nombre_producto__icontains=nombre)
            if cai:
                productos = productos.filter(id_cai__descripcion_cai__icontains=cai)
                
            # Filtros especiales
            if filtro_marca == "primeras":
                productos = productos.filter(id_marca__principal=True)
            elif filtro_marca == "otras":
                productos = productos.filter(id_marca__principal=False)
            elif filtro_marca == "stock":
                productos = productos.annotate(
                    total_stock=Sum('productostock__stock')
                ).filter(total_stock__gt=0)
            
            # Paginación
            paginator = Paginator(productos, 15)  # 15 productos por página
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            # Precargar stock por depósito para los productos de la página
            if page_obj:
                depositos = ProductoDeposito.objects.all()
                productos_ids = [p.id_producto for p in page_obj]
                
                # Obtener todo el stock de estos productos en una sola consulta
                stock_data = ProductoStock.objects.filter(
                    id_producto__in=productos_ids
                ).select_related('id_deposito')
                
                # Organizar el stock por producto
                for producto in page_obj:
                    stock_por_producto[producto.id_producto] = {
                        'total': 0,
                        'por_deposito': []
                    }
                    
                    # Filtrar y sumar el stock para este producto
                    for deposito in depositos:
                        stock_items = [s for s in stock_data 
                                     if s.id_producto_id == producto.id_producto 
                                     and s.id_deposito_id == deposito.id_producto_deposito]
                        
                        stock = sum(s.stock for s in stock_items) if stock_items else 0
                        
                        if stock > 0:  # Solo mostrar depósitos con stock
                            stock_por_producto[producto.id_producto]['por_deposito'].append({
                                'deposito': deposito.nombre_producto_deposito,
                                'stock': stock
                            })
                            stock_por_producto[producto.id_producto]['total'] += stock
        
        except Exception as e:
            error = f"Error al realizar la búsqueda: {str(e)}"
        
        context.update({
            'productos': page_obj,
            'page_obj': page_obj,
            'stock_por_producto': stock_por_producto,
            'medida': medida,
            'nombre': nombre,
            'cai': cai,
            'filtro_marca': filtro_marca,
            'error': error,
        })
        return context

