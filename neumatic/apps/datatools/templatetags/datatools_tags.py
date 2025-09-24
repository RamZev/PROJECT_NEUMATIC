# apps\datatools\templatetags\datatools_tags.py
from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
	"""Para uso general - devuelve lista vacía"""
	return dictionary.get(key, [])


@register.filter
def get_dict_value(dictionary, key):
	"""Específico para valores de diccionario - devuelve cadena vacía"""
	return dictionary.get(key, '')