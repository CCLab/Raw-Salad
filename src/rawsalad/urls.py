from django.conf.urls.defaults import *
from django.conf import settings

## ---> Static linkage to libs to be done
urlpatterns = patterns('',
    (r'^site_media/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^', include('rawsalad.databrowser.urls')),
    (r'^api', include('rawsalad.papi.urls')),
)
