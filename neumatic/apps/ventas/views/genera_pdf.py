# neumatic\apps\ventas\views\genera_pdf.py
from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from pathlib import Path
from os import path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm

from ..models.factura_models import Factura, DetalleFactura, SerialFactura
from apps.maestros.models.empresa_models import Empresa
from apps.maestros.models.cliente_models import Cliente
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
        # Obtener datos principales
        factura = get_object_or_404(Factura, pk=pk)
        detalles = DetalleFactura.objects.filter(id_factura=factura)
        empresa = Empresa.objects.first()
        cliente = factura.id_cliente  # No necesitas consulta adicional
        vendedor = factura.id_vendedor

        print("cliente", cliente)
        print("Nombre:", cliente.nombre_cliente)
        print("CUIT:", cliente.cuit)
        print("Teléfono:", cliente.telefono_cliente)
        
        print("vendedor:", vendedor)
        
        if not empresa:
            return HttpResponse("No se encontraron datos de empresa configurados", status=400)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        margin = 15*mm
        y_position = height - margin
        

        # Estilo para párrafos
        style_normal = ParagraphStyle(
            'normal',
            fontName='Helvetica',
            fontSize=9,
            leading=10,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=0
        )

        style_bold = ParagraphStyle(
            'bold',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=10,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=0
        )

        # 1. Encabezado dividido
        box_width = (width - 2*margin)/2
        box_height = 55*mm  # Aumentamos para acomodar múltiples líneas
        
        # Dibujar recuadro principal
        p.rect(margin, y_position - box_height, width - 2*margin, box_height)
        # Línea vertical divisoria
        p.line(width/2, y_position, width/2, y_position - box_height)

        # 1.1 Sección izquierda (Datos del cliente)
        x_left = margin + 5*mm
        label_width = 40*mm
        current_y = y_position - 15

        # Función modificada draw_field que usa current_y
        def draw_field(label, value, max_width=box_width - 10*mm):  # Reducimos margen interno de 20 a 10mm
            nonlocal current_y
            
            # Dibujar etiqueta
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x_left, current_y, label)
            
            # Aumentamos el espacio disponible para el texto
            available_width = max_width - label_width + 3*mm
            available_height = 60*mm  # Más altura para múltiples líneas
            
            # Procesar valor con Paragraph
            para = Paragraph(value or '', style_normal)
            para.wrapOn(p, available_width, available_height)
            
            # Dibujar contenido más hacia la derecha
            text_x = x_left + label_width - 3*mm 
            para.drawOn(p, text_x, current_y - (para.height - 9))
            
            # Ajustar posición Y para siguiente campo
            current_y -= max(12, para.height + 2)
        
        ######
        # 1. Configuración inicial del logo
        logo_path = path.join(settings.BASE_DIR, 'static', 'img', 'logo_01.png')
        logo_width = 40*mm
        logo_height = 16*mm

        # 2. Posicionamiento inicial (sin recuadro principal)
        y_position = height - margin
        y_position -= 10*mm  # Margen superior adicional

        # 3. Posicionar el logo
        try:
            p.drawImage(logo_path, 
                        x=margin + 5*mm,
                        y=y_position - 10*mm,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True)
        except:
            print("Logo no cargado - espacio reservado se mantiene")

        # 4. Posicionar los campos de texto (debajo del logo)
        # current_y = y_position - logo_height - 20*mm
        current_y = y_position - logo_height - 1*mm

        # 5. Dibujar línea divisoria vertical (sin recuadro)
        #div_line_top = y_position - 10*mm
        #div_line_bottom = current_y - (6 * 12*mm)  # Aprox altura de los campos
        #p.line(width/2, div_line_top, width/2, div_line_bottom)
        ######
        
        # Dibujar campos con el nuevo posicionamiento
        draw_field("Razon Social:", empresa.nombre_fiscal or '')
        draw_field("Sucursal:", factura.id_sucursal.nombre_sucursal if factura.id_sucursal else '')
        draw_field("Domicilio:", factura.id_sucursal.domicilio_sucursal or '')
        draw_field("e-Mail:", factura.id_sucursal.email_sucursal or '')
        draw_field("Telefono:", factura.id_sucursal.telefono_sucursal or '')
        draw_field("Condicion de Vta.:", "CTA.CTE." if factura.condicion_comprobante == 2 else "CONTADO")

        # 1.2 Sección derecha (Datos de factura y empresa)
        x_right = width/2 + 5*mm
        current_y = y_position - 15

        # Título
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_right, current_y, "FACTURA ELECTRÓNICA")
        current_y -= 15

        # Datos de factura
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x_right, current_y, f"Comprobante Nro: {factura.compro}-{factura.letra_comprobante}-{str(factura.numero_comprobante).zfill(8)}")
        current_y -= 12

        p.drawString(x_right, current_y, f"Fecha: {factura.fecha_comprobante.strftime('%d/%m/%Y') if factura.fecha_comprobante else ''}")
        current_y -= 12

        # Datos de empresa (dinámicos)
        p.setFont("Helvetica", 9)
        p.drawString(x_right, current_y, f"I.V.A.: {empresa.id_iva.nombre_iva if empresa.id_iva else 'RESP.INSCRIPTOS'}")
        current_y -= 12

        p.drawString(x_right, current_y, f"CUIT: {empresa.cuit}")
        current_y -= 12

        p.drawString(x_right, current_y, f"Ingresos Brutos: {empresa.ingresos_bruto}")
        current_y -= 12

        p.drawString(x_right, current_y, f"Inicio de Actividades: {empresa.inicio_actividad.strftime('%d/%m/%Y') if empresa.inicio_actividad else ''}")
        current_y -= 15

        y_position -= box_height + 15*mm

        # 2. Tabla de detalles de factura
        encabezados = ["Código", "Descripción", "Cantidad", "P. Unitario", "Desc.%", "Total"]
        detalle_data = [encabezados]
        
        for detalle in detalles:
            detalle_data.append([
                detalle.id_producto.codigo_producto[:10] if detalle.id_producto else "",
                detalle.producto_venta or "",
                f"{detalle.cantidad:,.2f}".replace(",", ".") if detalle.cantidad else "0.00",
                f"${detalle.precio:,.2f}".replace(",", ".") if detalle.precio else "$0.00",
                f"{detalle.descuento:.2f}%" if detalle.descuento else "0%",
                f"${detalle.total:,.2f}".replace(",", ".") if detalle.total else "$0.00"
            ])
        
        # Configuración de la tabla
        col_widths = [25*mm, 55*mm, 20*mm, 25*mm, 20*mm, 25*mm]
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
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
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