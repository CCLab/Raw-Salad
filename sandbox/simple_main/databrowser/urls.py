from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^$', 'main_page' ),
    (r'^choose/$', 'choose_view' ),
)
