from django import template
from django.forms.widgets import Select, CheckboxInput, TextInput, Textarea, NumberInput, EmailInput, URLInput, DateInput, DateTimeInput, TimeInput

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class=""):
    """
    Adds CSS classes to a form field's widget.
    It preserves existing classes and adds new ones from the filter argument
    and based on the widget type.
    """
    if not hasattr(field, 'field'):
        return field
    widget = field.field.widget
    
    # Start with classes from the widget definition
    existing_classes = widget.attrs.get('class', '')
    
    # Add classes from the template filter argument
    all_classes = f'{existing_classes} {css_class}'.strip()
    
    # Add classes based on widget type for consistent styling
    if isinstance(widget, Select):
        if 'form-control' not in all_classes:
            all_classes = f'{all_classes} form-control'.strip()
        if 'select2' not in all_classes:
            all_classes = f'{all_classes} select2'.strip()
    elif isinstance(widget, CheckboxInput):
        if 'form-check-input' not in all_classes:
            all_classes = f'{all_classes} form-check-input'.strip()
    elif isinstance(widget, (TextInput, Textarea, NumberInput, EmailInput, URLInput, DateInput, DateTimeInput, TimeInput)):
        if 'form-control' not in all_classes:
            all_classes = f'{all_classes} form-control'.strip()
            
    return field.as_widget(attrs={'class': all_classes})
