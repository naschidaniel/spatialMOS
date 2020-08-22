"""Template filters for spatialMOS"""

from django.template import Library

register = Library()

@register.filter(name='addclass')
def addclass(field, class_attr):
    """A function to add css classes to form fields"""
    return field.as_widget(attrs={'class': class_attr})
