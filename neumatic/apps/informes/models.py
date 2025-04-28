from django.db import models


#-----------------------------------------------------------------------------
# Saldos Clientes.
#-----------------------------------------------------------------------------
class SaldosClientesManager(models.Manager):

	def obtener_saldos_clientes(self, fecha_hasta, id_vendedor=None):
		
		#-- Se crea la consulta.
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
		
		#-- Se añaden parámetros.
		params = [fecha_hasta]
		
		#-- Filtros adicionales.
		if id_vendedor:
			query += " AND id_vendedor_id = %s"
			params.append(id_vendedor)
		
		#-- Se completa la consulta.
		query += """
		GROUP BY 
			id_cliente_id, nombre_cliente, domicilio_cliente, nombre_localidad, 
			codigo_postal, telefono_cliente, sub_cuenta
		HAVING 
			ROUND(SUM(total * (mult_saldo * 1.00)), 2) <> 0
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
# Resumen Cuenta Corriente.
#-----------------------------------------------------------------------------
class ResumenCtaCteManager(models.Manager):

	def obtener_fact_pendientes(self, id_cliente):
		""" Se determina los comprobantes pendientes de un cliente determinado. """
		
		#-- Se crea la consulta.
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
				WHERE id_cliente_id = %s AND total <> entrega
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
					ELSE 0.0
				END AS debe,
				CASE
					WHEN r.total < 0 THEN r.total * 1.0
					ELSE 0.0
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
			WHERE r.id_cliente_id = %s AND r.total <> r.entrega
			ORDER BY r.fecha_comprobante, r.numero_comprobante;
			"""
		
		#-- Se añaden parámetros.
		params = [id_cliente, id_cliente]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)
	
	def obtener_resumen_cta_cte(self, id_cliente, fecha_desde, fecha_hasta, condicion_venta1, condicion_venta2):
		""" Determina el Resumen de Cuenta Corriente de un cliente y período determinados. """
		
		#-- Se crea la consulta.
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
					ELSE 0.0
				END AS debe,
				CASE
					WHEN r.total < 0 THEN r.total * 1.0
					ELSE 0.0
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
		
		#-- Se añaden parámetros.
		params = [id_cliente, fecha_desde, fecha_hasta, condicion_venta1, condicion_venta2]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)
	
	def obtener_saldo_anterior(self, id_cliente, fecha_desde):
		""" Método que calcula y devuelve el saldo anterior a la fecha desde de un cliente dado. """
		
		query = """
			SELECT 
				v.id_cliente_id, 
				COALESCE(ROUND(SUM(v.total * 1.0), 2), 0.00) AS saldo_anterior 
			FROM VLResumenCtaCte v 
			WHERE v.id_cliente_id = %s AND v.fecha_comprobante < %s;
		"""
		
		#-- Se añaden parámetros.
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
	saldo_acumulado = models.DecimalField(max_digits=14, decimal_places=2)
	intereses = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = ResumenCtaCteManager()
	
	class Meta:
		managed = False
		db_table = 'VLResumenCtaCte'
		verbose_name = ('Resumen de Cta. Cte.')
		verbose_name_plural = ('Resumen de Cta. Cte.')
		ordering = ['razon_social']


