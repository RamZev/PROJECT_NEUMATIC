# neumatic\utils\utils.py
import re, locale, unicodedata
from datetime import date, datetime
from decimal import Decimal
from django.forms.models import model_to_dict


def es_numero_valido(valor):
	"""Verifica si un string es un número decimal válido."""
	return bool(re.fullmatch(r"-?\d+(\.\d+)?", valor))  # Acepta "10", "-5.5", "3.14"


def serializar_datos(datos):
	"""Convierte datos no serializables a formatos compatibles con JSON para guardarlos en la sesión."""
	if isinstance(datos, Decimal):
		return str(datos)  # Convertir Decimal a str
	elif isinstance(datos, (date, datetime)):
		return datos.isoformat()  # Convertir date/datetime a str
	elif isinstance(datos, list):
		return [serializar_datos(item) for item in datos]  # Recursivo para listas
	elif isinstance(datos, dict):
		return {k: serializar_datos(v) for k, v in datos.items()}  # Recursivo para dicts
	return datos  # Si no es un tipo especial, devolver el valor tal cual


def deserializar_datos(datos):
	"""Restaura los datos serializados desde la sesión a sus tipos originales."""
	if isinstance(datos, str):
		if es_numero_valido(datos):  # Verifica si es un número válido antes de convertir
			return Decimal(datos)
		try:
			return datetime.fromisoformat(datos)  # Intentar convertir a datetime
		except ValueError:
			try:
				return date.fromisoformat(datos)  # Intentar convertir a date
			except ValueError:
				return datos  # Si falla todo, devolver como string
	elif isinstance(datos, list):
		return [deserializar_datos(item) for item in datos]
	elif isinstance(datos, dict):
		return {k: deserializar_datos(v) for k, v in datos.items()}
	return datos


def serializar_queryset(queryset):
	return [model_to_dict(obj) for obj in queryset]


def formato_argentino(valor):
    return locale.format_string('%.2f', valor, grouping=True)


def format_date(date_value):
	"""Helper para formatear fechas en formato dd/mm/yyyy."""
	if not date_value:
		return ""
	
	if isinstance(date_value, str):
		try:
			return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
		except ValueError:
			return date_value
	else:
		return date_value.strftime("%d/%m/%Y")


def normalizar(nombre):
    #-- Normaliza los caracteres Unicode (descompone acentos en caracteres base + acento).
    nombre_normalizado = unicodedata.normalize('NFKD', nombre)
    
    #-- Elimina los caracteres diacríticos (acentos, diéresis, etc.).
    nombre_sin_acentos = ''.join([c for c in nombre_normalizado if not unicodedata.combining(c)])
    
    #-- Reemplaza caracteres específicos que pueden causar problemas.
    reemplazos = {
        'ñ': 'n',
        'Ñ': 'N',
        ' ': '_',  #-- Opcional: reemplazar espacios por guiones bajos.
    }
    
    #-- Aplica los reemplazos personalizados.
    for original, reemplazo in reemplazos.items():
        nombre_sin_acentos = nombre_sin_acentos.replace(original, reemplazo)
    
    #-- Elimina cualquier otro carácter que no sea alfanumérico, guión o punto.
    nombre_limpio = re.sub(r'[^\w\-.]', '', nombre_sin_acentos)
    
    return nombre_limpio