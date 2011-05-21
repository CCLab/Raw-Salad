from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^$', 'redirect' ),
    (r'^app/$', 'app_page' ),
    (r'^api/$', include('papi.urls')),
)
