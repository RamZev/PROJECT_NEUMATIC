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

def numero_a_letras(numero):
	"""
	Convierte un número decimal a su representación en letras con formato para céntimos.
	Ejemplos:
	 123.45 → "ciento veintitrés con 45/100"
	 79245.01 → "setenta y nueve mil doscientos cuarenta y cinco con 01/100"
	 100.00 → "cien con 00/100"
	
	Args:
		numero (float/int): Número a convertir
		
	Returns:
		str: Representación del número en letras con formato XX/100
	"""
	# Verificar si es negativo
	if numero < 0:
		return "menos " + numero_a_letras(abs(numero))
	
	# Separar parte entera y decimal
	entero = int(numero)
	decimal = int(round((numero - entero) * 100))
	
	# Conversión de la parte entera
	if entero == 0:
		resultado_entero = "cero"
	elif entero < 100:
		resultado_entero = convertir_decenas(entero)
	elif entero < 1000:
		resultado_entero = convertir_centenas(entero)
	elif entero < 1000000:
		resultado_entero = convertir_miles(entero)
	elif entero < 1000000000000:
		resultado_entero = convertir_millones(entero)
	else:
		resultado_entero = "número demasiado grande"
	
	# Formatear siempre con dos dígitos para los decimales
	decimal_str = f"{decimal:02d}"
	return f"{resultado_entero} con {decimal_str}/100"

def convertir_decenas(numero):
	"""Convierte números entre 1-99 a letras"""
	unidades = ["", "uno", "dos", "tres", "cuatro", "cinco", 
				"seis", "siete", "ocho", "nueve"]
	especiales = ["diez", "once", "doce", "trece", "catorce", "quince",
				 "dieciséis", "diecisiete", "dieciocho", "diecinueve"]
	decenas = ["", "diez", "veinte", "treinta", "cuarenta", "cincuenta",
			  "sesenta", "setenta", "ochenta", "noventa"]
	
	if numero < 10:
		return unidades[numero]
	elif 10 <= numero < 20:
		return especiales[numero - 10]
	else:
		d = numero // 10
		u = numero % 10
		if u == 0:
			return decenas[d]
		else:
			return f"{decenas[d]} y {unidades[u]}"

def convertir_centenas(numero):
	"""Convierte números entre 100-999 a letras"""
	if numero == 100:
		return "cien"
	centenas = ["", "ciento", "doscientos", "trescientos", "cuatrocientos",
			   "quinientos", "seiscientos", "setecientos", "ochocientos",
			   "novecientos"]
	c = numero // 100
	resto = numero % 100
	if resto == 0:
		return centenas[c]
	else:
		return f"{centenas[c]} {convertir_decenas(resto)}"

def convertir_miles(numero):
	"""Convierte números entre 1000-999999 a letras"""
	miles = numero // 1000
	resto = numero % 1000
	
	if miles == 1:
		resultado_mil = "mil"
	else:
		resultado_mil = f"{numero_a_letras(miles).replace(' con 00/100', '')} mil"
	
	if resto == 0:
		return resultado_mil
	else:
		return f"{resultado_mil} {convertir_decenas(resto) if resto < 100 else convertir_centenas(resto)}"

def convertir_millones(numero):
	"""Convierte números entre 1000000-999999999 a letras"""
	millones = numero // 1000000
	resto = numero % 1000000
	
	if millones == 1:
		resultado_millon = "un millón"
	else:
		resultado_millon = f"{numero_a_letras(millones).replace(' con 00/100', '')} millones"
	
	if resto == 0:
		return resultado_millon
	else:
		return f"{resultado_millon} {numero_a_letras(resto).replace(' con 00/100', '')}"