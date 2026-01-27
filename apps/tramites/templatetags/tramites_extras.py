from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Filtro personalizado para obtener un valor de un diccionario usando una clave.
    Uso: {{ datos_actuales|get_item:campo.nombre_tecnico }}
    """
    if dictionary is None:
        return ''
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''
