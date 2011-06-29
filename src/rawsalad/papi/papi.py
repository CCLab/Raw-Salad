# -*- coding: utf-8 -*-
"""
project: Raw Salad
function: public API to data and meta-data
requirements: mongod, conf file (see conf_filename)
"""

from django.http import HttpResponse
from django.utils import simplejson as json
from django.core import serializers

import xml.etree.cElementTree as ET

from ConfigParser import ConfigParser

import rsdbapi as rsdb


conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/media/rawsdata.conf"

xml_header= "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

level_list= ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']


def dict2et(xml_dict, root_tag='result', list_names=None):
    if not list_names:
        list_names = {}
    root = ET.Element(root_tag)
    _convert_dict_to_xml_recurse(root, xml_dict, list_names)

    return root


def _convert_dict_to_xml_recurse(parent, dict_item, list_names):
    # XML conversion
    # WARNING! can't convert bare lists

    assert not isinstance(dict_item, list)

    if isinstance(dict_item, dict):
        for (tag, child) in dict_item.iteritems():
            if isinstance(child, list):
                list_elem = ET.Element(tag)
                parent.append(list_elem)
                for listchild in child:
                    elem = ET.Element(list_names.get(tag, 'item'))
                    list_elem.append(elem)
                    _convert_dict_to_xml_recurse(elem, listchild, list_names)
            else:
                elem = ET.Element(tag)
                parent.append(elem)
                _convert_dict_to_xml_recurse(elem, child, list_names)
    elif not dict_item is None:
        parent.text = unicode(dict_item)


def format_result(result, srz, rt_tag= None):
    if srz == 'json':
        res= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif srz == 'xml':
        # if rt_tag is None: # if root tag is not given, use 'request' key as a root tag
        #     rt_tag= result.pop('request') # ehh.. i liked this idea very much
        rt_tag= 'result'
        res_raw= ET.tostring(dict2et(result, root_tag=rt_tag))
        res= "".join([ xml_header, res_raw ])
        mime_tp= "application/xml"
    else: # error: format missing (like ../api/dataset/ instead of /api/<format>/dataset/)
        res= json.dumps( {
            "response": rsdb.Error().throw_error(35),
            "request": srz
            }, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    return res, mime_tp


def path2query(path_str):
    out_query= {}

    if len(path_str) != 0:
        path_list= path_str.rsplit('/')
        last_elt= path_list[len(path_list)-1]
        if last_elt in level_list: # last element is a sign of level
            if path_list[len(path_list)-1] == 'a': # level 'a' has no parents
                out_query['level']= path_list[len(path_list)-1]
            else:
                out_query['parent']= path_list[len(path_list)-2] # the one before last is a parent
        else:
            out_query['idef']= path_list[len(path_list)-1] # the last elt is current idef
    return out_query


def get_formats(request):
    result= {'formats': ['json', 'xml']}
    result['uri']= request.build_absolute_uri()
    return HttpResponse( json.dumps( result ), 'application/json' )


def get_datasets(request, serializer, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    print dir( rsdb )
    nav= rsdb.Navtree()
    data= nav.get_dataset(db)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )

def get_datasets_meta(request, serializer, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )


def get_views(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    data= nav.get_view(db, dataset_idef)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )

def get_views_meta(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db, dataset_idef)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )

def get_issues(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    data= nav.get_issue(db, dataset_idef, view_idef)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )

def get_issues_meta(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db, dataset_idef, view_idef)

    result= { 'request': nav.request, 'response': nav.response }
    if result['response'] == 'OK':
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )

def get_userdef_fields(rq):
    """
    user defined list of fields
    format can be (with or without space):
      ?fields=[fieldX, fieldY]
      ?fields=fieldX, fieldY
    """
    clm_str= rq.GET.get('fields', '[]')
    out_tmp, out_list= [], []
    if clm_str != '[]':
        clm_str= clm_str.replace(' ', '')
        if '[' and ']' in clm_str:
            out_tmp= clm_str[1:-1].split(',')
        else:
            out_tmp= clm_str.split(',')

    for elm in out_tmp: # check for empty elements
        if len(elm) > 0:
            out_list.append(elm)
    
    return out_list

