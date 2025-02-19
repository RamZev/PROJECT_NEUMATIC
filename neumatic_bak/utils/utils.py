# neumatic\utils\utils.py
import re
from datetime import date, datetime
from decimal import Decimal


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