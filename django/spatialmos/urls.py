"""spatialmos URL Configuration"""

from django.contrib import admin
from django.conf.urls import url
from django.urls import include, path
from pages.views import page

# Admin urls
urlpatterns = [
    path('admin/', admin.site.urls),
]

# App urls
urlpatterns += [
    path('', include('predictions.urls')),
    path('systemstatus', include('statusfiles.urls')),
    path('api/', include('api.urls')),
    url(r'^(?P<url>.*)/$', page)
    ]
