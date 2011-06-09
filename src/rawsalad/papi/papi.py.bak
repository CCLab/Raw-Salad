# -*- coding: utf-8 -*-
"""
project: Raw Salad
function: public API to data and meta-data
requirements: mongod, conf file (see conf_filename)

to-do:
- standartization of the headers for both XML and JSON
- stardatization of the errors and processing
- bare list conversion to XML instead of converting them to dict
"""



from django.http import HttpResponse
from django.utils import simplejson as json
from django.core import serializers

import xml.etree.cElementTree as ET

from ConfigParser import ConfigParser
import pymongo

conn_schema= "md_budg_scheme"
nav_schema= "ms_nav"
conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/media/rawsdata.conf"

#-----------------------------
def dict2et(xml_dict, root_tag='result', list_names=None):
    if not list_names:
        list_names = {}
    root = ET.Element(root_tag)
    _convert_dict_to_xml_recurse(root, xml_dict, list_names)

    return root

#-----------------------------
def _convert_dict_to_xml_recurse(parent, dict_item, list_names):
    # XML conversion
    # WARNING! can't convert bare lists (yet)

    assert not isinstance(dict_item, list)

    if isinstance(dict_item, dict):
        for (tag, child) in sorted(dict_item.iteritems()):
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

#-----------------------------
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

#-----------------------------
def get_metadata_full(ds_id, ps_id, iss, dbase):
    metadata_full= dbase[conn_schema].find_one(
        { 'dataset': ds_id, 'idef' : ps_id, 'issue': iss },
        { '_id' : 0 }
        )
    return metadata_full


#-----------------------------
def get_formats(request):
    return HttpResponse( json.dumps( {'formats': ['json', 'xml']} ), 'application/json' )


#-----------------------------
def get_datasets(request, serializer, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives':0 })

    cursor_data= db[nav_schema].find(cond_query, nav_select_columns)

    res= []
    for row in cursor_data:
        res.append(row)
    result= {'datasets':res}

    if serializer == 'json':
        out= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='data'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_datasets_meta(request, serializer, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives':0 })

    cursor_data= db[nav_schema].find(cond_query, nav_select_columns)
    result= { 'count': cursor_data.count() }

    if serializer == 'json':
        out= json.dumps( {'datasets': result }, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='datasets'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_views(request, serializer, dataset_idef, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])
        

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

    result= { 'views': cursor_data['perspectives'] }

    if serializer == 'json':
        out= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='dataset'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_views_meta(request, serializer, dataset_idef, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])
        

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

    result= {'count': len(cursor_data['perspectives']) }

    if serializer == 'json':
        out= json.dumps( {'views': result}, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='views'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_issues(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])
        

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives.issues':1 })
    cond_query.update({ 'idef': int(dataset_idef) }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)

    result= cursor_data['perspectives'][int(view_idef)]

    if serializer == 'json':
        out= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='issues'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_issues_meta(request, serializer, dataset_idef, view_idef, db=None):
    if db is None:    
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])
        

    # initial params
    nav_select_columns= {'_id':0} # _id is never returned
    cond_query= {} # query conditions

    nav_select_columns.update({ 'perspectives.issue':1 })
    cond_query.update({ 'idef': int(dataset_idef) }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)

    result= {}
    result['count']= len(cursor_data['perspectives'][int(view_idef)]['issues'])

    if serializer == 'json':
        out= json.dumps( { 'issues': result }, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag='issues'))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_data(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])        

    # EXTRACT metadata
    metadata_full= get_metadata_full(int(dataset_idef), int(view_idef), str(issue), db)
    if metadata_full is None:
        dt= []
    else:
        conn_coll= metadata_full.pop('ns') # collection name

        md_select_columns= {'_id':0} # _id is never returned
        cond_aux= metadata_full.pop('aux') # list of aux columns to be returned
        md_select_columns.update(cond_aux)
        md_columns= metadata_full['columns'] # list of main columns to be returned
        for clm in md_columns:
            md_select_columns[clm['key']]= 1

        try: # batch size
            cursor_batchsize= metadata_full.pop('batchsize')
        except:
            cursor_batchsize= 'default'

        cursor_sort= [] # sort
        try:
            cond_sort= metadata_full.pop('sort')
        except:
            cond_sort= None

        if cond_sort is not None:
            list_sort= [int(k) for k, v in cond_sort.iteritems()]
            list_sort.sort()
            for sort_key in list_sort:
                cursor_sort.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

        cond_query= metadata_full.pop('query') # query conditions
        if path == '':
            query_aux= { 'level': 'a' }
        else:
            path_list= path.rsplit('/', 1)
            parent_idef= path_list[1] # last idef in the call
            query_aux= { 'parent': parent_idef }

        cond_query.update(query_aux) # additional query, depends on the path argument
        out= {'query':cond_query, 'columns':md_select_columns, 'sort':cursor_sort}

        # EXTRACT data (rows)
        if cursor_batchsize in ['default', None]:
            cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort)
        else:
            cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort).batch_size(cursor_batchsize)

        dt= []
        for row in cursor_data:
            dt.append(row)

    if len(dt) == 0:
        result= { 'data': None, 'response': 'No such data' }
    else:
        result= { 'data': dt, 'metadata': metadata_full, 'response': 'OK' }

    if serializer == 'json':
        out= json.dumps( result, ensure_ascii=False, indent=4 )
        # result= json.dumps( out )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag=metadata_full['name']))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )

#-----------------------------
def get_metadata(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])        

    # EXTRACT metadata
    metadata_full= get_metadata_full(int(dataset_idef), int(view_idef), str(issue), db)

    if metadata_full is None:
        result= { 'metadata': None, 'response': 'No such data' }
    else:
        # delete useless columns
        useless_keys= ['ns', 'aux', 'batchsize', 'sort', 'query', 'explorable']
        for curr in useless_keys:
            if curr in metadata_full:
                del metadata_full[curr]

        result= { 'metadata': metadata_full, 'response': 'OK' }

    if serializer == 'json':
        out= json.dumps( result, ensure_ascii=False, indent=4 )
        mime_tp= "application/json"
    elif serializer == 'xml':
        out= ET.tostring(dict2et(result, root_tag=metadata_full['name']))
        mime_tp= "text/xml"

    return HttpResponse( out, mimetype=mime_tp )
