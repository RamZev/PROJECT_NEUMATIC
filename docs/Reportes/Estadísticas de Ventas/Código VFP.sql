PUBLIC nDesdeMarca,nHastaMarca

dDesde=This.txtdesFecha.Value
dHasta=This.txtHasFecha.Value
nDesdeMarca=This.rangonumeros1.nDesde
nHastaMarca=This.rangonumeros1.nHasta

WAIT WINDOWS "Aguardar un Momento " NOWAIT

CREA CURSOR T2 (marca N(3), codigo N(6), articulo N(4), modelo N(4), cantidad N(10,2), unidad N(3), total N(12,2), nombre C(40), cliente N(6), cai C(15))
IF This.rdbSucursal.Value = 1
	SELECT 
		detven.compro,
		detven.letra,
		detven.numero,
		facturas.fecha,
		detven.codigo,
		lista.articulo,
		lista.modelo,
		lista.marca,
		lista.nombre,
		lista.unidad,
		detven.cantidad,
		detven.precio,
		detven.descuento,
		facturas.cliente,
		lista.codfabrica 
	FROM detven,facturas,lista,codven ;
	WHERE detven.id=facturas.id.AND.detven.codigo=lista.codigo.AND.detven.compro=codven.compro ;
		.AND.detven.codigo#0.AND.codven.mult_stad#0
		.AND.facturas.fecha BETWEEN dDesde.AND.dHasta .AND. !facturas.noestadist ;
	INTO CURSOR T1 READWRITE 
	ORDER BY 6 articulo, 7 modelo, 8 marca, 5 codigo
ELSE
	SELECT 
		detven.compro,
		detven.letra,
		detven.numero,
		facturas.fecha,
		detven.codigo,
		lista.articulo,
		lista.modelo,
		lista.marca,
		lista.nombre,
		lista.unidad,
		detven.cantidad,
		detven.precio,
		detven.descuento,
		facturas.cliente,
		lista.codfabrica 
	FROM detven,facturas,lista,codven ;
	WHERE detven.id=facturas.id.AND.detven.codigo=lista.codigo.AND.detven.compro=codven.compro ;
		.AND.detven.codigo#0.AND.codven.mult_stad#0
		.AND.facturas.fecha BETWEEN dDesde.AND.dHasta .AND.!facturas.noestadist .AND.facturas.sucursal=sucursal.id ;
	INTO CURSOR T1 READWRITE 
	ORDER BY 6,7,8,5
ENDIF 
---------------------------------------------------
IF This.chkCliente.Value 
	DELETE FOR cliente # Thisform.txtCliente.Value 
