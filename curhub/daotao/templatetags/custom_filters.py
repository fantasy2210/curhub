from django import template

register = template.Library()

@register.filter
def sum_attribute(queryset, attribute_name):
    """
    Sums the value of a given attribute for all items in a queryset.
    Handles None values by treating them as 0.
    """
    total = 0
    for item in queryset:
        value = getattr(item, attribute_name, 0)
        if value is not None:
            total += value
    return total