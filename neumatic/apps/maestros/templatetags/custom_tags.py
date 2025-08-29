# neumatic\apps\maestros\templatetags\custom_tags.py
from django import template
from decimal import Decimal
import locale
from ..models.base_models import ProductoEstado

register = template.Library()


@register.filter(name='get_attribute')
def get_attribute(value, arg):
	"""
	Obtiene el valor de un atributo de un objeto.
	"""
	try:
		return getattr(value, arg)
	except AttributeError:
		return None

	
@register.filter(name='get_item')
def get_item(dictionary, key):
	return dictionary.get(key, None)


@register.filter(name='get_columna')
def get_columna(field, field_name):
	extra_attrs = field.widget.attrs.get('extra_attrs', {})
	return extra_attrs.get('columna', 12)  # Si no se encuentra, se devuelve 12 por defecto


@register.filter
def get_type(value):
	""" Devuelve el tipo de valor en formato string."""
	return type(value).__name__


@register.filter
def formato_es_ar(value):
	"""
	Formatea un número con el formato de Argentina:
	Separador de miles: punto (.)
	Separador decimal: coma (,)
	Compatible con float y Decimal.
	"""
	try:
		#-- Configura el locale para números en es_AR.
		locale.setlocale(locale.LC_NUMERIC, 'es_AR.UTF-8')
		
		#-- Convierte a float si el valor es Decimal.
		if isinstance(value, Decimal):
			value = float(value)
		
		#-- Formatea con separadores de miles y 2 decimales.
		return locale.format_string('%.2f', value, grouping=True)
	except (ValueError, TypeError):
		#-- Devuelve el valor sin formatear si no es un número válido.
		return value


@register.filter
def formato_es_ar_entero(value):
    """
    Formatea un número entero con el formato de Argentina:
    - Separador de miles: punto (.)
    - Sin decimales
    - Compatible con int, float y Decimal.
    """
    try:
        # Configura el locale para números en es_AR
        locale.setlocale(locale.LC_NUMERIC, 'es_AR.UTF-8')
        
        # Convierte a float si es Decimal y luego a int
        if isinstance(value, Decimal):
            value = int(float(value))
        elif isinstance(value, float):
            value = int(value)
            
        # Formatea con separadores de miles y sin decimales
        return locale.format_string('%d', value, grouping=True)
    except (ValueError, TypeError):
        # Devuelve el valor sin formatear si no es un número válido
        return value


@register.simple_tag
def get_color_estado(nombre_estado):
    try:
        return ProductoEstado.objects.get(nombre_producto_estado=nombre_estado).color
    except ProductoEstado.DoesNotExist:
        return '#FFFFFF'  # Color por defecto si no existe
