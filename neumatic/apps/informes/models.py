from django.db import models

#-----------------------------------------------------------------------------
# Saldos Clientes
#-----------------------------------------------------------------------------
class SaldosClientesManager(models.Manager):

	def obtener_saldos_clientes(self, fecha_hasta, id_vendedor=None):
		
		#-- Se crea la consulta parametrizada.
		query = """
		SELECT 
			id_cliente_id, 
			nombre_cliente, 
			domicilio_cliente, 
			nombre_localidad, 
			codigo_postal, 
			telefono_cliente, 
			sub_cuenta, 
			SUM(total * (mult_saldo * 1.00)) AS saldo,
			MIN(CASE WHEN condicion_comprobante = 2 AND mult_saldo <> 0 AND total <> entrega THEN fecha_comprobante END) AS primer_fact_impaga, 
			MAX(fecha_pago) AS ultimo_pago 
		FROM VLSaldosClientes
		WHERE 
			fecha_comprobante <= %s
		"""
		
		#-- Se añade el parámetro fecha.
		params = [fecha_hasta]
		
		#-- Condición adicional para el vendedor si está definido.
		if id_vendedor:
			query += " AND id_vendedor_id = %s"
			params.append(id_vendedor)
		
		#-- Se agrega la clausula GROUP BY y ORDER BY.
		query += """
		GROUP BY 
			id_cliente_id
		ORDER BY
			nombre_cliente
		"""
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


#-- Modelo asociado a una consulta RAW SQL con parámetros dinámicos.
class VLSaldosClientes(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	nombre_cliente = models.CharField(max_length=50)
	domicilio_cliente = models.CharField(max_length=50)
	nombre_localidad = models.CharField(max_length=30)
	codigo_postal = models.CharField(max_length=5)
	telefono_cliente = models.CharField(max_length=15)
	sub_cuenta = models.CharField(max_length=6)
	id_vendedor_id = models.IntegerField()
	total = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = SaldosClientesManager()
	
	class Meta:
		managed = False  #-- No gestionamos la creación/edición de la vista (Ignorado para migraciones).
		db_table = 'VLSaldosClientes'  #-- Nombre de la vista en la base de datos.
		verbose_name = ('Saldos de Clientes')
		verbose_name_plural = ('Saldos de Clientes')
		ordering = ['nombre_cliente']


#-----------------------------------------------------------------------------
# Resumen Cuenta Corriente
#-----------------------------------------------------------------------------
class ResumenCtaCteManager(models.Manager):

	def obtener_fact_pendientes(self, id_cliente):
		""" Se determina los comprobantes pendientes de un cliente determinado. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			WITH acumulado AS (
				SELECT 
					id_cliente_id,
					fecha_comprobante,
					numero_comprobante,
					(total - entrega) AS saldo, 
					ROW_NUMBER() OVER (
						PARTITION BY id_cliente_id 
						ORDER BY fecha_comprobante, numero_comprobante
					) AS row_num
				FROM VLResumenCtaCte
				WHERE id_cliente_id = %s
				AND total <> entrega
			)
			SELECT 
				r.id_cliente_id, 
				r.razon_social, 
				r.nombre_comprobante_venta, 
				r.letra_comprobante, 
				r.numero_comprobante, 
				r.numero, 
				r.fecha_comprobante, 
				r.remito, 
				r.condicion_comprobante, 
				r.condicion, 
				r.total, 
				r.entrega, 
				CASE
					WHEN r.total >= 0 THEN r.total * 1.0
					ELSE ''
				END AS debe,
				CASE
					WHEN r.total < 0 THEN r.total * 1.0
					ELSE ''
				END AS haber,
				(
					SELECT SUM(a.saldo)
					FROM acumulado a
					WHERE a.id_cliente_id = r.id_cliente_id
					AND a.row_num <= (
						SELECT row_num 
						FROM acumulado 
						WHERE id_cliente_id = r.id_cliente_id 
						AND fecha_comprobante = r.fecha_comprobante
						AND numero_comprobante = r.numero_comprobante
					)
				) AS saldo_acumulado,
				r.intereses
			FROM VLResumenCtaCte r
			WHERE r.id_cliente_id = %s 
			AND r.total <> r.entrega
			ORDER BY r.fecha_comprobante, r.numero_comprobante;
			"""
		
		#-- Se añade el parámetro.
		params = [id_cliente, id_cliente]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)
	
	def obtener_resumen_cta_cte(self, id_cliente, fecha_desde, fecha_hasta, condicion_venta1, condicion_venta2):
		""" Determina el Resumen de Cuenta Corriente de un cliente y período determinados. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT 
				r.id_cliente_id, 
				r.razon_social, 
				r.nombre_comprobante_venta, 
				r.letra_comprobante, 
				r.numero_comprobante, 
				r.numero, 
				r.fecha_comprobante, 
				r.remito, 
				r.condicion_comprobante, 
				r.condicion, 
				r.total, 
				r.entrega, 
				CASE
					WHEN r.total >= 0 THEN r.total * 1.0
					ELSE ''
				END AS debe,
				CASE
					WHEN r.total < 0 THEN r.total * 1.0
					ELSE ''
				END AS haber,
				SUM(r.total) OVER (
					PARTITION BY r.id_cliente_id 
					ORDER BY r.fecha_comprobante, r.numero_comprobante
				) AS saldo_acumulado,
				r.intereses
			FROM VLResumenCtaCte r
			WHERE r.id_cliente_id = %s 
			AND r.fecha_comprobante BETWEEN %s AND %s 
			AND r.condicion_comprobante BETWEEN %s AND %s
			ORDER BY r.fecha_comprobante, r.numero_comprobante;
		"""
		
		#-- Se añade los parámetros.
		params = [id_cliente, fecha_desde, fecha_hasta, condicion_venta1, condicion_venta2]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)
	
	def obtener_saldo_anterior(self, id_cliente, fecha_desde):
		""" Método que calcula y devuelve el saldo anterior a la fecha desde de un cliente dado. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT v.id_cliente_id, COALESCE(SUM(v.total * 1.0), 0.0) AS saldo_anterior 
				FROM VLResumenCtaCte v 
				WHERE v.id_cliente_id = %s AND v.fecha_comprobante < %s;
		"""
		
		#-- Se añade los parámetros.
		params = [id_cliente, fecha_desde]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLResumenCtaCte(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	razon_social = models.CharField(max_length=50)
	nombre_comprobante_venta = models.CharField(max_length=50)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	numero = models.CharField(max_length=13)
	fecha_comprobante = models.DateField()
	remito = models.CharField(max_length=15)
	condicion_comprobante = models.IntegerField()
	total = models.DecimalField(max_digits=14, decimal_places=2)
	entrega = models.DecimalField(max_digits=14, decimal_places=2)
	saldo = models.DecimalField(max_digits=14, decimal_places=2)
	saldo_acumulado = models.DecimalField(max_digits=14, decimal_places=2)
	intereses = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = ResumenCtaCteManager()
	
	class Meta:
		managed = False
		db_table = 'VLResumenCtaCte'
		verbose_name = ('Facturas Pendientes')
		verbose_name_plural = ('Facturas Pendientes')
		ordering = ['razon_social']


#-----------------------------------------------------------------------------
# Mercadería por Cliente
#-----------------------------------------------------------------------------
class MercaderiaPorClienteManager(models.Manager):

	def obtener_fact_pendientes(self, id_cliente, fecha_desde, fecha_hasta):
		""" Se determina los comprobantes pendientes de un cliente determinado. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT * 
				FROM VLMercaderiaPorCliente v 
				WHERE v.id_cliente_id = %s AND v.fecha_comprobante BETWEEN %s AND %s;
		"""
		
		#-- Se añade los parámetros.
		params = [id_cliente, fecha_desde, fecha_hasta]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)

		
