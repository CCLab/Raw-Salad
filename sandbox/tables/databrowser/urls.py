from django.conf.urls.defaults import *

urlpatterns = patterns( '',
    (r'^$', 'databrowser.views.main_page' ),
    (r'^first/$', 'databrowser.views.first_table' ),     
    (r'^second/$', 'databrowser.views.second_table' ), 
)
