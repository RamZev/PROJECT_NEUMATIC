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
		#-- Se crea la consulta parametrizada.
		query = "SELECT * FROM VLFactPendiente WHERE id_cliente_id = %s"
		
		#-- Se añade el parámetro.
		params = [id_cliente]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)
	
	def obtener_resumen_cta_cte(self, id_cliente, fecha_desde, fecha_hasta):
		#-- Se crea la consulta parametrizada.
		query = "SELECT * FROM VLFactPendiente WHERE id_cliente_id = %s AND fecha_comprobante BETWEEN %s AND %s"
		
		#-- Se añade los parámetros.
		params = [id_cliente, fecha_desde, fecha_hasta]
		
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
		db_table = 'VLFactPendiente'
		verbose_name = ('Facturas Pendientes')
		verbose_name_plural = ('Facturas Pendientes')
		ordering = ['razon_social']
