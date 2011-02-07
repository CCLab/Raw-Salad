from django.conf.urls.defaults import *

urlpatterns = patterns( '',
    (r'^$', 'databrowser.views.main_page' ),
)
