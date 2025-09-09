from django import template
import pprint
import re

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

@register.filter
def youtube_embed_url(url):
    """
    Convertit une URL YouTube normale en URL d'intégration
    """
    if not url:
        return url
    
    # Pattern pour youtube.com/watch?v=VIDEO_ID
    youtube_watch_pattern = r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
    # Pattern pour youtu.be/VIDEO_ID
    youtube_short_pattern = r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)'
    
    # Vérifier le format youtube.com/watch?v=
    match = re.search(youtube_watch_pattern, url)
    if match:
        video_id = match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Vérifier le format youtu.be/
    match = re.search(youtube_short_pattern, url)
    if match:
        video_id = match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Si ce n'est pas YouTube, retourner l'URL originale
    return url

@register.filter
def is_youtube_url(url):
    """
    Vérifie si l'URL est une URL YouTube
    """
    if not url:
        return False
    return 'youtube.com' in url or 'youtu.be' in url

# Ajoutez aussi le filtre split si vous voulez l'utiliser ailleurs
@register.filter
def split(value, delimiter):
    """
    Divise une chaîne selon un délimiteur
    """
    if not value:
        return []
    return value.split(delimiter)
