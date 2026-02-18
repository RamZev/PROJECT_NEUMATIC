import base64
import xml.etree.ElementTree as ET
import json
import requests
import os
import ssl
import urllib3
import time
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AFIPAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx)

class FacturadorARCA:
    def __init__(self, homologacion=True):
        self.homologacion = homologacion
        self.entorno = "homologacion" if homologacion else "produccion"
        
        if homologacion:
            self.url_wsaa = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
            self.url_wsfe = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx"
        else:
            self.url_wsaa = "https://wsaa.afip.gov.ar/ws/services/LoginCms"
            self.url_wsfe = "https://servicios1.afip.gov.ar/wsfev1/service.asmx"

        self.session = requests.Session()
        self.session.mount("https://", AFIPAdapter())

    def realizar_request_afip(self, url, data=None, headers=None, metodo='POST'):
        try:
            response = self.session.post(url, data=data, headers=headers, timeout=60, verify=False)
            return response
        except Exception as e:
            print(f"❌ Error en conexión {self.entorno}: {str(e)[:100]}")
            raise

    def obtener_token_sign(self, cert_path, key_path, service="wsfe"):
        archivo_json = f"acceso_arca_{self.entorno}.json"
        
        if os.path.exists(archivo_json):
            with open(archivo_json, "r") as f:
                data = json.load(f)
                if datetime.now() < datetime.strptime(data["expira"], "%Y-%m-%d %H:%M:%S"):
                    print(f"✅ Token cargado desde caché ({self.entorno})")
                    return data["token"], data["sign"]

        print(f"🔐 Firmando TRA con certificado: {cert_path}")
        now = datetime.now() - timedelta(minutes=5)
        exp = now + timedelta(hours=12)
        tra = f"""<?xml version="1.0" encoding="UTF-8"?>
        <loginTicketRequest version="1.0">
          <header>
            <uniqueId>{int(now.timestamp())}</uniqueId>
            <generationTime>{now.strftime("%Y-%m-%dT%H:%M:%S")}</generationTime>
            <expirationTime>{exp.strftime("%Y-%m-%dT%H:%M:%S")}</expirationTime>
          </header>
          <service>{service}</service>
        </loginTicketRequest>""".encode('utf-8')

        with open(cert_path, "rb") as f: cert = x509.load_pem_x509_certificate(f.read())
        with open(key_path, "rb") as f: key = serialization.load_pem_private_key(f.read(), password=None)
        
        builder = pkcs7.PKCS7SignatureBuilder().set_data(tra).add_signer(cert, key, hashes.SHA256())
        cms = base64.b64encode(builder.sign(serialization.Encoding.DER, options=[])).decode('utf-8')

        soap = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsaa="http://wsaa.view.xfire.ao.do.afip.gov.ar">
          <soapenv:Body><wsaa:loginCms><wsaa:in0>{cms}</wsaa:in0></wsaa:loginCms></soapenv:Body>
        </soapenv:Envelope>"""
        
        resp = self.realizar_request_afip(self.url_wsaa, soap, {'Content-Type': 'text/xml;charset=UTF-8', 'SOAPAction': ''})
        root = ET.fromstring(resp.text)
        ticket_xml = root.find(".//{http://wsaa.view.xfire.ao.do.afip.gov.ar}loginCmsReturn").text
        ticket_root = ET.fromstring(ticket_xml)
        token, sign = ticket_root.find(".//token").text, ticket_root.find(".//sign").text

        with open(archivo_json, "w") as f:
            json.dump({"token": token, "sign": sign, "expira": exp.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=4)
        print(f"✅ Nuevo token guardado en {archivo_json}")
        return token, sign

    def obtener_proximo_numero(self, pv, tipo, token, sign, cuit):
        print(f"🔍 Consultando último comprobante autorizado ({self.entorno})...")
        soap = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <FECompUltimoAutorizado xmlns="http://ar.gov.afip.dif.FEV1/">
              <Auth><Token>{token}</Token><Sign>{sign}</Sign><Cuit>{cuit}</Cuit></Auth>
              <PtoVta>{pv}</PtoVta><CbteTipo>{tipo}</CbteTipo>
            </FECompUltimoAutorizado>
          </soap12:Body>
        </soap12:Envelope>"""
        
        headers = {'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': '"http://ar.gov.afip.dif.FEV1/FECompUltimoAutorizado"'}
        resp = self.realizar_request_afip(self.url_wsfe, soap, headers)
        root = ET.fromstring(resp.text)
        ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
        cbte_nro = root.find('.//ar:CbteNro', ns)
        
        if cbte_nro is not None and cbte_nro.text:
            ultimo = int(cbte_nro.text)
            return ultimo + 1, ultimo
        return 1, 0

    def enviar_solicitud_cae(self, xml_content):
        headers = {'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAESolicitar'}
        resp = self.realizar_request_afip(self.url_wsfe, xml_content, headers)
        return resp.text