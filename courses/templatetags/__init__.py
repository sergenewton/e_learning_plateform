from django import template
import pprint

register = template.Library()

@register.filter
def debug(value):
    """Affiche les variables dans le template pour le débogage."""
    return pprint.pformat(value)
