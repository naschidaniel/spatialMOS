from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Pages

def page(request, url):
    """A function to output simple markdown pages."""

    def get_object():
        """The function to generate the database query."""
        try:
            return Pages.objects.values_list('slug', flat=True)
        except Pages.DoesNotExist:
            raise Http404
    
    if url in get_object():
        query = Pages.objects.get(slug=url)
        context = {
            'content': query,
            'title': query.title,
            'error': ''
        }
    else:
        query = get_object_or_404(Pages, slug='404')
        context = {
            'content': query,
            'title': query.title,
            'error': 'Ihre Anfrage konnte nicht bearbeitet werden.'
        }

    return render(request, 'pages/page.html', context)