ENDIF 
SELE t1
SET RELA TO compro INTO codven
GO TOP
DO CASE
	CASE This.rdbGrupo.Value=1
		This.ctrlimpresion1.cTituloreporte="Estadistica de Ventas por Productos"
		STORE t1.cliente TO m.cliente
		STORE t1.codigo TOm.codigo
		STORE t1.articulo TO m.articulo
		STORE t1.modelo TO m.modelo
		STORE t1.marca TO m.marca
		STORE t1.codfabrica TO m.cai
		STORE 0 TO m.total,m.cantidad
		SCAN
			IF t1.codigo#m.codigo
				INSERT INTO T2 FROM MEMVAR
				STORE t1.cliente  TO m.cliente
				STORE t1.codigo   TO m.codigo
				STORE t1.articulo TO m.articulo
				STORE t1.modelo   TO m.modelo
				STORE t1.marca    TO m.marca
				STORE t1.nombre   TO m.nombre
				STORE t1.codfabrica TO m.cai
				STORE 0 TO m.total,m.cantidad
			ENDIF
			m.cantidad=m.cantidad+(t1.cantidad*codven.mult_stad)
			m.total=m.total+((t1.cantidad*t1.precio)+(t1.cantidad*t1.precio*t1.descuento/100))*codven.mult_stad
			SELE T1
		ENDSCAN

	CASE This.rdbGrupo.Value=2
		This.ctrlimpresion1.cTituloreporte="Estadistica de Ventas por Familia"
		INDEX ON STR(articulo,4)+STR(marca,3) TO t1aux
		GO TOP
		STORE t1.cliente TO m.cliente
		STORE t1.articulo TO m.articulo
		STORE t1.marca  TO m.marca
		STORE 0 TO m.total,m.cantidad
		SCAN
			IF t1.articulo#m.articulo.OR.t1.marca#m.marca
				INSERT INTO T2 FROM MEMVAR
				STORE t1.cliente TO m.cliente
				STORE t1.articulo TO m.articulo
				STORE t1.marca  TO m.marca
				STORE 0 TO m.total,m.cantidad
			ENDIF
			m.cantidad=m.cantidad+(t1.cantidad*codven.mult_stad)
			m.total=m.total+((t1.cantidad*t1.precio)+(t1.cantidad*t1.precio*t1.descuento/100))*codven.mult_stad
			SELE T1
		ENDSCAN

	CASE This.rdbGrupo.Value=3
		This.ctrlimpresion1.cTituloreporte="Estadistica de Ventas por Modelos"
		GO TOP
		STORE t1.cliente TO m.cliente
		STORE t1.modelo TO m.modelo
		STORE t1.marca  TO m.marca
		STORE 0 TO m.total,m.cantidad
		SCAN
			IF t1.modelo#m.modelo.OR.t1.marca#m.marca
				INSERT INTO T2 FROM MEMVAR
				STORE t1.cliente TO m.cliente
				STORE t1.modelo TO m.modelo
				STORE t1.marca  TO m.marca
				STORE 0 TO m.total,m.cantidad
			ENDIF
			m.cantidad=m.cantidad+(t1.cantidad*codven.mult_stad)
			m.total=m.total+((t1.cantidad*t1.precio)+(t1.cantidad*t1.precio*t1.descuento/100))*codven.mult_stad
			SELE T1
		ENDSCAN

	CASE This.rdbGrupo.Value=4
		This.ctrlimpresion1.cTituloreporte="Estadistica de Ventas por Marca"
		INDEX ON marca TO t1aux
		GO TOP
		STORE t1.cliente TO m.cliente
		STORE t1.marca TO m.marca
		STORE t1.codigo TO m.codigo
		STORE 0 TO m.total,m.cantidad
		SCAN
			IF t1.marca#m.marca
				INSERT INTO T2 FROM MEMVAR
				STORE t1.cliente TO m.cliente
				STORE t1.codigo TO m.codigo
				STORE t1.marca  TO m.marca
				STORE 0 TO m.total,m.cantidad
			ENDIF
			m.cantidad=m.cantidad+(t1.cantidad*codven.mult_stad)
			m.total=m.total+((t1.cantidad*t1.precio)+(t1.cantidad*t1.precio*t1.descuento/100))*codven.mult_stad
			SELE T1
		ENDSCAN
ENDCASE
INSERT INTO T2 FROM MEMVAR
SELE T2
IF This.rdbOrden.Value=1
	INDEX ON cantidad TAG cantidad DESC
	SUM cantidad TO This.nTotal
ELSE
	INDEX ON total TAG total DESC
	SUM TOTAL TO This.nTotal
ENDIF
DO CASE 
	CASE This.rdbGrupo.Value=1
		SET RELATION TO codigo INTO lista, articulo INTO articulo, modelo INTO modelos
	CASE This.rdbGrupo.Value=2
		SET RELA TO articulo INTO articulo, marca INTO marcas
	CASE This.rdbGrupo.Value=3
		SET RELA TO modelo INTO modelos, marca INTO marcas
	CASE This.rdbGrupo.Value=4
		SET RELA TO marca INTO marcas
ENDCASE 
REPLACE t2.unidad WITH lista.unidad ALL 
WAIT CLEAR
