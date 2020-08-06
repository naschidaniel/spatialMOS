from django.conf import settings

def custom_context(request):
    """A function to pass variables that are valid in all templates."""
    return {'LASTCOMMIT': settings.LASTCOMMIT}