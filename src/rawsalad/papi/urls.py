from django.conf.urls.defaults import *
import papi

urlpatterns = patterns( '',
    (r'^$', 'get_datasets' ),
    (r'^meta/$', 'get_datasets_meta' ),
    (r'^dataset/$', 'get_datasets' ),
    (r'^dataset/meta/$', 'get_datasets_meta' ),
    
    (r'dataset/(?P<dataset>\d+)/$', 'get_views' ),
    (r'dataset/(?P<dataset>\d+)/meta/$', 'get_views_meta' ),
    (r'dataset/(?P<dataset>\d+)/view/$', 'get_views' ),
    (r'dataset/(?P<dataset>\d+)/view/meta/$', 'get_views_meta' ),
    
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/$', 'get_issues' ),
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/meta/$', 'get_issues_meta' ),
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/$', 'get_issues' ),
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/meta/$', 'get_issues_meta' ),
    
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/meta/$', 'get_data_meta' ),
    (r'dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/$', 'get_data' ),
)
