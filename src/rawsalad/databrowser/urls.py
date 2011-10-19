from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^(?P<idef>\d+)/$', 'init_restore' ),
    (r'^store_state/$', 'store_state' ),
    (r'^restore_state/$', 'restore_state' ),
    (r'^prepare_data/$', 'prepare_data' ),
    (r'^download/$', 'download_data' ),
    (r'^feedback/$', 'feedback_email' ),
    (r'^search/$', 'search_data' ),
    (r'^get_searched/$', 'get_searched_data' ),
    (r'^$', 'app_page' ),
)
