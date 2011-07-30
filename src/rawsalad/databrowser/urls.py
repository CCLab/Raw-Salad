from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^store_state/$', 'store_state' ),
    (r'^id/(?P<idef>)[0-9]+/$', 'init_restore' ),
    (r'^restore_state/$', 'restore_state' ),
    (r'^prepare_data/$', 'prepare_data' ),
    (r'^download/$', 'download_data' ),
    (r'^app/feedback/$', 'feedback_email' ),
    (r'^$', 'redirect' ),
    (r'^app/search/$', 'search_data' ),
    (r'^app/get_searched/$', 'get_searched_data' ),
    (r'^app/$', 'app_page' ),
)
