from django.conf.urls.defaults import *

urlpatterns = patterns( '',
    (r'^$', 'databrowser.views.main_page' ),
    (r'^button_i/$', 'databrowser.views.button_i' ),     
    (r'^button_ii/$', 'databrowser.views.button_ii' ),     
    (r'^button_iii/$', 'databrowser.views.button_iii' ),     
)