class VLMercaderiaPorCliente(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	nombre_comprobante_venta = models.CharField(max_length=50)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	numero = models.CharField(max_length=13)
	fecha_comprobante = models.DateField()
	nombre_producto_marca = models.CharField(max_length=50)
	medida = models.CharField(max_length=15)
	id_producto_id = models.IntegerField()
	nombre_producto = models.CharField(max_length=50)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = MercaderiaPorClienteManager()
	
	class Meta:
		managed = False
		db_table = 'VLMercaderiaPorCliente'
		verbose_name = ('Mercadería por Cliente')
		verbose_name_plural = ('Mercadería por Cliente')
		ordering = ['id_cliente_id', 'fecha_comprobante']


#-----------------------------------------------------------------------------
# Remitos por Cliente
#-----------------------------------------------------------------------------
class RemitosPorClienteManager(models.Manager):

	def obtener_remitos_por_cliente(self, id_cliente, fecha_desde, fecha_hasta):
		""" Se determina los comprobantes pendientes de un cliente determinado. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT * 
				FROM VLRemitosPorCliente v 
				WHERE v.id_cliente_id = %s AND v.fecha_comprobante BETWEEN %s AND %s;
		"""
		
		#-- Se añade los parámetros.
		params = [id_cliente, fecha_desde, fecha_hasta]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLRemitosPorCliente(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	id_comprobante_venta_id = models.IntegerField()
	compro = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	numero = models.CharField(max_length=13)
	nombre_producto = models.CharField(max_length=50)
	medida = models.CharField(max_length=15)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = RemitosPorClienteManager()
	
	class Meta:
		managed = False
		db_table = 'VLMercaderiaPorCliente'
		verbose_name = ('Mercadería por Cliente')
		verbose_name_plural = ('Mercadería por Cliente')
		ordering = ['id_cliente_id', 'fecha_comprobante']

"""
SELECT 
	f.id_cliente_id, 
	f.fecha_comprobante,
	f.id_comprobante_venta_id, 
	f.compro, 
	f.letra_comprobante, 
	f.numero_comprobante, 
	p.nombre_producto, 
	p.medida, 
	df.cantidad,
	df.precio, 
	df.total*cv.mult_stock*-1 AS total
 FROM factura f 
	JOIN detalle_factura df ON df.id_factura_id = f.id_factura
 	JOIN comprobante_venta cv ON cv.id_comprobante_venta = f.id_comprobante_venta_id
	JOIN producto p ON p.id_producto = df.id_producto_id = p.id_producto
 WHERE 
	f.compro BETWEEN "RD" AND "RT" AND cv.mult_venta = 0
 ORDER BY f.fecha_comprobante, f.numero_comprobante

SELECT 
	Detven.compro, 
	Detven.letra, 
	Detven.numero, 
	Facturas.fecha,
	Facturas.cliente, 
	Lista.nombre, 
	Lista.medida, 
	Detven.cantidad,
	Detven.precio, 
	Detven.descuento,
	Detven.total*Codven.mult_sto*-1 AS total
 FROM facturas, codven,
	detven INNER JOIN lista ON  Detven.codigo = Lista.codigo;
 WHERE Detven.compro = Facturas.compro;
   AND Detven.letra = Facturas.letra;
   AND Detven.numero = Facturas.numero;
   AND Detven.compro = Codven.compro;
   AND (Detven.compro BETWEEN "RD" AND "RT";
   AND Facturas.cliente = ?nCliente;
   AND Codven.mult_ven = 0);
 ORDER BY Facturas.fecha, Detven.numero


"""