SELECT ltVentasDet
STORE 0 TO nCant, nID
SCAN
	IF nID#ltVentasDet.id
		nCant = nCant + 1
		nID = ltVentasDet.id
	ENDIF 
	
ENDSCAN 
?nCant