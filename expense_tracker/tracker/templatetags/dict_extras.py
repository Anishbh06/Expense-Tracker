# tracker/templatetags/dict_extras.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve dictionary item by key."""
    return dictionary.get(key)
