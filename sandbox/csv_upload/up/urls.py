from django.conf.urls.defaults import patterns, url
from csv_upload.up.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', home ),
    url(r'^upload/$', upload ),
)

urlpatterns += staticfiles_urlpatterns()
