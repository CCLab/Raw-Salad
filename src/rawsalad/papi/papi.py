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
import pymongo

import rsdbapi as rsdb


conn_schema= "md_budg_scheme"
nav_schema= "ms_nav"
conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/media/rawsdata.conf"

xml_header= "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

error_codes= {
    '10': 'ERROR: No such data!',
    '20': 'ERROR: No metadata specified!',
    '30': 'ERROR: Wrong request!',
    '31': 'ERROR: Scope +TO+ is applicable to the same level!',
    '32': 'ERROR: Wrong sequence in the scope +TO+!',
    '33': 'ERROR: Scope +TO+ should include only 2 elements!',
    '34': 'ERROR: Syntax error in scope definition!'
    }

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


def get_db_connect(dbtype):
    connect_dict= {}
    defaults= {
        'basedir': conf_filename
    }
    cfg= ConfigParser(defaults)

    cfg.read(conf_filename)

    success= True
    try: # check if we can read conf file
        connect_dict['host']= cfg.get(dbtype,'host')
    except:
        success= False

    if success: # all OK, fill the rest
        connect_dict['port']= cfg.getint(dbtype,'port')
        connect_dict['database']= cfg.get(dbtype,'database')
        connect_dict['username']= cfg.get(dbtype,'username')
        try:
            connect_dict['password']= cfg.get(dbtype,'password')
        except:
            # password must be instance of basestring
            connect_dict['password']= ''
    else: # can't read conf file - filling defaults
        connect_dict['host']= 'localhost'
        connect_dict['port']= 27017
        connect_dict['database']= 'rawsdoc00'
        connect_dict['username']= 'readonly'
        connect_dict['password']= ''

    return connect_dict


def get_mongo_db():
    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    dbase= connect[dsn['database']]
    dbase.authenticate(dsn['username'], dsn['password'])
    return dbase


def format_result(result, srz, rt_tag= None):
    if srz == 'json':
        res= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif srz == 'xml':
        # if rt_tag is None: # if root tag is not given, use 'request' key as a root tag
        #     rt_tag= result.pop('request') # i liked this idea very much
        rt_tag= 'result'
        res_raw= ET.tostring(dict2et(result, root_tag=rt_tag))
        res= "".join([ xml_header, res_raw ])
        mime_tp= "application/xml"
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


def get_metadata_full(ds_id, ps_id, iss, dbase):
    metadata_full= dbase[conn_schema].find_one(
        { 'dataset': ds_id, 'idef' : ps_id, 'issue': iss },
        { '_id' : 0 }
        )
    return metadata_full


def get_datasets(request, serializer, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= { 'request': 'dataset' }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives':0 })

    cursor_data= db[nav_schema].find(cond_query, nav_select_columns)

    if cursor_data.count() > 0:
        res= []
        for row in cursor_data:
            res.append(row)

        result['data']= res
        result['response']= 'OK'
        result['uri']= request.build_absolute_uri()
    else:
        result['response']= error_codes['10']

    out, mime_tp = format_result(result, serializer)

    return HttpResponse( out, mimetype=mime_tp )


def get_datasets_meta(request, serializer, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= { 'request': 'dataset' }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives':0 })

    cursor_data= db[nav_schema].find(cond_query, nav_select_columns)
    if cursor_data.count() > 0:
        result['response']= 'OK'
        result['metadata']= { 'count': cursor_data.count() }
        result['uri']= request.build_absolute_uri()
    else:
        result['response']= error_codes['10']

    out, mime_tp = format_result(result, serializer)

    return HttpResponse( out, mimetype=mime_tp )


def get_views(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'request': 'view',
        'dataset_id': int(dataset_idef)
        }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({
            'perspectives.idef':1,
            'perspectives.name':1,
            'perspectives.description':1,
            'perspectives.long_description':1
            })
    cond_query.update({ 'idef': int(dataset_idef) }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)
    if cursor_data is None:
        result['response']= error_codes['10']
    else:
        result['response']= 'OK'
        result['data']= cursor_data['perspectives']
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)

    return HttpResponse( out, mimetype=mime_tp )


def get_views_meta(request, serializer, dataset_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'request': 'view',
        'dataset_id': int(dataset_idef)
        }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({
            'perspectives.idef':1,
            'perspectives.name':1,
            'perspectives.description':1,
            'perspectives.long_description':1
            })
    cond_query.update({ 'idef': int(dataset_idef) }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)
    if cursor_data is None:
        result['response']= error_codes['10']
    else:
        result['response']= 'OK'
        result['metadata']= { 'count': len(cursor_data['perspectives']) }
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)

    return HttpResponse( out, mimetype=mime_tp )


def get_issues(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'request': 'issue',
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef)
        }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives.issues':1 })
    cond_query.update({ 'idef': int(dataset_idef),
        'perspectives': { '$elemMatch': { 'idef': int(view_idef) } } }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)
    if cursor_data is None:
        result['response']= error_codes['10']
    else:
        result['response']= 'OK'
        result['data']= cursor_data['perspectives'][int(view_idef)].pop('issues')
        result['uri']= request.build_absolute_uri()

    out, mime_tp = format_result(result, serializer)

    return HttpResponse( out, mimetype=mime_tp )


def get_issues_meta(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:
        db= rsdb.DBconnect("mongodb").dbconnect

    result= {
        'request': 'issue',
        'dataset_id': int(dataset_idef),
        'view_id': int(view_idef)
        }

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives':1 })
    cond_query.update({
        'idef': int(dataset_idef),
        'perspectives': { '$elemMatch': { 'idef': int(view_idef) } } }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)
    if cursor_data is None:
        result['response']= error_codes['10']
    else:
        result['response']= 'OK'
        result['metadata']= {'count': len(cursor_data['perspectives'][int(view_idef)]['issues']) }
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


def get_columns(meta_data, usr_def_cols):
    columns_list= {'_id':0} # _id is never returned
    columns_list.update(meta_data['aux']) # list of columns to be returned in any case
    if len(usr_def_cols) > 0:
        for clm in usr_def_cols: # list of user defined columns to be returned
            columns_list[clm]= 1
    else:
        md_columns= meta_data['columns'] # list of main columns to be returned
        for clm in md_columns:
            columns_list[clm['key']]= 1

    return columns_list


def get_sort_list(meta_data):
    sort_list= []
    try:
        cond_sort= meta_data['sort']
    except:
        cond_sort= None

    if cond_sort is not None:
        srt= [int(k) for k, v in cond_sort.iteritems()]
        srt.sort()
        for sort_key in srt:
            sort_list.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

    return sort_list


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
        result['response']= error_codes[userdef_query['error']]

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
        result['response']= error_codes[userdef_query['error']]

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
