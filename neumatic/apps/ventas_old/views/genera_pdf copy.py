from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from ..models.factura_models import Factura, DetalleFactura

class GeneraPDFView(View):
    def get(self, request, model_name, pk):
        try:
            if model_name == 'factura':
                return self.generar_pdf_factura(pk)
            return self.generar_pdf_default(model_name, pk)
        except Exception as e:
            return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
    
    def generar_pdf_factura(self, pk):
        # Obtener datos
        factura = get_object_or_404(Factura, pk=pk)
        detalles = DetalleFactura.objects.filter(id_factura=factura)
        
        # Configuración del documento
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        margin = 50
        y_position = height - margin
        
        # 1. Encabezado principal
        p.setFont("Helvetica-Bold", 16)
        p.drawString(margin, y_position, f"FACTURA {factura.compro}-{factura.letra_comprobante}-{factura.numero_comprobante}")
        y_position -= 30
        
        # 2. Datos del cliente
        p.setFont("Helvetica", 10)
        p.drawString(margin, y_position, f"Cliente: {factura.nombre_factura or 'No especificado'}")
        y_position -= 20
        p.drawString(margin, y_position, f"CUIT: {factura.cuit or 'No especificado'}")
        y_position -= 20
        p.drawString(margin, y_position, f"Fecha: {factura.fecha_comprobante.strftime('%d/%m/%Y') if factura.fecha_comprobante else 'No especificada'}")
        y_position -= 40
        
        # 3. Tabla de detalles
        encabezados = ["Producto", "Cantidad", "P. Unitario", "Desc.%", "Total"]
        detalle_data = [encabezados]
        
        for detalle in detalles:
            detalle_data.append([
                detalle.producto_venta or "-",
                f"{detalle.cantidad:.2f}" if detalle.cantidad else "0.00",
                f"${detalle.precio:.2f}" if detalle.precio else "$0.00",
                f"{detalle.descuento:.2f}%" if detalle.descuento else "0%",
                f"${detalle.total:.2f}" if detalle.total else "$0.00"
            ])
        
        # Configuración de la tabla
        tabla = Table(detalle_data, colWidths=[220, 60, 80, 60, 80])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#D9E1F2")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#7F7F7F")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Dibujar tabla
        tabla.wrapOn(p, width - 2*margin, height)
        tabla.drawOn(p, margin, y_position - (20 * len(detalle_data)))
        
        # 4. Totales
        y_position -= (20 * len(detalle_data)) + 40
        p.setFont("Helvetica-Bold", 12)
        
        # Subtotal
        p.drawString(width - 250, y_position, "Subtotal:")
        p.drawString(width - 150, y_position, f"${factura.gravado + factura.exento:.2f}")
        y_position -= 20
        
        # IVA
        if factura.iva:
            p.drawString(width - 250, y_position, "IVA:")
            p.drawString(width - 150, y_position, f"${factura.iva:.2f}")
            y_position -= 20
        
        # Total General
        p.setFont("Helvetica-Bold", 14)
        p.drawString(width - 250, y_position, "TOTAL GENERAL:")
        p.drawString(width - 150, y_position, f"${factura.total:.2f}")
        
        # Finalizar documento
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