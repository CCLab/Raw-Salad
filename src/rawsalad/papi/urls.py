from django.conf.urls.defaults import *

# URLs for search: temporary update by Denis Kolokol, marked with comment "DK"


urlpatterns = patterns( 'papi.papi',
    (r'^$', 'get_formats' ),
    (r'^(?P<serializer>[a-z]+)/$', 'get_datasets' ),
    (r'^(?P<serializer>[a-z]+)/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/meta/$', 'get_datasets_meta' ),
    (r'^(?P<serializer>[a-z]+)/dataset/$', 'get_datasets' ),
    (r'^(?P<serializer>[a-z]+)/dataset/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/meta/$', 'get_datasets_meta' ),

    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/$', 'get_views' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/meta/$', 'get_views_meta' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/$', 'get_views' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/meta/$', 'get_views_meta' ),

    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/$', 'get_issues' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/meta/$', 'get_issues_meta' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/$', 'get_issues' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/meta/$', 'get_issues_meta' ),

    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/search/$', 'search_data' ), # DK
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/meta/$', 'get_metadata' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/tree/$', 'get_tree' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/$', 'get_data' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>[0-9a-zA-Z/\-]*)/meta/$', 'get_metadata' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>[0-9a-zA-Z/\-]*)/tree/$', 'get_tree' ),
    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>[0-9a-zA-Z/\-\+(AND|TO)\[\]]*)/$', 'get_data' ),
#    (r'^(?P<serializer>[a-z]+)/dataset/(?P<dataset_idef>\d+)/view/(?P<view_idef>\d+)/issue/(?P<issue>\d+)/(?P<path>([a-z]+/|[0-9\-\+(AND|TO)\[\]]*/)+)$', 'get_data' ),
)
