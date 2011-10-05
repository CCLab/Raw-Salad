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
import re

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


def format_result(result, srz, httpresp= None, rt_tag= None):
    if httpresp is None:
        httpresp= 200    
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
        format_error= rsdb.Response().get_response(35)
        res= json.dumps( {
            "response": format_error["descr"],
            "request": srz
            }, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
        httpresp= format_error["httpresp"]
    return res, mime_tp, httpresp


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

    nav= rsdb.Navtree()
    data= nav.get_dataset(db)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response = format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def get_datasets_meta(request, serializer, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response = format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )


def get_views(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    data= nav.get_view(db, dataset_idef)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response = format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def get_views_meta(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db, dataset_idef)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response= format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def get_issues(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    data= nav.get_issue(db, dataset_idef, view_idef)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['data']= data
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response = format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def get_issues_meta(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    nav= rsdb.Navtree()
    count= nav.get_count(db, dataset_idef, view_idef)

    result= { 'request': nav.request, 'response': nav.response['descr'] }
    if nav.response['httpresp'] == 200:
        result['metadata']= { 'count': count }
        result['uri']= request.build_absolute_uri()

    out, mime_tp, http_response = format_result(result, serializer, nav.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def get_userdef_fields(rq, parm):
    """
    user defined list of fields
    format can be (with or without space):
      ?fields=[fieldX, fieldY]
      ?fields=fieldX, fieldY
    """
    clm_str= rq.GET.get(parm, '[]')
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
        path_elm_list= pth[pth.index('[')+1 : pth.index(']')].split('+AND+')
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
                    
                    if len(tmplst_from) > 1: # check one, but do for both (we know alredy that they are on the same level)
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

        if '/branch' in pth: # query based on regexp (brothers and parents of given idefs + all level 'a')
            lookup, i= "", 0
            for idef in idef_list:
                i += 1
                lookup_idef= build_idef_regexp( idef )

                lookup += "(%s)|" % lookup_idef
                if i == len(idef_list):
                    lookup= lookup[:-1] # cutting the last symbol | in case it's the end of list

            if len(idef_list) == 1: # single idef
                lookup= lookup[1:-1] # cutting ( and )

            qry_fin= re.compile(lookup, re.IGNORECASE)

        else: # plain list of elements
            qry_fin= { "$in": idef_list }

        return { "idef": qry_fin }    

    elif (not test_presence) and (not test_order) and (not test_count): # dealing with single idef
        if '/branch' in pth: # query based on regexp (brothers and parents of given idef + all level 'a')
            idef= pth[0:pth.index('/branch')]
            lookup= build_idef_regexp( path2query( idef )['idef'] )
            qry_fin= { 'idef' : re.compile(lookup, re.IGNORECASE) }
        else:
            qry_fin= path2query(pth)
        return qry_fin

    else: # ERROR
        return { "error": '34' } # otherwise it's a syntax error

def get_count(query, collection, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    return db[collection].find(query).count()

def build_idef_regexp( curr_idef ):
    """ build regexp quering collection """
    level_num= curr_idef.count('-')
    if level_num > 0: # deeper than 'a'
        idef_srch= curr_idef.rsplit('-', 1)[0]
        lookup_idef= "^%s\-\d+$" % idef_srch
        curr_idef= idef_srch
        level= 1
        while level < level_num:
            idef_srch= curr_idef.rsplit('-', 1)[0]
            lookup_idef += "|^%s\-\d+$" % idef_srch
            curr_idef= idef_srch
            level += 1
        lookup_idef += "|^([A-Z]|\d)+$"
    else: # just query the highest level
        lookup_idef= "^([A-Z]|\d)+$"

    return lookup_idef

def get_data(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue
        }

    httpresp_dict= {}
    userdef_query= parse_conditions(path)
    if 'error' in userdef_query: # already an error
        httpresp_dict= rsdb.Response().get_response(userdef_query['error'])
        result['response']= httpresp_dict['descr']
    else:
        userdef_fields= get_userdef_fields(request, 'fields')

        coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
        data= coll.get_data(db, dataset_idef, view_idef, issue)
        httpresp_dict= coll.response

        if httpresp_dict['httpresp'] == 200:
            result['data']= data
            result['count']= coll.count
            result['uri']= request.build_absolute_uri()

        if coll.warning:
            result['warning']= coll.warning

        result['response']= httpresp_dict['descr']
        result['request']= coll.request

        coll= None

    out, mime_tp, http_response = format_result(result, serializer, httpresp_dict['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )


def get_metadata(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue,
        }

    userdef_fields= get_userdef_fields(request, 'fields')
    userdef_query= {}
    if len(path) != 0:
        userdef_query.update(path2query(path))

    coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
    metadata= coll.get_metadata(db, dataset_idef, view_idef, issue)
    if coll.response['httpresp'] == 200:
        result['metadata']= metadata
        result['uri']= request.build_absolute_uri()

    if coll.warning:
        result['warning']= coll.warning

    result['response']= coll.response['descr']
    result['request']= coll.request

    out, mime_tp, http_response = format_result(result, serializer, coll.response['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )


def get_tree(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef),
        'issue': issue
        }

    httpresp_dict= {}
    userdef_query= parse_conditions(path)
    if 'error' in userdef_query: # already an error
        httpresp_dict= rsdb.Response().get_response(userdef_query['error'])
        result['response']= httpresp_dict['descr']
    else:
        userdef_fields= get_userdef_fields(request, 'fields')

        coll= rsdb.Collection(fields= userdef_fields, query= userdef_query)
        tree= coll.get_tree(db, dataset_idef, view_idef, issue)
        httpresp_dict= coll.response
        if httpresp_dict['httpresp'] == 200:
            result['tree']= tree
            result['uri']= request.build_absolute_uri()

        if coll.warning:
            result['warning']= coll.warning

        result['response']= httpresp_dict['descr']
        result['request']= coll.request

    out, mime_tp, http_response = format_result(result, serializer, httpresp_dict['httpresp'])
    return HttpResponse( out, mimetype=mime_tp, status=http_response )

def build_scope(dbase, dataset, view, issue):
    out, lst= [], []
    fieldict= { '_id':0, 'dataset': 1, 'idef': 1, 'issue': 1 }
    sortlist= [ ('dataset', 1), ('idef', 1), ('issue', 1) ]
    if dataset:
        if view:
            if issue: # dataset-view-issue
                specdict= { 'dataset': int(dataset), 'idef': int(view), 'issue': issue }
            else: # dataset-view-  all issues
                specdict= { 'dataset': int(dataset), 'idef': int(view) }
        else: # dataset-  all views and issues
            specdict ={ 'dataset': int(dataset) }
    else: # all datasets, views and issues
        specdict= None

    lst= dbase[rsdb.meta_src].find( spec= specdict, fields= fieldict, sort= sortlist )

    if lst.count() > 0: # gather elements into the list
        for elt in lst:
            out.append( '-'.join([ str(elt['dataset']), str(elt['idef']), elt['issue'] ]) )

    return out

def search_data(request, serializer, path='', db=None, **kwargs):
    result= { 'request': 'search for data' }

    query_str= request.GET.get('query', None) # THE search string
    lookup_fields= get_userdef_fields(request, 'lookup') # what fields to include to search

    strict= request.GET.get('strict', False) # strict?
    if str(strict).upper() in ['TRUE', 'T', 'YES', 'Y', 'TAK', '1']:
        strict= True
    else:
        strict= False

    if (query_str is None) or (query_str.strip() == ''):
        result['response']= rsdb.Response().get_response(36)["descr"]
    else:
        if db is None:
            db= rsdb.DBconnect("mongodb").dbconnect

        # cleaning user query
        query_str= query_str.strip()
        query_str= re.sub('\s+', ' ', query_str) # cleaning multiple spaces

        # optional args specifying what collections to search in
        dataset= kwargs.get('dataset_idef', None)
        view= kwargs.get('view_idef', None)
        issue= kwargs.get('issue', None)        
        scope_list= build_scope(db, dataset, view, issue)
        if len(scope_list) == 0: # ERROR! wrong conditions for search
            result['response']= rsdb.Response().get_response(37)["descr"]
        else:
            result.update( {
                'query': query_str,
                'uri': request.build_absolute_uri()
                } )

            if query_str is None:
                result['response']= rsdb.Response().get_response(36)["descr"]
            else:
                res= rsdb.Search()
                # # old search
                # result.update(
                #     res.search_data(
                #         db, qrystr= query_str, scope= scope_list, strict= strict, lookup= lookup_fields
                #         )
                #     )
                # result['response']= rsdb.Response().get_response(0)["descr"]

                # new search
                display_fields= get_userdef_fields(request, 'fields') # fields to display
                result.update(
                    res.search_text(
                        db, qrystr= query_str, scope= scope_list, strict= strict, display= display_fields
                        )
                    )
                result['response']= rsdb.Response().get_response(0)["descr"]                

    out, mime_tp, http_response = format_result(result, serializer, 200)
    return HttpResponse( out, mimetype=mime_tp, status=http_response )
