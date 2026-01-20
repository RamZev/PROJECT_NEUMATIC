# utils/afip_simple.py
import requests
import xml.etree.ElementTree as ET
from django.core.cache import cache
import time
import logging

logger = logging.getLogger(__name__)

class AFIPSimpleClient:
    """
    Cliente mínimo para AFIP - Solo lo esencial
    """
    
    def __init__(self, token, sign, cuit, ambiente="homologacion"):
        self.token = token
        self.sign = sign
        self.cuit = cuit
        self.wsfe_url = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx" if ambiente == "homologacion" else "https://servicios1.afip.gov.ar/wsfev1/service.asmx"
    
    def obtener_ultimo_autorizado(self, pto_vta, cbte_tipo):
        """
        Consulta el último número autorizado por AFIP
        """
        # Construir XML de consulta
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <FECompUltimoAutorizado xmlns="http://ar.gov.afip.dif.FEV1/">
            <Auth>
                <Token>{self.token}</Token>
                <Sign>{self.sign}</Sign>
                <Cuit>{self.cuit}</Cuit>
            </Auth>
            <PtoVta>{pto_vta}</PtoVta>
            <CbteTipo>{cbte_tipo:03d}</CbteTipo>
        </FECompUltimoAutorizado>
    </soap:Body>
</soap:Envelope>"""
        
        # Enviar
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        response = requests.post(self.wsfe_url, data=xml, headers=headers, timeout=30)
        
        # Parsear respuesta
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://ar.gov.afip.dif.FEV1/'}
        
        cbte_nro = root.find('.//ns:CbteNro', ns)
        if cbte_nro is not None:
            return int(cbte_nro.text)
        else:
            # Si no hay comprobantes, devolver 0
            return 0
    
    def emitir_factura(self, xml_factura):
        """
        Envía factura a AFIP
        """
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        response = requests.post(
            self.wsfe_url,
            data=xml_factura.encode('utf-8'),
            headers=headers,
            timeout=30
        )
        return response.content