from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^$', 'main_page' ),
    (r'^choose/col/(?P<col_nr>\d+)/$', 'choose_page' ),
    (r'^browse/$', 'browse_page' ),
    (r'^', 'other_page' ),
)
