*.*
*.* Controla de ID ducpluicados en Facturacion
*.* 
CLOSE TABLES all
SET DELETED ON

STORE {01/11/24} to dDesde
STORE {30/11/24} to dHasta
STORE 0 TO nID

USE facturas ORDER id
SCAN FOR fecha>=dDesde AND fecha<=dHasta 
	IF facturas.id=nID
		?nID
	ENDIF 
	nID=facturas.id
ENDSCAN 
