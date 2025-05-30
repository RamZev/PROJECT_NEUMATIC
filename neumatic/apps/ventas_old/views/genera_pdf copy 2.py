from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from ..models.factura_models import Factura, DetalleFactura, SerialFactura
from apps.maestros.models.empresa_models import Empresa
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.base_models import Provincia, Localidad, TipoIva


class GeneraPDFView(View):
    def get(self, request, model_name, pk):
        if model_name == 'factura':
            return self.generar_pdf_factura(pk)
        return self.generar_pdf_default(model_name, pk)
    
    def generar_pdf_factura(self, pk):
        factura = get_object_or_404(Factura, pk=pk)
        detalles = DetalleFactura.objects.filter(id_factura=factura)
        empresa = Empresa.objects.first()  # Obtenemos la primera empresa
        
        if not empresa:
            return HttpResponse("No se encontraron datos de empresa configurados", status=400)
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        margin = 15*mm
        y_position = height - margin
        
        # 1. Encabezado dividido
        box_width = (width - 2*margin)/2
        box_height = 60*mm
        
        # Dibujar recuadro principal
        p.rect(margin, y_position - box_height, width - 2*margin, box_height)
        # Línea vertical divisoria
        p.line(width/2, y_position, width/2, y_position - box_height)
        
        # 1.1 Sección izquierda (Datos del cliente)
        x_left = margin + 5*mm
        label_width = 40*mm  # Ancho fijo para las etiquetas
        
        # Función auxiliar para dibujar líneas alineadas
        def draw_label_value(y, label, value):
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x_left, y, label)
            p.setFont("Helvetica", 9)
            p.drawString(x_left + label_width, y, value)
        
        draw_label_value(y_position - 15, "Razon Social*:", empresa.nombre_fiscal or '')
        draw_label_value(y_position - 27, "Sucursal:", factura.id_sucursal.nombre_sucursal if factura.id_sucursal else '')
        draw_label_value(y_position - 39, "Domicilio:", factura.id_sucursal.domicilio_sucursal or '')
        draw_label_value(y_position - 51, "e-Mail:", factura.id_sucursal.email_sucursal or '')
        draw_label_value(y_position - 63, "Telefono:", factura.id_sucursal.telefono_sucursal or '')
        draw_label_value(y_position - 75, "Condicion de Vta.:", "CTA.CTE." if factura.condicion_comprobante == 2 else "CONTADO")
        
        # 1.2 Sección derecha (Datos de factura)
        x_right = width/2 + 5*mm
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_right, y_position - 15, "FACTURA ELECTRÓNICA")
        
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x_right, y_position - 30, f"Comprobante Nro: {factura.compro}-{factura.letra_comprobante}-{str(factura.numero_comprobante).zfill(8)}")
        
        p.drawString(x_right, y_position - 42, f"Fecha: {factura.fecha_comprobante.strftime('%d/%m/%Y') if factura.fecha_comprobante else ''}")
        
        p.setFont("Helvetica", 9)
        p.drawString(x_right, y_position - 54, "I.V.A.: RESP.INSCRIPTOS")
        p.drawString(x_right, y_position - 66, f"CUIT: {factura.cuit or ''}")
        p.drawString(x_right, y_position - 78, "Ingresos Brutos: 921-746351-8")
        p.drawString(x_right, y_position - 90, "Inicio de Actividades: 15/10/1998")
        
        y_position -= box_height + 15*mm
        
        # 2. Tabla de detalles de factura
        encabezados = ["Código", "Descripción", "Cantidad", "P. Unitario", "Desc.%", "Total"]
        detalle_data = [encabezados]
        
        for detalle in detalles:
            detalle_data.append([
                detalle.id_producto.codigo_producto if detalle.id_producto else "",
                detalle.producto_venta or "",
                f"{detalle.cantidad:,.2f}".replace(",", ".") if detalle.cantidad else "0.00",
                f"${detalle.precio:,.2f}".replace(",", ".") if detalle.precio else "$0.00",
                f"{detalle.descuento:.2f}%" if detalle.descuento else "0%",
                f"${detalle.total:,.2f}".replace(",", ".") if detalle.total else "$0.00"
            ])
        
        # Configuración de la tabla
        col_widths = [20*mm, 60*mm, 20*mm, 25*mm, 20*mm, 25*mm]
        tabla = Table(detalle_data, colWidths=col_widths, repeatRows=1)
        
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#D9E1F2")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#7F7F7F")),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alinear descripción a la izquierda
        ]))
        
        # Dibujar tabla
        tabla.wrapOn(p, width - 2*margin, height)
        tabla.drawOn(p, margin, y_position - (8 * len(detalle_data)*mm))
        y_position -= (8 * len(detalle_data)*mm) + 20*mm
        
        # 3. Totales
        p.setFont("Helvetica-Bold", 10)
        p.drawString(width - 150, y_position, "Subtotal:")
        p.drawString(width - 50, y_position, f"${factura.gravado + factura.exento:,.2f}".replace(",", "."))
        y_position -= 12
        
        p.drawString(width - 150, y_position, "IVA 21%:")
        p.drawString(width - 50, y_position, f"${factura.iva:,.2f}".replace(",", "."))
        y_position -= 12
        
        p.drawString(width - 150, y_position, "Percep. IIBB:")
        p.drawString(width - 50, y_position, f"${factura.percep_ib:,.2f}".replace(",", "."))
        y_position -= 15
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(width - 150, y_position, "TOTAL:")
        p.drawString(width - 50, y_position, f"${factura.total:,.2f}".replace(",", "."))
        y_position -= 25
        
        # 4. Datos CAE si existe
        if factura.cae:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(margin, y_position, f"CAE N°: {factura.cae}")
            y_position -= 12
            
            p.drawString(margin, y_position, f"Vto. CAE: {factura.cae_vto.strftime('%d/%m/%Y') if factura.cae_vto else ''}")
            y_position -= 20
        
        # 5. Pie de página
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width/2, y_position, "Recibi Conforme")
        y_position -= 20
        
        p.drawCentredString(width/2, y_position, "Comprobante Autorizado")
        y_position -= 15
        
        p.drawCentredString(width/2, y_position, "ORIGINAL / DUPLICADO")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="factura_{factura.numero_comprobante}.pdf"'
        return response
    
    def generar_pdf_default(self, model_name, pk):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Documento {model_name} - ID {pk}")
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{model_name}_{pk}.pdf"'
        return response