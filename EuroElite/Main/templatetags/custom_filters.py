from django import template

register = template.Library()

@register.filter
def miles_chilenos(value):
    """
    Formatea números con separador de miles estilo chileno (puntos).
    Ejemplo: 20000 -> 20.000
    """
    try:
        valor = int(value)
        return f"{valor:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value
