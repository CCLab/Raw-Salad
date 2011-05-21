from django.conf.urls.defaults import *

urlpatterns = patterns( '',
    (r'^$', 'databrowser.views.redirect' ),
    (r'^app/$', 'databrowser.views.app_page' ),
)