def parse_conditions(pth):
    path_elm_list= []
    idef_list= []

    test_presence= '[' and ']' in pth
    test_order= pth.find('[') < pth.find(']')
    test_count= (pth.count('[') + pth.count(']') == 2)

    if test_presence and test_order and test_count:
        path_elm_list= pth[pth.index('[')+1:-1].split('+AND+')
        if len(path_elm_list) > 0:
            for elm in path_elm_list:
                scope_list= elm.split('+TO+')

                if len(scope_list) == 1: # no scope, just adding it to the list of idefs
                    idef_list.append(elm)

                elif len(scope_list) == 2: # there is a correctly defined scope
                    idef_from, idef_to= scope_list[0], scope_list[1]

                    tmplst_from= idef_from.split('-')
                    tmplst_to= idef_to.split('-')

                    if len(tmplst_from) != len(tmplst_to): # ERROR!
                        return { "error": '31' } # 'to' and 'from' are from different levels
                    
                    if len(tmplst_from) > 1: # check one, but do for both, as it's alredy checked if they are on the same level
                        try:
                            last_num_from= int(tmplst_from[-1])
                            last_num_to= int(tmplst_to[-1])

                            base_from= "-".join(tmplst_from[:-1])
                            base_to= "-".join(tmplst_to[:-1])
                        except: # ERROR!
                            return { "error": '34' } # syntax error like [...+AND] or [+TO+2...]                        
                    else:
                        try:
                            last_num_from= int(tmplst_from[0])
                            last_num_to= int(tmplst_to[0])
                        except:
                            return { "error": '34' } # syntax error like [...+2+6+AND...]                        

                    if last_num_to < last_num_from: # ERROR!
                        return { "error": '32' } # 'to' is less than 'from'

                    last_num_curr= last_num_from
                    while last_num_curr <= last_num_to:
                        if len(tmplst_from) > 1:
                            idef_list.append("-".join([base_from, str(last_num_curr)]))
                        else:
                            idef_list.append(str(last_num_curr))
                        last_num_curr += 1
                        

                elif len(scope_list) > 2: # ERROR!
                    return { "error": '33' } # incorrectly defined scope!

        return { "idef": { "$in": idef_list } }

    elif (not test_presence) and (not test_order) and (not test_count):
        return path2query(pth) # well, then it means we're dealing with single idef

    else: # ERROR
        return { "error": '34' } # otherwise it's a syntax error

def get_count(query, collection, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    return db[collection].find(query).count()


def get_data(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue
        }

    userdef_query= parse_conditions(path)
    if 'error' in userdef_query: # already an error
        result['response']= rsdb.Error().throw_error(userdef_query['error'])

    else:
        userdef_fields= get_userdef_fields(request)

        coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
        data= coll.get_data(db, dataset_idef, view_idef, issue)
        if coll.response == 'OK':
            result['data']= data
            result['count']= coll.count
            result['uri']= request.build_absolute_uri()

        if coll.warning:
            result['warning']= coll.warning

        result['response']= coll.response
        result['request']= coll.request

        coll= None

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )


def get_metadata(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue,
        }

    userdef_fields= get_userdef_fields(request)
    userdef_query= {}
    if len(path) != 0:
        userdef_query.update(path2query(path))

    coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
    metadata= coll.get_metadata(db, dataset_idef, view_idef, issue)
    if coll.response == 'OK':
        result['metadata']= metadata
        result['uri']= request.build_absolute_uri()

    if coll.warning:
        result['warning']= coll.warning

    result['response']= coll.response
    result['request']= coll.request

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )


def get_tree(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue,
        }

    userdef_query= parse_conditions(path)
    if 'error' in userdef_query: # already an error
        result['response']= rsdb.Error().throw_error(userdef_query['error'])

    else:
        userdef_fields= get_userdef_fields(request)

        coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
        tree= coll.get_tree(db, dataset_idef, view_idef, issue)
        if coll.response == 'OK':
            result['tree']= tree
            result['uri']= request.build_absolute_uri()

        if coll.warning:
            result['warning']= coll.warning

        result['response']= coll.response
        result['request']= coll.request

    out, mime_tp = format_result(result, serializer)
    return HttpResponse( out, mimetype=mime_tp )
