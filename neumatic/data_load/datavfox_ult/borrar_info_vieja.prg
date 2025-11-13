CLOSE ALL 
CLEAR ALL 
CLEAR 
CLOSE TABLES ALL 

SET EXCLUSIVE ON 
SET DELETED ON
SET DATE DMY 
SET STRICTDATE TO 0

USE facturas ORDER id IN 0
USE detven   ORDER id IN 0 
USE codven   ORDER codigo IN 0 
USE stockCliente ORDER id IN 0 
USE movStock ORDER id IN 0 
*------------------------------------- Creo un tabla con el detalle de movimiento de stock para sacarlo del detalle de ventas, para no tener problemas en las migraciones de Django
SELECT detven
COPY TO movStockDetalle.dbf FOR detven.compro='MI'
USE movStockDetalle IN 0


dFecha = {31/12/2023}

*--------------------------------- Borro info vieja de Movimientos de Stock y Guardo detalle de movStocvk en nueva tabla
SELECT movStock
DELETE FOR fecha<=dFecha
PACK 
SELECT movStockDetalle
SET RELATION TO id INTO movStock
DELETE FOR EMPTY(movStock.id) 
PACK
	
*--------------------------------- Creo Saldo anterior de clientes para traslado de cuentas como Ajustes
SELECT cliente,sum(total*codven.mult_cli) as saldo ;
	FROM facturas, codven ;
	WHERE facturas.compro=codven.codigo AND fecha<=dFecha and codven.mult_cli#0 AND condicion=2;
	GROUP BY cliente ;
	INTO CURSOR T1

SELECT facturas
GO BOTTOM 
nID=id
nNro=0

SELECT T1
BROWSE FOR SALDO#0 NODELETE NOAPPEND NOMODIFY 

IF MESSAGEBOX("QUIERE PROCEDER AL AJUSTE DE CUENTAS",4+32+256,"VERIFICAR")=6
	*--------------------------------- Agrego los saldos de clientes a la fecha de borrado como ajustes de cuenta
	SELECT t1
	SCAN FOR saldo#0
		nID=nID+1
		nNro=nNro+1
		INSERT INTO facturas (compro,letra,numero,fecha,cliente,condicion,total,sucursal,id,observa) ;
			VALUES ("ND","X",nNro,dFecha+1,t1.cliente,2,t1.saldo,1,nID,"AJUSTE DE CUENTA A LA FECHA")
		SELECT t1
	ENDSCAN 
	
	*--------------------------------- Borro los comprobantes viejos
	SELECT FACTURAS
	DELETE FOR fecha<=dFecha
	PACK

	*--------------------------------- Borro el detalle de Ventas exeeptuando los Mov.Internos de Stock
	SELECT detven
	SET RELATION TO id INTO facturas
	DELETE FOR EMPTY(facturas.id)          &&AND compro#'MI' 
	PACK 

	*--------------------------------- Borro stock Cliente viejo
	SELECT stockCliente
	SET RELATION TO id INTO facturas
	DELETE FOR EMPTY(facturas.id) 
	PACK 

*!*		*--------------------------------- Borro info vieja de Movimientos de Stock
*!*		SELECT movStock
*!*		DELETE FOR fecha<=dFecha
*!*		SELECT detven 
*!*		SET RELATION TO id INTO movStock
*!*		DELETE FOR EMPTY(movStock.id) AND compro='MI' 
*!*		PACK 
ENDIF 

CLOSE TABLES ALL 
USE FACTURAS 
SORT TO FACT_ORD ON fecha

CLOSE TABLES ALL 
USE facturas EXCLUSIVE 
ZAP 
APPEND FROM fact_ord 

CLOSE TABLES ALL 

