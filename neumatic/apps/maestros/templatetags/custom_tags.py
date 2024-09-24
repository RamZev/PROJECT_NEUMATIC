
from django import template

register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(value, arg):
    # print("Valor: ", value)
    # print("Atributo solicitado: ", arg)
    """
    Obtiene el valor de un atributo de un objeto.
    """
    try:
        return getattr(value, arg)
    except AttributeError:
        return None
    
# @register.filter(name='get_columna')
# def get_columna(field):
#     try:
#         return field.field.widget.attrs.get('columna')
#     except (AttributeError, KeyError):
#         return None

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter(name='get_columna')
def get_columna(field, field_name):
    extra_attrs = field.widget.attrs.get('extra_attrs', {})
    return extra_attrs.get('columna', 12)  # Si no se encuentra, se devuelve 12 por defecto
