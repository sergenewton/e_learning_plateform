from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calcule le pourcentage de value par rapport à total
    Usage: {{ value|percentage:total }}
    """
    try:
        if total == 0:
            return 0
        return round((value / total) * 100)
    except (ValueError, TypeError):
        return 0