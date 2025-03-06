-- Consulta original para VFP
SELECT 
		Detven.compro,
		Detven.letra,
		Detven.numero,
		Facturas.fecha,
		Facturas.cliente,
		Clientes.nombre,
		Detven.codigo,
		Lista.nombre AS descripcion,
		Lista.codfabrica,
		Lista.medida,
		Detven.cantidad,
		Detven.precio,
		Detven.descuento,
		Detven.total*Codven.mult_sto*-1 AS total,
		Facturas.sucursal,
		Clientes.sucursal AS succliente
 FROM facturas, clientes, codven, detven, lista
 WHERE Detven.id = Facturas.id
   AND Detven.compro = Codven.compro   AND Detven.codigo = Lista.codigo   AND Facturas.cliente = Clientes.codigo
   AND (Detven.compro$"RF*RD*RT*RM*DM*MR*MD*MS*MM" = .T.   AND Facturas.estado = " "
   AND Clientes.vendedor BETWEEN ?nDesVen AND ?nHasVen
   AND Facturas.cliente BETWEEN ?nDesCli AND ?nHasCli AND Codven.mult_ven = 0)
 ORDER BY Clientes.nombre, Facturas.fecha, Detven.numero

-- Filtros generales:
-- Codven.mult_ven = 0 AND Facturas.estado = " " 

-- Filtros dinámicos:
-- Clientes.vendedor BETWEEN ?nDesVen AND ?nHasVen
-- Facturas.cliente BETWEEN ?nDesCli AND ?nHasCli
-- Facturas.sucursal = ?mSUCURSAL
-- Clientes.sucursal = ?mSUCURSAL
 
 
 