#-----------------------------------------------------------------------------
# Mercadería por Cliente.
#-----------------------------------------------------------------------------
class MercaderiaPorClienteManager(models.Manager):

	def obtener_mercaderia_por_cliente(self, id_cliente, fecha_desde, fecha_hasta):
		""" Se determina los comprobantes pendientes de un cliente determinado. """
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLMercaderiaPorCliente v 
			WHERE v.id_cliente_id = %s AND v.fecha_comprobante BETWEEN %s AND %s;
		"""
		
		#-- Se añaden parámetros.
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
# Remitos por Clientes.
#-----------------------------------------------------------------------------
class RemitosClientesManager(models.Manager):

	def obtener_remitos_por_cliente(self, id_cliente, fecha_desde, fecha_hasta):
		""" Se determina los Remitos de un cliente determinado. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT * 
			FROM VLRemitosClientes
			WHERE id_cliente_id = %s AND 
				codigo_comprobante_venta BETWEEN %s AND %s AND
				fecha_comprobante BETWEEN %s AND %s;
		"""
		
		#-- Se añaden parámetros.
		params = [id_cliente, "RD", "RT", fecha_desde, fecha_hasta]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLRemitosClientes(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	id_comprobante_venta_id = models.IntegerField()
	codigo_comprobante_venta = models.CharField(max_length=3)
	nombre_comprobante_venta = models.CharField(max_length=50)
	fecha_comprobante = models.DateField()
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	numero = models.CharField(max_length=13)
	nombre_producto = models.CharField(max_length=50)
	medida = models.CharField(max_length=15)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = RemitosClientesManager()
	
	class Meta:
		managed = False
		db_table = 'VLRemitosClientes'
		verbose_name = ('Remitos por Clientes')
		verbose_name_plural = ('Remitos por Clientes')
		ordering = ['id_cliente_id', 'fecha_comprobante', 'numero_comprobante']


#-----------------------------------------------------------------------------
# Total Remitos por Clientes.
#-----------------------------------------------------------------------------
class TotalRemitosClientesManager(models.Manager):

	def obtener_total_remitos_cliente(self, id_cliente, fecha_desde, fecha_hasta):
		""" Se determina los Totales de Remitos por clientes. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT 
				id_cliente_id, 
				fecha_comprobante, 
				nombre_cliente, 
				domicilio_cliente, 
				codigo_postal, 
				nombre_iva, 
				cuit, 
				telefono_cliente, 
				SUM(total) AS total
			FROM VLTotalRemitosClientes 
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Filtros adicionales.
		if id_cliente:
			query += " AND id_cliente_id = %s "
			params.append(id_cliente)
		
		#-- Completar la consulta.
		query += "GROUP BY id_cliente_id;"
	
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLTotalRemitosClientes(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	nombre_cliente = models.CharField(max_length=50)
	domicilio_cliente = models.CharField(max_length=50)
	codigo_postal = models.CharField(max_length=5)
	nombre_iva = models.CharField(max_length=25)
	cuit = models.IntegerField()
	telefono_cliente = models.CharField(max_length=15)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = TotalRemitosClientesManager()
	
	class Meta:
		managed = False
		db_table = 'VLTotalRemitosClientes'
		verbose_name = ('Totales de Remitos por Clientes')
		verbose_name_plural = ('Totales de Remitos por Clientes')
		ordering = ['nombre_cliente']


#-----------------------------------------------------------------------------
# Ventas por Localidad.
#-----------------------------------------------------------------------------
class VentaComproLocalidadManager(models.Manager):

	def obtener_venta_compro_localidad(self, fecha_desde, fecha_hasta, sucursal=None, codigo_postal=None):
		"""
		Retorna un RawQuerySet con las ventas dentro del rango de fechas, y opcionalmente
		filtra por sucursal y código postal, aplicando todo el filtrado directamente en SQL.
		"""
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT *
			FROM VLVentaComproLocalidad 
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Filtros adicionales.
		if sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(sucursal.id_sucursal)
		
		if codigo_postal:
			query += " AND codigo_postal = %s"
			params.append(codigo_postal)
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLVentaComproLocalidad(models.Model):
	id_cliente_id = models.IntegerField(primary_key=True)
	id_sucursal_id = models.IntegerField()
	fecha_comprobante = models.DateField()
	nombre_cliente = models.CharField(max_length=50)
	cuit = models.IntegerField()
	codigo_postal = models.CharField(max_length=5)
	codigo_comprobante_venta = models.CharField(max_length=3)
	nombre_comprobante_venta = models.CharField(max_length=50)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	exento = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	iniciales = models.CharField(max_length=3)
	
	objects = VentaComproLocalidadManager()
	
	class Meta:
		managed = False
		db_table = 'VLVentaComproLocalidad'
		verbose_name = ('Ventas por Localidad')
		verbose_name_plural = ('Ventas por Localidad')
		ordering = ['fecha_comprobante']


#-----------------------------------------------------------------------------
# Ventas por Mostrador.
#-----------------------------------------------------------------------------
class VentaMostradorManager(models.Manager):

	def obtener_venta_mostrador(self, fecha_desde, fecha_hasta, sucursal=None, tipo_venta=None, tipo_cliente=None, tipo_producto=None):
		""" Se determina las Ventas por Mostrador por un rango de fechas, aplicando filtros. """
		
		#-- Se crea la consulta.
		query = """
			SELECT *
			FROM VLVentaMostrador 
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Filtros adicionales.
		if sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(sucursal.id_sucursal)
		
		if tipo_venta and tipo_venta != "T":
			query += " AND reventa = %s"
			params.append(tipo_venta)
		
		if tipo_cliente == "M":
			query += " AND mayorista = %s"
			params.append(True)
		elif tipo_cliente == "R":
			query += " AND mayorista = %s"
			params.append(False)
		
		if tipo_producto and tipo_producto != "T":
			query += " AND tipo_producto = %s"
			params.append(tipo_producto)		
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLVentaMostrador(models.Model):
	id_detalle_factura = models.IntegerField(primary_key=True)
	nombre_comprobante_venta = models.CharField(max_length=50)
	codigo_comprobante_venta = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	fecha_comprobante = models.DateField()
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	mayorista = models.BooleanField()
	reventa = models.CharField(max_length=1)
	id_producto_id = models.IntegerField()
	nombre_producto = models.CharField(max_length=50)
	tipo_producto = models.CharField(max_length=1)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	
	objects = VentaMostradorManager()
	
	class Meta:
		managed = False
		db_table = 'VLVentaMostrador'
		verbose_name = ('Ventas por Mostrador')
		verbose_name_plural = ('Ventas por Mostrador')
		ordering = ['fecha_comprobante', 'numero_comprobante']


#-----------------------------------------------------------------------------
# Ventas por Comprobantes.
#-----------------------------------------------------------------------------
class VentaComproManager(models.Manager):

	def obtener_venta_compro(self, fecha_desde, fecha_hasta, sucursal=None):
		""" Se determina las Ventas por Comprobante por un rango de fechas, aplicando filtros. """
		
		#-- Se crea la consulta parametrizada.
		query = """
			SELECT *
			FROM VLVentaCompro 
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Filtros adicionales.
		if sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(sucursal.id_sucursal)
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLVentaCompro(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	nombre_comprobante_venta = models.CharField(max_length=50)
	codigo_comprobante_venta = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	fecha_comprobante = models.DateField()
	dias_vencimiento = models.IntegerField()
	condicion = models.CharField(max_length=9)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	
	objects = VentaComproManager()
	
	class Meta:
		managed = False
		db_table = 'VLVentaCompro'
		verbose_name = ('Ventas por Comprobantes')
		verbose_name_plural = ('Ventas por Comprobantes')
		ordering = ['comprobante']


#-----------------------------------------------------------------------------
# Comprobantes Vencidos.
#-----------------------------------------------------------------------------
class ComprobantesVencidosManager(models.Manager):
	
	def obtener_compro_vencidos(self, dias, id_vendedor=None, id_sucursal=None):
		""" Se determina los Comprobantes vencidos según parámetro indicado por vendedor o todos los vendedores,
		una sucursal o todas. """
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLComprobantesVencidos 
			WHERE dias_vencidos > %s
		"""
		
		#-- Se añaden parámetros.
		params = [dias]
		
		#-- Filtros adicionales.
		if id_vendedor:
			query += " AND id_vendedor_id = %s"
			params.append(id_vendedor)
		
		if id_sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(id_sucursal)
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLComprobantesVencidos(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	dias_vencidos = models.IntegerField()
	codigo_comprobante_venta = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	entrega = models.DecimalField(max_digits=14, decimal_places=2)
	saldo = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	id_vendedor_id = models.IntegerField()
	
	objects = ComprobantesVencidosManager()
	
	class Meta:
		managed = False
		db_table = 'VLComprobantesVencidos'
		verbose_name = ('Comprobantes Vencidos')
		verbose_name_plural = ('Comprobantes Vencidos')
		ordering = ['fecha_comprobante']


#-----------------------------------------------------------------------------
# Remitos Pendientes.
#-----------------------------------------------------------------------------
class RemitosPendientesManager(models.Manager):
	
	def obtener_remitos_pendientes(self, filtrar_por, id_vendedor=None, id_cli_desde=0, id_cli_hasta=0, id_sucursal=None):
		""" Permite obtener los Remitos Pendientes por procesar según parámetros indicados: por Vendedor, rango de Ids de Cliente, 
		Sucursal de Facturación o Sucursal del Cliente. """
		
		#-- Se crea la consulta.
		query = "SELECT * FROM VLRemitosPendientes "
		
		#-- Filtros adicionales.
		match filtrar_por:
			case "vendedor":
				query += "WHERE id_vendedor_id = %s"
				params = [id_vendedor]
				
			case "clientes":
				query += "WHERE id_cliente_id BETWEEN %s AND %s"
				params = [id_cli_desde, id_cli_hasta]
				
			case "sucursal_fac":
				query += "WHERE id_sucursal_fac = %s"
				params = [id_sucursal]
				
			case "sucursal_cli":
				query += "WHERE id_sucursal_cli = %s"
				params = [id_sucursal]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLRemitosPendientes(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	nombre_comprobante_venta = models.CharField(max_length=50)
	fecha_comprobante = models.DateField()
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	id_producto_id = models.IntegerField()
	nombre_producto = models.CharField(max_length=50)
	medida = models.CharField(max_length=15)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_vendedor_id = models.IntegerField()
	id_sucursal_fac = models.IntegerField()
	id_sucursal_cli = models.IntegerField()
	
	
	objects = RemitosPendientesManager()
	
	class Meta:
		managed = False
		db_table = 'VLRemitosPendientes'
		verbose_name = ('Remitos Pendientes')
		verbose_name_plural = ('Remitos Pendientes')
		ordering = ['nombre_cliente', 'fecha_comprobante', 'numero_comprobante']


#-----------------------------------------------------------------------------
# Remitos por Vendedor.
#-----------------------------------------------------------------------------
class RemitosVendedorManager(models.Manager):
	
	def obtener_remitos_vendedor(self, id_vendedor, fecha_desde, fecha_hasta):
		""" Permite obtener los Remitos de un Vendedor específico en un período de tiempo. """
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLRemitosVendedor 
			WHERE id_vendedor_id = %s AND 
				fecha_comprobante BETWEEN %s AND %s"""
		
		#-- Se añaden parámetros.
		params = [id_vendedor, fecha_desde, fecha_hasta]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLRemitosVendedor(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	nombre_comprobante_venta = models.CharField(max_length=50)
	fecha_comprobante = models.DateField()
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	id_producto_id = models.IntegerField()
	nombre_producto = models.CharField(max_length=50)
	medida = models.CharField(max_length=15)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_vendedor_id = models.IntegerField()
	
	objects = RemitosVendedorManager()
	
	class Meta:
		managed = False
		db_table = 'VLRemitosVendedor'
		verbose_name = ('Remitos por Vendedor')
		verbose_name_plural = ('Remitos por Vendedor')
		ordering = ['nombre_cliente', 'fecha_comprobante', 'numero_comprobante']

#-----------------------------------------------------------------------------
# Libro I.V.A. Ventas - Detalle.
#-----------------------------------------------------------------------------
class IVAVentasFULLManager(models.Manager):
	
	def obtener_datos(self, id_sucursal, anno, mes):
		
		#-- Se crea la consulta.
		query = """
			SELECT * FROM VLIVAVentasFULL
			WHERE STRFTIME('%%Y', fecha_comprobante) = %s AND
				  STRFTIME('%%m', fecha_comprobante) = %s
		"""
		
		#-- Se añaden parámetros.
		params = [str(anno), str(mes)]
		
		#-- Filtros adicionales.
		if id_sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(id_sucursal)
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLIVAVentasFULL(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	# id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	codigo_iva = models.CharField(max_length=4)
	cuit = models.IntegerField()
	nombre_comprobante_venta = models.CharField(max_length=50)
	codigo_comprobante_venta = models.CharField(max_length=3)
	fecha_comprobante = models.DateField()
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=17)
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	exento = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	
	objects = IVAVentasFULLManager()
	
	class Meta:
		managed = False
		db_table = 'VLIVAVentasFULL'
		verbose_name = ('Libro de I.V.A. Ventas - Detalle')
		verbose_name_plural = ('Libro de I.V.A. Ventas - Detalle')
		ordering = ['fecha_comprobante', 'numero_comprobante']

#-----------------------------------------------------------------------------
# Libro I.V.A. Ventas - Totales por Provincias.
#-----------------------------------------------------------------------------
class VLIVAVentasProvinciasManager(models.Manager):
	
	def obtener_datos(self, id_sucursal, anno, mes):
		
		#-- Se crea la consulta.
		query = """
			SELECT 
				id_factura, 
				nombre_provincia,
				ROUND(SUM(gravado), 2) AS gravado,
				ROUND(SUM(exento), 2) AS exento,
				ROUND(SUM(iva), 2) AS iva,
				ROUND(SUM(percep_ib), 2) AS percep_ib,
				ROUND(SUM(total), 2) AS total
			FROM VLIVAVentasProvincias
			WHERE STRFTIME('%%Y', fecha_comprobante) = %s AND
				  STRFTIME('%%m', fecha_comprobante) = %s
		"""
		
		#-- Se añaden parámetros.
		params = [str(anno), str(mes)]
		
		#-- Filtros adicionales.
		if id_sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(id_sucursal)
		
		#-- Se completa la consulta.
		query += " GROUP BY nombre_provincia"
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLIVAVentasProvincias(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_provincia = models.IntegerField()
	nombre_provincia = models.CharField(max_length=30)
	fecha_comprobante = models.DateField()
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	exento = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	
	objects = VLIVAVentasProvinciasManager()
	
	class Meta:
		managed = False
		db_table = 'VLIVAVentasProvincias'
		verbose_name = ('Libro de I.V.A. Ventas - Totales por Provincias')
		verbose_name_plural = ('Libro de I.V.A. Ventas - Totales por Provincias')
		ordering = ['nombre_provincia']


#-----------------------------------------------------------------------------
# Libro I.V.A. Ventas - Totales para SITRIB.
#-----------------------------------------------------------------------------
class VLIVAVentasSitribManager(models.Manager):
	
	def obtener_datos(self, id_sucursal, anno, mes):
		
		#-- Se crea la consulta.
		query = """
			SELECT 
				id_factura,
				codigo_iva,
				nombre_iva,
				ROUND(SUM(gravado), 2) AS gravado, 
				ROUND(SUM(exento), 2) AS exento, 
				ROUND(SUM(iva), 2) AS iva, 
				ROUND(SUM(percep_ib), 2) AS percep_ib, 
				ROUND(SUM(total), 2) AS total
			FROM VLIVAVentasSitrib
			WHERE STRFTIME('%%Y', fecha_comprobante) = %s AND
				  STRFTIME('%%m', fecha_comprobante) = %s
		"""
		
		#-- Se añaden parámetros.
		params = [str(anno), str(mes)]
		
		#-- Filtros adicionales.
		if id_sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(id_sucursal)
		
		#-- Se completa la consulta.
		query += " GROUP BY codigo_iva"
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLIVAVentasSitrib(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	codigo_iva = models.CharField(max_length=4)
	nombre_iva = models.CharField(max_length=25)
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	exento = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_sucursal_id = models.IntegerField()
	
	objects = VLIVAVentasSitribManager()
	
	class Meta:
		managed = False
		db_table = 'VLIVAVentasSitrib'
		verbose_name = ('Libro de I.V.A. Ventas - Totales para SITRIB')
		verbose_name_plural = ('Libro de I.V.A. Ventas - Totales para SITRIB')
		ordering = ['codigo_iva']


#-----------------------------------------------------------------------------
# Percepción IB por Vendedores - Totales.
#-----------------------------------------------------------------------------
class VLPercepIBVendedorTotalesManager(models.Manager):
	
	def obtener_datos(self, fecha_desde, fecha_hasta):
		
		#-- Se crea la consulta.
		query = """
			SELECT 
				id_factura,
				id_vendedor_id,
				nombre_vendedor,
				ROUND(SUM(neto), 2) AS neto, 
				ROUND(SUM(percep_ib), 2) AS percep_ib
			FROM VLPercepIBVendedorTotales
			WHERE fecha_comprobante BETWEEN %s AND %s
			GROUP BY id_vendedor_id
			ORDER by nombre_vendedor
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLPercepIBVendedorTotales(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	id_vendedor_id = models.IntegerField()
	nombre_vendedor = models.CharField(max_length=30)
	neto = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = VLPercepIBVendedorTotalesManager()
	
	class Meta:
		managed = False
		db_table = 'VLPercepIBVendedorTotales'
		verbose_name = ('Percepciones por Vendedor - Totales')
		verbose_name_plural = ('Percepciones por Vendedor - Totales')
		ordering = ['id_vendedor_id']


#-----------------------------------------------------------------------------
# Percepción IB por Vendedores - Detallado.
#-----------------------------------------------------------------------------
class VLPercepIBVendedorDetalladoManager(models.Manager):
	
	def obtener_datos(self, fecha_desde, fecha_hasta):
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLPercepIBVendedorDetallado
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Lista de parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLPercepIBVendedorDetallado(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_vendedor_id = models.IntegerField()
	nombre_vendedor = models.CharField(max_length=30)
	compro = models.CharField(max_length=3)	
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	fecha_comprobante = models.DateField()
	comprobante = models.CharField(max_length=30)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	cuit = models.IntegerField()
	neto = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = VLPercepIBVendedorDetalladoManager()
	
	class Meta:
		managed = False
		db_table = 'VLPercepIBVendedorDetallado'
		verbose_name = ('Percepciones por Vendedor - Detallado')
		verbose_name_plural = ('Percepciones por Vendedor - Detallado')
		ordering = ['nombre_vendedor']


#-----------------------------------------------------------------------------
# Percepción IB por Sub Cuentas - Totales.
#-----------------------------------------------------------------------------
class VLPercepIBSubcuentaTotalesManager(models.Manager):
	
	def obtener_datos(self, fecha_desde, fecha_hasta):
		
		#-- Base de la consulta SQL.
		query = """
			SELECT 
					id_factura,
					sub_cuenta,
					nombre_cliente_padre,
					ROUND(SUM(neto), 2) AS neto, 
					ROUND(SUM(percep_ib), 2) AS percep_ib
				FROM VLPercepIBSubcuentaTotales
				WHERE fecha_comprobante BETWEEN %s AND %s
				GROUP BY sub_cuenta
				ORDER by sub_cuenta
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLPercepIBSubcuentaTotales(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	sub_cuenta = models.IntegerField()
	nombre_cliente_padre = models.CharField(max_length=50)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	neto = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = VLPercepIBSubcuentaTotalesManager()
	
	class Meta:
		managed = False
		db_table = 'VLPercepIBSubcuentaTotales'
		verbose_name = ('Percepciones por Sub Cuentas - Totales')
		verbose_name_plural = ('Percepciones por Sub Cuentas - Totales')
		ordering = ['sub_cuenta']


#-----------------------------------------------------------------------------
# Percepción IB por Sub Cuentas - Detallado.
#-----------------------------------------------------------------------------
class VLPercepIBSubcuentaDetalladoManager(models.Manager):
	
	def obtener_datos(self, fecha_desde, fecha_hasta):
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLPercepIBSubcuentaDetallado
			WHERE fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Ejecutar la consulta y devolver los resultados.
		return self.raw(query, params)

class VLPercepIBSubcuentaDetallado(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	sub_cuenta = models.IntegerField()
	nombre_cliente_padre = models.CharField(max_length=50)
	compro = models.CharField(max_length=3)	
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	fecha_comprobante = models.DateField()
	comprobante = models.CharField(max_length=30)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	cuit = models.IntegerField()
	neto = models.DecimalField(max_digits=14, decimal_places=2)
	percep_ib = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = VLPercepIBSubcuentaDetalladoManager()
	
	class Meta:
		managed = False
		db_table = 'VLPercepIBSubcuentaDetallado'
		verbose_name = ('Percepciones por Sub Cuentas - Detallado')
		verbose_name_plural = ('Percepciones por Sub Cuentas - Detallado')
		ordering = ['sub_cuenta']


#-----------------------------------------------------------------------------
# Comisión a Vendedor Según Facturaras.
#-----------------------------------------------------------------------------
class ComisionVendedorIBManager(models.Manager):
	
	def obtener_datos(self, id_vendedor, fecha_desde, Fecha_hasta):
		
		#-- Se crea la primera consulta (Recibos).
		query1 = """
			SELECT *
			FROM VLComisionVendedor
			WHERE 
				pje_comision <> 0 AND 
				fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se crea la segunda consulta (Detalle).
		query2 = """
			SELECT *
			FROM VLComisionVendedorDetalle
			WHERE 
				pje_comision <> 0 AND 
				fecha_comprobante BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, Fecha_hasta]
		
		#-- Filtros adicionales.
		if id_vendedor:
			query1 += " AND id_vendedor_id = %s"
			query2 += " AND id_vendedor_id = %s"
			params.append(id_vendedor)
		
		#-- Unir las consultas.
		query_full = f"{query1} UNION {query2} ORDER BY nombre_vendedor, fecha_comprobante, numero_comprobante"
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query_full, params*2)


class VLComisionVendedor(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	compro = models.CharField(max_length=3)	
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=19)
	fecha_comprobante = models.DateField()
	nombre_cliente = models.CharField(max_length=50)
	reventa = models.CharField(max_length=1)
	id_producto_id = models.IntegerField()
	medida = models.CharField(max_length=15)
	nombre_producto_marca = models.CharField(max_length=50)
	nombre_producto_familia = models.CharField(max_length=50)
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	pje_comision = models.DecimalField(max_digits=4, decimal_places=2)
	monto_comision = models.DecimalField(max_digits=14, decimal_places=2)
	id_vendedor_id = models.IntegerField()
	nombre_vendedor = models.CharField(max_length=30)	
	
	objects = ComisionVendedorIBManager()
	
	class Meta:
		managed = False
		db_table = 'VLComisionVendedor'
		verbose_name = ('Comisión Según Facturación')
		verbose_name_plural = ('Comisión Según Facturación')
		ordering = ['nombre_vendedor','fecha_comprobante','numero_comprobante']


#-----------------------------------------------------------------------------
# Comisiones a Operarios.
#-----------------------------------------------------------------------------
class ComisionOperarioManager(models.Manager):
	
	def obtener_datos(self, id_operario, fecha_desde, fecha_hasta):
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLComisionOperario 
			WHERE fecha_comprobante BETWEEN %s AND %s"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta]
		
		#-- Filtros adicionales.
		if id_operario:
			query += " AND id_operario_id = %s"
			params.append(id_operario)
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLComisionOperario(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_operario_id = models.IntegerField()
	nombre_operario = models.CharField(max_length=50)
	codigo_comprobante_venta = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=19)
	fecha_comprobante = models.DateField()
	id_producto_id = models.IntegerField()
	nombre_producto_familia = models.CharField(max_length=50)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	comision_operario = models.DecimalField(max_digits=5, decimal_places=2)
	monto_comision = models.DecimalField(max_digits=14, decimal_places=2)
	
	objects = ComisionOperarioManager()
	
	class Meta:
		managed = False
		db_table = 'VLComisionOperario'
		verbose_name = ('Comisiones a Operarios')
		verbose_name_plural = ('Comisiones a Operarios')
		ordering = ['nombre_operario', 'fecha_comprobante', 'numero_comprobante']


#-----------------------------------------------------------------------------
# Deferencias de Precios en Facturación.
#-----------------------------------------------------------------------------
class PrecioDiferenteManager(models.Manager):
	
	def obtener_datos(self, fecha_desde, fecha_hasta, id_vendedor_desde, id_vendedor_hasta, comprobantes, dif_mayor=0):
		
		#-- Determinar cantidad de marcas de parámetros para los comprobantes.
		placeholders = ','.join(['%s'] * len(comprobantes))
		
		#-- Se crea la consulta.
		query = """
			SELECT * 
			FROM VLPrecioDiferente 
			WHERE fecha_comprobante BETWEEN %s AND %s 
				AND id_vendedor_id BETWEEN %s AND %s 
				AND ABS(precio - precio_lista) > %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta, id_vendedor_desde, id_vendedor_hasta, dif_mayor]
		
		#-- Añadir filtro por comprobantes.
		query += f" AND compro IN ({placeholders})"
		params.extend(comprobantes)  # Extender con los elementos de la lista
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLPrecioDiferente(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_vendedor_id = models.IntegerField()
	nombre_vendedor = models.CharField(max_length=30)
	codigo_comprobante_venta = models.CharField(max_length=3)
	letra_comprobante = models.CharField(max_length=1)
	fecha_comprobante = models.DateField()
	numero_comprobante = models.IntegerField()
	comprobante = models.CharField(max_length=19)
	id_cliente_id = models.IntegerField()
	nombre_cliente = models.CharField(max_length=50)
	id_producto_id = models.IntegerField()
	nombre_producto = models.CharField(max_length=50)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	precio = models.DecimalField(max_digits=12, decimal_places=2)
	precio_lista = models.DecimalField(max_digits=12, decimal_places=2)
	diferencia = models.DecimalField(max_digits=12, decimal_places=2)
	descuento = models.DecimalField(max_digits=6, decimal_places=2)
	adicional = models.DecimalField(max_digits=12, decimal_places=2)
	
	objects = PrecioDiferenteManager()
	
	class Meta:
		managed = False
		db_table = 'VLPrecioDiferente'
		verbose_name = ('Diferencias de Precios en Facturación')
		verbose_name_plural = ('Diferencias de Precios en Facturación')
		ordering = ['nombre_vendedor', 'fecha_comprobante', 'numero_comprobante']


#-----------------------------------------------------------------------------
# Resumen de Ventas Ing. Brutos Mercadolibre.
#-----------------------------------------------------------------------------
class VentasResumenIBManager(models.Manager):
	
	def obtener_datos(self, anno, mes, id_sucursal=0):
		
		#-- Se crea la consulta.
		query = """
			SELECT *
			FROM VLVentasResumenIB
			WHERE STRFTIME('%%Y', fecha_comprobante) = %s AND
				  STRFTIME('%%m', fecha_comprobante) = %s AND
				  suc_imp = %s
		"""
		
		#-- Se añaden parámetros.
		params = [str(anno), str(mes), id_sucursal]
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLVentasResumenIB(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	fecha_comprobante = models.DateField()
	gravado = models.DecimalField(max_digits=14, decimal_places=2)
	iva = models.DecimalField(max_digits=14, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	id_provincia_id = models.IntegerField()
	nombre_provincia = models.CharField(max_length=30)	
	suc_imp = models.IntegerField()
	
	objects = VentasResumenIBManager()
	
	class Meta:
		managed = False
		db_table = 'VLVentasResumenIB'
		verbose_name = ('Resumen de Ventas por Provincias')
		verbose_name_plural = ('Resumen de Ventas por Provincias')
		ordering = ['fecha_comprobante']


#-----------------------------------------------------------------------------
# Estadísticas de Ventas.
#-----------------------------------------------------------------------------
class EstadisticasVentasManager(models.Manager):
	
	def obtener_datos(self, id_sucursal, id_cliente, fecha_desde, fecha_hasta, id_marca_desede, id_marca_hasta, agrupar, ordenar):
		
		#-- Se crea la consulta.
		# query = """
		# 	SELECT *, sum(cantidad) AS cantidad_sumada, sum(total) AS total_sumado
		# 	FROM VLEstadisticasVentas
		# 	WHERE fecha_comprobante BETWEEN %s AND %s AND
		# 		id_marca_id BETWEEN %s AND %s
		# """
		query = """
			SELECT 
				id_factura,
				id_producto_id,
				cai,
				nombre_producto,
				nombre_producto_familia,
				nombre_modelo,
				nombre_producto_marca,
				SUM(cantidad) AS cantidad, 
				SUM(total) AS total
			FROM VLEstadisticasVentas
			WHERE fecha_comprobante BETWEEN %s AND %s AND
				id_marca_id BETWEEN %s AND %s
		"""
		
		#-- Se añaden parámetros.
		params = [fecha_desde, fecha_hasta, id_marca_desede, id_marca_hasta]
		
		#-- Filtros adicionales.
		if id_sucursal:
			query += " AND id_sucursal_id = %s"
			params.append(id_sucursal)
		
		if id_cliente:
			query += " AND id_cliente_id = %s"
			params.append(id_cliente)
		
		match agrupar:
			case "Producto":
				query += " GROUP BY id_producto_id"
			case "Familia":
				query += " GROUP BY id_familia_id, id_marca_id"
			case "Modelo":
				# query += " GROUP BY id_modelo_id, id_marca_id"
				query += " GROUP BY id_modelo_id"
			case "Marca":
				query += " GROUP BY id_marca_id"
		
		if ordenar:
			match ordenar:
				case "Cantidad":
					query += " ORDER BY cantidad DESC"
				case "Importe":
					query += " ORDER BY total DESC"
		
		#-- Se ejecuta la consulta con `raw` y se devueven los resultados.
		return self.raw(query, params)


class VLEstadisticasVentas(models.Model):
	id_factura = models.IntegerField(primary_key=True)
	id_producto_id = models.IntegerField()
	cai = models.CharField(max_length=20)
	nombre_producto = models.CharField(max_length=50)
	nombre_producto_familia = models.CharField(max_length=50)
	nombre_modelo = models.CharField(max_length=50)
	nombre_producto_marca = models.CharField(max_length=50)
	cantidad = models.DecimalField(max_digits=7, decimal_places=2)
	total = models.DecimalField(max_digits=14, decimal_places=2)
	fecha_comprobante = models.DateField()
	id_cliente_id = models.IntegerField()
	id_sucursal_id = models.IntegerField()
	
	objects = EstadisticasVentasManager()
	
	class Meta:
		managed = False
		db_table = 'VLEstadisticasVentas'
		verbose_name = ('Estadísticas de Ventas')
		verbose_name_plural = ('Estadísticas de Ventas')
		# ordering = ['fecha_comprobante']


"""
---------------------------------------------------------------------------------------
-- Genérica:
SELECT factura.compro, 
	detalle_factura.id_factura, 
	detalle_factura.id_producto_id, 
	producto.cai,
	producto.nombre_producto,
	producto_familia.nombre_producto_familia, 
	producto_modelo.nombre_modelo,
	producto_marca.nombre_producto_marca,
	detalle_factura.cantidad*comprobante_venta.mult_estadistica AS cantidad,
	((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica AS total,
	factura.id_cliente_id,
	factura.fecha_comprobante,
	fatura.id_sucursal_id
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False

---------------------------------------------------------------------------------------
--Producto:
SELECT 
	detalle_factura.id_producto_id, 
	producto.cai,
	producto.nombre_producto,
	producto_familia.nombre_producto_familia, 
	producto_modelo.nombre_modelo,
	producto_marca.nombre_producto_marca,
	--producto.unidad,
	SUM(detalle_factura.cantidad*comprobante_venta.mult_estadistica) AS cantidad,
	SUM(((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica) AS total
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False
GROUP BY detalle_factura.id_producto_id
ORDER BY producto.nombre_producto

---------------------------------------------------------------------------------------
-- Familia:
SELECT 
	producto_familia.nombre_producto_familia, 
	producto_marca.nombre_producto_marca,
	SUM(detalle_factura.cantidad*comprobante_venta.mult_estadistica) AS cantidad,
	SUM(((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica) AS total
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False
GROUP BY producto.id_familia_id, producto.id_marca_id
ORDER BY producto_familia.nombre_producto_familia, producto.id_marca_id

---------------------------------------------------------------------------------------
-- Modelo:
SELECT 
	producto_modelo.nombre_modelo,
	producto_marca.nombre_producto_marca,
	SUM(detalle_factura.cantidad*comprobante_venta.mult_estadistica) AS cantidad,
	SUM(((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica) AS total
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False
GROUP BY producto.id_modelo_id, producto.id_modelo_id
ORDER BY producto_modelo.nombre_modelo, producto.id_modelo_id

---------------------------------------------------------------------------------------
-- Marca:
SELECT 
	producto_marca.nombre_producto_marca,
	SUM(detalle_factura.cantidad*comprobante_venta.mult_estadistica) AS cantidad,
	SUM(((detalle_factura.cantidad*detalle_factura.precio)+(detalle_factura.cantidad*detalle_factura.precio*detalle_factura.descuento/100))*comprobante_venta.mult_estadistica) AS total
FROM 
	detalle_factura INNER JOIN factura ON detalle_factura.id_factura_id = factura.id_factura
		INNER JOIN producto ON detalle_factura.id_producto_id = producto.id_producto
		INNER JOIN producto_modelo ON producto.id_modelo_id = producto_modelo.id_modelo
		INNER JOIN producto_familia ON producto.id_familia_id = producto_familia.id_producto_familia
		INNER JOIN producto_marca ON producto.id_marca_id = producto_marca.id_producto_marca
		INNER JOIN comprobante_venta ON factura.id_comprobante_venta_id = comprobante_venta.id_comprobante_venta
WHERE 
	detalle_factura.id_producto_id <> 0 AND comprobante_venta.mult_estadistica <> 0 AND factura.no_estadist = False
GROUP BY producto.id_marca_id
ORDER BY producto.id_marca_id

"""
