from django import template
from django.forms.widgets import Select, CheckboxInput, TextInput, Textarea, NumberInput, EmailInput, URLInput, DateInput, DateTimeInput, TimeInput

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class=""): # Default to empty string
    widget = field.field.widget
    final_css_class = css_class.strip() # Start with the provided class, stripped

    if isinstance(widget, Select):
        if not final_css_class: # If no class was provided, use form-select
            final_css_class = 'form-select'
        else: # If a class was provided, append form-select
            final_css_class += ' form-select'
    elif isinstance(widget, CheckboxInput):
        if not final_css_class: # If no class was provided, use form-check-input
            final_css_class = 'form-check-input'
        else: # If a class was provided, append form-check-input
            final_css_class += ' form-check-input'
    # For other common input types, apply form-control if no class is provided
    elif isinstance(widget, (TextInput, Textarea, NumberInput, EmailInput, URLInput, DateInput, DateTimeInput, TimeInput)):
        if not final_css_class:
            final_css_class = 'form-control'
    # For any other widget type not explicitly handled, if no class was provided, default to form-control
    elif not final_css_class:
        final_css_class = 'form-control'
        
    return field.as_widget(attrs={'class': final_css_class.strip()})
