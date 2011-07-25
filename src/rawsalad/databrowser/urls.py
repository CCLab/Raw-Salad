from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^prepare_data/$', 'prepare_data' ),
    (r'^download/$', 'download_data' ),
    (r'^feedback/$', 'feedback_email' ),
    (r'^$', 'redirect' ),
    (r'^app/search/$', 'search_data' ),
    (r'^app/get_searched/$', 'get_searched_data' ),
    (r'^app/$', 'app_page' ),
)
