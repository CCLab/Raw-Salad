from django.conf.urls.defaults import *

urlpatterns = patterns( 'papi.papi',
#    (r'^$', 'get_datasets' ),
#    (r'^meta/$', 'get_datasets_meta' ),
#    (r'^dataset/$', 'get_datasets' ),
#    (r'^dataset/meta/$', 'get_datasets_meta' ),
    
    (r'dataset/(?P<dataset_idef>\d+)/$', 'get_views' ),
#    (r'dataset/(?P<dataset_idef>\d+)/meta/$', 'get_views_meta' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/$', 'get_views' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/meta/$', 'get_views_meta' ),
    
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/$', 'get_issues' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/meta/$', 'get_issues_meta' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/$', 'get_issues' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/meta/$', 'get_issues_meta' ),
    
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/meta/$', 'get_metadata' ),
#    (r'dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/$', 'get_data' ),
)
