from django.conf.urls.defaults import *

urlpatterns = patterns( 'databrowser.views',
    (r'^(?P<idef>\d+)/$', 'init_restore' ),
    (r'^app/store_state/$', 'store_state' ),
    (r'^restore_state/$', 'restore_state' ),
    (r'^prepare_data/$', 'prepare_data' ),
    (r'^download/$', 'download_data' ),
    (r'^app/feedback/$', 'feedback_email' ),
    (r'^$', 'redirect' ),
    (r'^en/$', 'redirect_en' ),
    (r'^app/search/$', 'search_data' ),
    (r'^app/get_searched/$', 'get_searched_data' ),
    (r'^app/$', 'app_page' ),
)
