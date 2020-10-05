"""The context pre processors for the spatialMOS project"""

from django.conf import settings

def custom_context(request):
    """A function to pass variables that are valid in all templates."""
    return_dict = {
        'DEBUG': settings.DEBUG, 
        'LASTCOMMIT': settings.LASTCOMMIT,
        'UPDATETIME': settings.UPDATETIME, 
        }
    return return_dict