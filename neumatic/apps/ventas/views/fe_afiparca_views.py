from afip import Afip
from zeep import Client
from zeep.exceptions import Fault
import xml.etree.ElementTree as ET


def fe_dummy(environment="homologacion"):
    """
    Verifica el estado de la infraestructura de AFIP mediante el método FEDummy.
    
    Args:
        environment (str): 'homologacion' o 'produccion' para seleccionar el entorno.
    
    Returns:
        dict: Diccionario con los estados de AppServer, DbServer, AuthServer y un indicador de éxito.
              En caso de error, retorna el mensaje de error.
    """
    # Configuración del entorno
    wsdl_url = (
        "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL" if environment == "homologacion"
        else "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"
    )
    
    result = {"success": False, "AppServer": None, "DbServer": None, "AuthServer": None, "error": None}
    
    try:
        # Crear cliente SOAP
        client = Client(wsdl_url)
        
        # Llamar al método FEDummy
        response = client.service.FEDummy()
        
        # Procesar la respuesta
        result.update({
            "success": True,
            "AppServer": response.AppServer,
            "DbServer": response.DbServer,
            "AuthServer": response.AuthServer
        })
        
        # Validar estados
        all_ok = all(status == "OK" for status in [response.AppServer, response.DbServer, response.AuthServer])
        if not all_ok:
            result["warning"] = "Uno o más servidores no están en estado OK"
        
        # Imprimir resultado (para compatibilidad con el código original)
        print("Estado de la infraestructura de AFIP:")
        print(f"AppServer: {response.AppServer}")
        print(f"DbServer: {response.DbServer}")
        print(f"AuthServer: {response.AuthServer}")
        if "warning" in result:
            print(f"Advertencia: {result['warning']}")
            
    except Fault as fault:
        result["error"] = f"Error SOAP: Código {fault.code}, Mensaje: {fault.message}"
        print(f"Error SOAP: {fault.message}")
    except Exception as e:
        result["error"] = f"Error al consumir el servicio: {str(e)}"
        print(f"Error: {str(e)}")
    
    return result