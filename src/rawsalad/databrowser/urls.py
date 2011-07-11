from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^prepare_data/$', 'prepare_data' ),
    (r'^download/$', 'download_data' ),
    (r'^$', 'redirect' ),
    (r'^app/search/$', 'search_data' ),
    (r'^app/$', 'app_page' ),
)
