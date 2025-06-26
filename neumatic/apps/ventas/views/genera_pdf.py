# neumatic\apps\ventas\views\genera_pdf.py
from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import date

from pathlib import Path
from os import path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm, cm

from ..models.factura_models import Factura, DetalleFactura, SerialFactura
from ..models.recibo_models import DetalleRecibo, RetencionRecibo, DepositoRecibo, TarjetaRecibo, ChequeRecibo
from apps.maestros.models.empresa_models import Empresa
from apps.maestros.models.cliente_models import Cliente
from apps.maestros.models.sucursal_models import Sucursal
from apps.maestros.models.producto_models import Producto
from apps.maestros.models.vendedor_models import Vendedor
from apps.maestros.models.base_models import Provincia, Localidad, TipoIva
from utils.utils import formato_argentino

class GeneraPDFView(View):
	# def get(self, request, model_name, pk):
	# 	if model_name == 'factura':
	# 		return self.generar_pdf_factura(pk)
	# 	return self.generar_pdf_default(model_name, pk)
	def get(self, request, model_string, pk):
		method_name = f"generar_pdf_{model_string.lower()}"
		if hasattr(self, method_name):
			method = getattr(self, method_name)
			return method(pk)
		return self.generar_pdf_default(model_string, pk)
	
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
		p = canvas.Canvas(buffer, pagesize=portrait(A4))
		width, height = portrait(A4)
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
		# p.setLineWidth(0.5)
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

		y_position -= box_height - 5*mm
		
		############################
		# 1.5 Sección de datos del cliente
		# current_y = y_position - 15*mm  # Ajustar posición Y después del encabezado

		# Estilo para etiquetas
		style_label = ParagraphStyle(
			'label',
			fontName='Helvetica-Bold',
			fontSize=9,
			leading=10,
			alignment=TA_LEFT
		)

		# Dibujar recuadro para datos del cliente
		p.rect(margin, current_y - 30*mm, width - 2*margin, 30*mm)

		# Datos del cliente - primera línea
		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 5*mm, current_y - 15*mm, "Cuenta:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 25*mm, current_y - 15*mm, str(cliente.id_cliente))

		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 60*mm, current_y - 15*mm, "Ap. y Nombre / Razón Social:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 120*mm, current_y - 15*mm, cliente.nombre_cliente[:40])  # Limitado a 40 caracteres

		# Datos del cliente - segunda línea
		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 5*mm, current_y - 20*mm, "I.V.A.:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 25*mm, current_y - 20*mm, cliente.id_tipo_iva.nombre_iva if cliente.id_tipo_iva else "")

		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 60*mm, current_y - 20*mm, "Domicilio:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 120*mm, current_y - 20*mm, cliente.domicilio_cliente[:40])  # Limitado a 40 caracteres

		# Datos del cliente - tercera línea
		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 5*mm, current_y - 25*mm, "C.U.I.T:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 25*mm, current_y - 25*mm, str(cliente.cuit))

		p.setFont("Helvetica-Bold", 9)
		p.drawString(margin + 60*mm, current_y - 25*mm, "Localidad:")
		p.setFont("Helvetica", 9)
		p.drawString(margin + 120*mm, current_y - 25*mm, cliente.id_localidad.nombre_localidad if cliente.id_localidad else "")

		# Ajustar posición Y para la tabla de detalles
		y_position = current_y - 30*mm
		############################

		# 2. Tabla de detalles de factura
		encabezados = ["Medida", "Descripción", "Cantidad", "Precio", "Desc.%", "Total"]
		detalle_data = [encabezados]
		
		for detalle in detalles:
			detalle_data.append([
				detalle.id_producto.medida[:10] if detalle.id_producto else "",
				detalle.producto_venta or "",
				f"{detalle.cantidad:,.2f}".replace(",", ".") if detalle.cantidad else "0.00",
				f"${detalle.precio:,.2f}".replace(",", ".") if detalle.precio else "$0.00",
				f"{detalle.descuento:.2f}%" if detalle.descuento else "0%",
				f"${detalle.total:,.2f}".replace(",", ".") if detalle.total else "$0.00"
			])
		
		# Configuración de la tabla
		col_widths = [25*mm, 70*mm, 20*mm, 25*mm, 20*mm, 25*mm]
		tabla = Table(detalle_data, colWidths=col_widths, repeatRows=1)
		
		tabla.setStyle(TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),  # Gris claro para el encabezado
			('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('FONTSIZE', (0, 0), (-1, 0), 8),
			('BOTTOMPADDING', (0, 0), (-1, 0), 6),
			('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Blanco para el cuerpo
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
		'''
		p.setFont("Helvetica-Bold", 10)
		p.drawString(width - 250, y_position, "Subtotal:")
		p.drawString(width - 150, y_position, f"${factura.gravado + factura.exento:,.2f}".replace(",", "."))
		y_position -= 12
		
		p.drawString(width - 250, y_position, "IVA 21%:")
		p.drawString(width - 150, y_position, f"${factura.iva:,.2f}".replace(",", "."))
		y_position -= 12
		
		p.drawString(width - 250, y_position, "Percep. IIBB:")
		p.drawString(width - 150, y_position, f"${factura.percep_ib:,.2f}".replace(",", "."))
		y_position -= 15
		
		p.setFont("Helvetica-Bold", 12)
		p.drawString(width - 250, y_position, "TOTAL:")
		p.drawString(width - 150, y_position, f"${factura.total:,.2f}".replace(",", "."))
		y_position -= 25
		'''
		
		p.setFont("Helvetica-Bold", 10)
		p.drawString(width - 250, y_position, "Subtotal:")
		p.drawRightString(width - 50, y_position, f"${factura.gravado + factura.exento:,.2f}".replace(",", "."))
		y_position -= 12

		p.drawString(width - 250, y_position, "IVA 21%:")
		p.drawRightString(width - 50, y_position, f"${factura.iva:,.2f}".replace(",", "."))
		y_position -= 12

		p.drawString(width - 250, y_position, "Percep. IIBB:")
		p.drawRightString(width - 50, y_position, f"${factura.percep_ib:,.2f}".replace(",", "."))
		y_position -= 15

		p.setFont("Helvetica-Bold", 12)
		p.drawString(width - 250, y_position, "TOTAL:")
		p.drawRightString(width - 50, y_position, f"${factura.total:,.2f}".replace(",", "."))
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
	
	def generar_pdf_recibo(self, pk):
		# Obtener datos principales
		recibo = get_object_or_404(Factura, pk=pk)
		detalle_recibo = DetalleRecibo.objects.filter(id_factura=recibo)
		retenciones = RetencionRecibo.objects.filter(id_factura=recibo)
		depositos = DepositoRecibo.objects.filter(id_factura=recibo)
		tarjetas = TarjetaRecibo.objects.filter(id_factura=recibo)
		cheques = ChequeRecibo.objects.filter(id_factura=recibo)
		
		empresa = Empresa.objects.first()
		cliente = recibo.id_cliente  # No necesitas consulta adicional
		
		#------------------------------------------------
		print(f"--------------------------------")
		print("Datos de la Empresa:")
		print(f"{empresa.nombre_fiscal = }")
		print(f"{empresa.domicilio_empresa = }")
		print(f"{empresa.codigo_postal = }")
		print(f"{empresa.id_localidad = }")
		print(f"{empresa.id_iva = }")
		print(f"{empresa.cuit = }")
		print(f"--------------------------------")
		
		print("Datos del Cliente:")
		print(f"{cliente.nombre_cliente = }")
		print(f"{cliente.id_cliente = }")
		print(f"{cliente.pk = }")
		print(f"{cliente.domicilio_cliente = }")
		print(f"{cliente.codigo_postal = }")
		print(f"{cliente.id_tipo_iva = }")
		print(f"{cliente.cuit = }")
		print(f"{cliente.telefono_cliente = }")
		
		print(f"--------------------------------")
		print("Detalle", list(detalle_recibo))
		print("Retenciones", list(retenciones))
		print("Depósitos", list(depositos))
		print("Tarjetas", list(tarjetas))
		print("Cheques", list(cheques))
		print("Efectivo", recibo.efectivo_recibo)
		#------------------------------------------------
		if not empresa:
			return HttpResponse("No se encontraron datos de empresa configurados", status=400)
		
		buffer = BytesIO()
		c = canvas.Canvas(buffer, pagesize=portrait(A4))
		width, height = portrait(A4)
		margin = 10*mm
		
		y_position = height - margin
		
		
		#-- Estilo para párrafos.
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
		available_width = (width - 2*margin)/2
		header_top_height = 35*mm  # Aumentamos para acomodar múltiples líneas
		
		#-- Dibujar recuadro header top left.
		c.setLineWidth(0.5)
		y_header_top = y_position - header_top_height
		c.rect(margin, y_header_top, width - 2*margin, header_top_height)
		
		#-- Línea vertical divisoria.
		c.line(width/2, y_position, width/2, y_position - header_top_height)
		
		#-- Configuración inicial del logo.
		logo_path = path.join(settings.BASE_DIR, 'static', 'img', 'logo_01.png')
		logo_width = 30*mm
		logo_height = 12*mm
		
		#-- Posicionamiento inicial.
		y_position = height - margin
		y_position -= 10*mm  # Margen superior adicional

		#-- Posicionar el logo.
		try:
			c.drawImage(logo_path, 
						x=margin + 5*mm,
						y=y_position -5*mm,
						width=logo_width,
						height=logo_height,
						preserveAspectRatio=True)
		except:
			print("Logo no cargado - espacio reservado se mantiene")
		
		#-- Mostrar los datos de la empresa en el header-top-left.
		c.setFont("Helvetica", 8)
		x_text_left = margin + 5*mm
		y_text_left = y_position - logo_height
		c.drawString(x_text_left, y_text_left, empresa.nombre_fiscal)
		
		y_text_left -= 3*mm
		c.drawString(x_text_left, y_text_left, empresa.domicilio_empresa)
		
		y_text_left -= 3*mm
		c.drawString(x_text_left, y_text_left, f"C.P.: ({empresa.codigo_postal})  {empresa.id_localidad} - {empresa.id_provincia}")
		
		y_text_left -= 3*mm
		c.drawString(x_text_left, y_text_left, f"I.V.A.: {empresa.id_iva}    C.U.I.T.: {empresa.cuit}")
		
		#-- Mostrar datos del recibo en el header-top-right.
		y_text_right = y_position
		x_text_right = width/2 + 5*mm
		
		c.setFont("Helvetica-Bold", 10)
		c.drawString(x_text_right, y_text_right, "RECIBO OFICIAL")
		
		y_text_right -= 4*mm
		c.drawString(x_text_right, y_text_right, f"Nº: {recibo.letra_comprobante} {recibo.numero_comprobante_formateado}")
		
		c.setFont("Helvetica", 8)
		y_text_right -= 4*mm
		c.drawString(x_text_right, y_text_right, f"Fecha: {recibo.fecha_comprobante}")
		
		
		#-- Dibujar recuadro header bottom.
		header_bottom_heigth = 15*mm
		y_header_bottom = y_header_top - header_bottom_heigth - 1*mm
		c.rect(margin, y_header_bottom, width - 2*margin, header_bottom_heigth)
		
		y_text = y_header_bottom + header_bottom_heigth - 4*mm
		c.drawString(x_text_left, y_text, "Se ha recibido de:")
		
		c.drawString(x_text_right, y_text, "La suma de:")
		
		y_text -= 3*mm
		c.drawString(x_text_left, y_text, f"{cliente.nombre_cliente}  [{cliente.id_cliente}]")
		
		c.setFont("Helvetica-Bold", 8)
		c.drawString(x_text_right, y_text, f"${formato_argentino(recibo.total)}")
		c.setFont("Helvetica", 8)
		
		y_text -= 3*mm
		c.drawString(x_text_left, y_text, f"{cliente.domicilio_cliente}    C.P.: {cliente.codigo_postal}")
		
		y_text -= 3*mm
		c.drawString(x_text_left, y_text, f"I.V.A.: {cliente.id_tipo_iva}    C.U.I.T.: {cliente.cuit}")
		
		
		#-- Mostrar detalle del recibo.
		
		y_detail = y_header_bottom - 4*mm
		c.drawString(x_text_left, y_detail, "Detalle del Recibo")
		
		
		#-- Medios de Pago.
		table_cols = ["Banco/Tarjeta", "Número", "Fecha", "Cuotas", "Importe"]
		cols_width = [30*mm, 20*mm, 20*mm, 20*mm, 20*mm]
		
		table_data = [table_cols]
		
		if detalle_recibo:
			y_detail -= 3*mm
			c.drawString(x_text_left, y_detail, "Detalle del Recibo")
		
		if retenciones:
			y_detail -= 3*mm
			c.drawString(x_text_left, y_detail, "Detalle Retenciones")
		
		if depositos:
			for deposito in depositos:
				row = [
					deposito.id_banco,
					"",
					deposito.fecha_deposito.strftime("%d/%m/%Y"),
					"",
					f"${formato_argentino(deposito.importe_deposito)}"
				]
				table_data.append(row)
		
		if tarjetas:
			for tarjeta in tarjetas:
				row = [
					tarjeta.id_tarjeta,
					tarjeta.cupon,
					date.today().strftime("%d/%m/%Y"),
					tarjeta.cuotas or "",
					f"${formato_argentino(tarjeta.importe_tarjeta)}"
				]
				table_data.append(row)
		
		if cheques:
			y_detail -= 3*mm
			c.drawString(x_text_left, y_detail, "Detalle Cheques")
		
		# table = Table(table_data, colWidths=cols_width, repeatRows=repeat_rows)
		table = Table(table_data, colWidths=cols_width)
		
		# Aplica estilo a la tabla
		table.setStyle(TableStyle([
			# ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),  # Encabezado gris claro
			# ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
			# ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('FONTSIZE', (0, 0), (-1, -1), 8),
			('TOPPADDING', (0,0), (-1,-1), 0),
			('BOTTOMPADDING', (0, 0), (-1, -1), 0),
			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
			('ALIGN', (1, 0), (1, -1), 'LEFT'),
			# ('LINEABOVE', (0,0), (-1,0), 0.5, colors.black),
			('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
			('ALIGN', (1, 0), (1, -1), 'RIGHT'),
			('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
		]))
		
		# Calcula la posición Y para la tabla (ajusta según tu layout)
		y_table = y_detail - 10*mm
		
		# Dibuja la tabla en el canvas
		table.wrapOn(c, width - 2*margin, 200*mm)
		table.drawOn(c, margin, y_table - (len(table_data) * 8))  # Ajusta el 8 si la tabla se ve muy arriba/abajo
		
		'''
# 		# 1.1 Sección izquierda (Datos del cliente)
# 		x_left = margin + 5*mm
# 		label_width = 40*mm
# 		current_y = y_position - 15
# 		
# 		# Función modificada draw_field que usa current_y
# 		def draw_field(label, value, max_width=available_width - 10*mm):  # Reducimos margen interno de 20 a 10mm
# 			nonlocal current_y
# 			
# 			# Dibujar etiqueta
# 			c.setFont("Helvetica-Bold", 10)
# 			c.drawString(x_left, current_y, label)
# 			
# 			# Aumentamos el espacio disponible para el texto
# 			available_width = max_width - label_width + 3*mm
# 			available_height = 60*mm  # Más altura para múltiples líneas
# 			
# 			# Procesar valor con Paragraph
# 			para = Paragraph(value or '', style_normal)
# 			para.wrapOn(c, available_width, available_height)
# 			
# 			# Dibujar contenido más hacia la derecha
# 			text_x = x_left + label_width - 3*mm 
# 			para.drawOn(c, text_x, current_y - (para.height - 9))
# 			
# 			# Ajustar posición Y para siguiente campo
# 			current_y -= max(12, para.height + 2)
# 		
# 		######
# 		# 1. Configuración inicial del logo
# 		logo_path = path.join(settings.BASE_DIR, 'static', 'img', 'logo_01.png')
# 		logo_width = 40*mm
# 		logo_height = 16*mm
# 		
# 		# 2. Posicionamiento inicial (sin recuadro principal)
# 		y_position = height - margin
# 		y_position -= 10*mm  # Margen superior adicional
# 
# 		# 3. Posicionar el logo
# 		try:
# 			c.drawImage(logo_path, 
# 						x=margin + 5*mm,
# 						y=y_position - 10*mm,
# 						width=logo_width,
# 						height=logo_height,
# 						preserveAspectRatio=True)
# 		except:
# 			print("Logo no cargado - espacio reservado se mantiene")
# 
# 		# 4. Posicionar los campos de texto (debajo del logo)
# 		# current_y = y_position - logo_height - 20*mm
# 		current_y = y_position - logo_height - 1*mm
# 
# 		# Dibujar campos con el nuevo posicionamiento
# 		draw_field("Razon Social:", empresa.nombre_fiscal or '')
# 		draw_field("Sucursal:", factura.id_sucursal.nombre_sucursal if factura.id_sucursal else '')
# 		draw_field("Domicilio:", factura.id_sucursal.domicilio_sucursal or '')
# 		draw_field("e-Mail:", factura.id_sucursal.email_sucursal or '')
# 		draw_field("Telefono:", factura.id_sucursal.telefono_sucursal or '')
# 		draw_field("Condicion de Vta.:", "CTA.CTE." if factura.condicion_comprobante == 2 else "CONTADO")
# 
# 		# 1.2 Sección derecha (Datos de factura y empresa)
# 		x_right = width/2 + 5*mm
# 		current_y = y_position - 15
# 
# 		# Título
# 		c.setFont("Helvetica-Bold", 12)
# 		c.drawString(x_right, current_y, "FACTURA ELECTRÓNICA")
# 		current_y -= 15
# 
# 		# Datos de factura
# 		c.setFont("Helvetica-Bold", 10)
# 		c.drawString(x_right, current_y, f"Comprobante Nro: {factura.compro}-{factura.letra_comprobante}-{str(factura.numero_comprobante).zfill(8)}")
# 		current_y -= 12
# 
# 		c.drawString(x_right, current_y, f"Fecha: {factura.fecha_comprobante.strftime('%d/%m/%Y') if factura.fecha_comprobante else ''}")
# 		current_y -= 12
# 
# 		# Datos de empresa (dinámicos)
# 		c.setFont("Helvetica", 9)
# 		c.drawString(x_right, current_y, f"I.V.A.: {empresa.id_iva.nombre_iva if empresa.id_iva else 'RESP.INSCRIPTOS'}")
# 		current_y -= 12
# 
# 		c.drawString(x_right, current_y, f"CUIT: {empresa.cuit}")
# 		current_y -= 12
# 
# 		c.drawString(x_right, current_y, f"Ingresos Brutos: {empresa.ingresos_bruto}")
# 		current_y -= 12
# 
# 		c.drawString(x_right, current_y, f"Inicio de Actividades: {empresa.inicio_actividad.strftime('%d/%m/%Y') if empresa.inicio_actividad else ''}")
# 		current_y -= 15
# 
# 		y_position -= header_top_height - 5*mm
# 		
# 		############################
# 		# 1.5 Sección de datos del cliente
# 		# current_y = y_position - 15*mm  # Ajustar posición Y después del encabezado
# 
# 		# Estilo para etiquetas
# 		style_label = ParagraphStyle(
# 			'label',
# 			fontName='Helvetica-Bold',
# 			fontSize=9,
# 			leading=10,
# 			alignment=TA_LEFT
# 		)
# 
# 		# Dibujar recuadro para datos del cliente
# 		c.rect(margin, current_y - 30*mm, width - 2*margin, 30*mm)
# 
# 		# Datos del cliente - primera línea
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 5*mm, current_y - 15*mm, "Cuenta:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 25*mm, current_y - 15*mm, str(cliente.id_cliente))
# 
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 60*mm, current_y - 15*mm, "Ap. y Nombre / Razón Social:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 120*mm, current_y - 15*mm, cliente.nombre_cliente[:40])  # Limitado a 40 caracteres
# 
# 		# Datos del cliente - segunda línea
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 5*mm, current_y - 20*mm, "I.V.A.:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 25*mm, current_y - 20*mm, cliente.id_tipo_iva.nombre_iva if cliente.id_tipo_iva else "")
# 
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 60*mm, current_y - 20*mm, "Domicilio:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 120*mm, current_y - 20*mm, cliente.domicilio_cliente[:40])  # Limitado a 40 caracteres
# 
# 		# Datos del cliente - tercera línea
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 5*mm, current_y - 25*mm, "C.U.I.T:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 25*mm, current_y - 25*mm, str(cliente.cuit))
# 
# 		c.setFont("Helvetica-Bold", 9)
# 		c.drawString(margin + 60*mm, current_y - 25*mm, "Localidad:")
# 		c.setFont("Helvetica", 9)
# 		c.drawString(margin + 120*mm, current_y - 25*mm, cliente.id_localidad.nombre_localidad if cliente.id_localidad else "")
# 
# 		# Ajustar posición Y para la tabla de detalles
# 		y_position = current_y - 30*mm
# 		############################
# 
# 		# 2. Tabla de detalles de factura
# 		encabezados = ["Medida", "Descripción", "Cantidad", "Precio", "Desc.%", "Total"]
# 		detalle_data = [encabezados]
# 		
# 		for detalle in detalles:
# 			detalle_data.append([
# 				detalle.id_producto.medida[:10] if detalle.id_producto else "",
# 				detalle.producto_venta or "",
# 				f"{detalle.cantidad:,.2f}".replace(",", ".") if detalle.cantidad else "0.00",
# 				f"${detalle.precio:,.2f}".replace(",", ".") if detalle.precio else "$0.00",
# 				f"{detalle.descuento:.2f}%" if detalle.descuento else "0%",
# 				f"${detalle.total:,.2f}".replace(",", ".") if detalle.total else "$0.00"
# 			])
# 		
# 		# Configuración de la tabla
# 		col_widths = [25*mm, 70*mm, 20*mm, 25*mm, 20*mm, 25*mm]
# 		tabla = Table(detalle_data, colWidths=col_widths, repeatRows=1)
# 		
# 		tabla.setStyle(TableStyle([
# 			('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),  # Gris claro para el encabezado
# 			('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# 			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# 			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# 			('FONTSIZE', (0, 0), (-1, 0), 8),
# 			('BOTTOMPADDING', (0, 0), (-1, 0), 6),
# 			('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Blanco para el cuerpo
# 			('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#7F7F7F")),
# 			('FONTSIZE', (0, 1), (-1, -1), 8),
# 			('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# 			('ALIGN', (1, 0), (1, -1), 'LEFT'),
# 		]))
# 		
# 		# Dibujar tabla
# 		tabla.wrapOn(c, width - 2*margin, height)
# 		tabla.drawOn(c, margin, y_position - (8 * len(detalle_data)*mm))
# 		y_position -= (8 * len(detalle_data)*mm) + 20*mm
# 		
# 		# 3. Totales
# 		"""
# 		p.setFont("Helvetica-Bold", 10)
# 		p.drawString(width - 250, y_position, "Subtotal:")
# 		p.drawString(width - 150, y_position, f"${factura.gravado + factura.exento:,.2f}".replace(",", "."))
# 		y_position -= 12
# 		
# 		p.drawString(width - 250, y_position, "IVA 21%:")
# 		p.drawString(width - 150, y_position, f"${factura.iva:,.2f}".replace(",", "."))
# 		y_position -= 12
# 		
# 		p.drawString(width - 250, y_position, "Percep. IIBB:")
# 		p.drawString(width - 150, y_position, f"${factura.percep_ib:,.2f}".replace(",", "."))
# 		y_position -= 15
# 		
# 		p.setFont("Helvetica-Bold", 12)
# 		p.drawString(width - 250, y_position, "TOTAL:")
# 		p.drawString(width - 150, y_position, f"${factura.total:,.2f}".replace(",", "."))
# 		y_position -= 25
# 		"""
# 		
# 		c.setFont("Helvetica-Bold", 10)
# 		c.drawString(width - 250, y_position, "Subtotal:")
# 		c.drawRightString(width - 50, y_position, f"${factura.gravado + factura.exento:,.2f}".replace(",", "."))
# 		y_position -= 12
# 
# 		c.drawString(width - 250, y_position, "IVA 21%:")
# 		c.drawRightString(width - 50, y_position, f"${factura.iva:,.2f}".replace(",", "."))
# 		y_position -= 12
# 
# 		c.drawString(width - 250, y_position, "Percep. IIBB:")
# 		c.drawRightString(width - 50, y_position, f"${factura.percep_ib:,.2f}".replace(",", "."))
# 		y_position -= 15
# 
# 		c.setFont("Helvetica-Bold", 12)
# 		c.drawString(width - 250, y_position, "TOTAL:")
# 		c.drawRightString(width - 50, y_position, f"${factura.total:,.2f}".replace(",", "."))
# 		y_position -= 25
# 		
# 		# 4. Datos CAE si existe
# 		if factura.cae:
# 			c.setFont("Helvetica-Bold", 10)
# 			c.drawString(margin, y_position, f"CAE N°: {factura.cae}")
# 			y_position -= 12
# 			
# 			c.drawString(margin, y_position, f"Vto. CAE: {factura.cae_vto.strftime('%d/%m/%Y') if factura.cae_vto else ''}")
# 			y_position -= 20
# 		
# 		# 5. Pie de página
# 		c.setFont("Helvetica-Bold", 10)
# 		c.drawCentredString(width/2, y_position, "Recibi Conforme")
# 		y_position -= 20
# 		
# 		c.drawCentredString(width/2, y_position, "Comprobante Autorizado")
# 		y_position -= 15
# 		
# 		c.drawCentredString(width/2, y_position, "ORIGINAL / DUPLICADO")
		'''
		
		c.showPage()
		c.save()
		
		buffer.seek(0)
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="factura_{recibo.numero_comprobante}.pdf"'
		return response
		
	def generar_pdf_default(self, model_string, pk):
		buffer = BytesIO()
		p = canvas.Canvas(buffer, pagesize=portrait(A4))
		p.setFont("Helvetica", 12)
		p.drawString(100, 750, f"Documento {model_string} - ID {pk}")
		p.showPage()
		p.save()
		buffer.seek(0)
		response = HttpResponse(buffer, content_type='application/pdf')
		response['Content-Disposition'] = f'inline; filename="{model_string}_{pk}.pdf"'
		return response