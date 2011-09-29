from django.conf.urls.defaults import patterns, url
from csv_upload.up.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    url(r'^$', home ),
    url(r'^upload/$', upload ),
    url(r'^save_metadata/$', save_metadata ),
    url(r'^save_advanced/$', save_advanced ),
)

urlpatterns += staticfiles_urlpatterns()
