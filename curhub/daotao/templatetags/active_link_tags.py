from django import template

register = template.Library()

@register.filter
def startswith_filter(value, arg):
    """
    Checks if the value starts with the argument.
    Usage: {{ request.path|startswith_filter:'/admin/' }}
    """
    return value.startswith(arg)
