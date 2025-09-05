from django import template
import pprint

register = template.Library()

@register.filter
def debug(value):
    """Affiche les variables dans le template pour le débogage."""
    return pprint.pformat(value)

@register.filter
def has_attr(obj, attr_name):
    """Vérifie si un objet a un attribut donné."""
    return hasattr(obj, attr_name)

@register.filter
def get_attr(obj, attr_name):
    """Obtient un attribut d'un objet."""
    return getattr(obj, attr_name, None)

@register.filter
def in_list(value, arg):
    """Vérifie si une valeur est dans une liste."""
    return value in arg

@register.filter
def get_item(dictionary, key):
    """Get the value from a dictionary using its key."""
    return dictionary.get(key, None)
