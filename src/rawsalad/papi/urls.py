from django.conf.urls.defaults import *
import pubapi

urlpatterns = patterns( '',
    (r'^api/$', 'get_datasets' ),
    (r'^api/meta/$', 'get_datasets_meta' ),
    (r'^api/dataset/$', 'get_datasets' ),
    (r'^api/dataset/meta/$', 'get_datasets_meta' ),
    
    (r'api/dataset/(?P<dataset>\d+)/$', 'get_views' ),
    (r'api/dataset/(?P<dataset>\d+)/meta/$', 'get_views_meta' ),
    (r'api/dataset/(?P<dataset>\d+)/view/$', 'get_views' ),
    (r'api/dataset/(?P<dataset>\d+)/view/meta/$', 'get_views_meta' ),
    
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/$', 'get_issues' ),
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/meta/$', 'get_issues_meta' ),
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/$', 'get_issues' ),
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/meta/$', 'get_issues_meta' ),
    
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/meta/$', 'get_data_meta' ),
    (r'api/dataset/(?P<dataset>\d+)/view/(?P<view>\d+)/issue/(?P<issue>\d+)/(?P<path>\.*)/$', 'get_data' ),
)
