from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def merge(prev, next):
    return f"{prev}-{next}"

@register.filter
def multiply(value, arg):
    """Multiplica dos valores."""
    return value * arg
