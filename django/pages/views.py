from django.shortcuts import render
from .models import Pages

from django.shortcuts import get_object_or_404

def page(request, url):
    """A function to output simple markdown pages."""
    
    if url in Pages.objects.values_list('slug', flat=True):
        query = Pages.objects.get(slug=url)
        context = {
            'content': query,
            'title': query.title,

        }
    else:
        query = get_object_or_404(Pages, slug='404')
        context = {
            'content': query,
            'title': query.title
        }

    return render(request, 'pages/page.html', context)