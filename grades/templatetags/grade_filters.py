from django import template
import math

register = template.Library()

@register.filter
def trunc2(value):
    """Trunca un número a 2 decimales SIN redondear."""
    try:
        v = float(value)
        return f"{math.trunc(v * 100) / 100:.2f}"
    except (ValueError, TypeError):
        return value
