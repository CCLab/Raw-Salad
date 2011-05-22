# -*- coding: utf-8 -*-
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
def dict2et(xmldict, roottag='data', listnames=None):
    if not listnames:
        listnames = {}
    root = ET.Element(roottag)
    _convert_dict_to_xml_recurse(root, xmldict, listnames)

    return root

#-----------------------------
def _convert_dict_to_xml_recurse(parent, dictitem, listnames):
    """Helper Function for XML conversion."""
    # we can't convert bare lists
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        for (tag, child) in sorted(dictitem.iteritems()):
            if isinstance(child, list):
                listelem = ET.Element(tag)
                parent.append(listelem)
                for listchild in child:
                    elem = ET.Element(listnames.get(tag, 'item'))
                    listelem.append(elem)
                    _convert_dict_to_xml_recurse(elem, listchild, listnames)
            else:
                elem = ET.Element(tag)
                parent.append(elem)
                _convert_dict_to_xml_recurse(elem, child, listnames)
    elif not dictitem is None:
        parent.text = unicode(dictitem)

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

    out= []
    for row in cursor_data:
        out.append(row)

    return HttpResponse( json.dumps( out ))

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
    out= { 'count': cursor_data.count() }
    return HttpResponse( json.dumps( out ))

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

    out= cursor_data['perspectives']

    return HttpResponse( json.dumps( out ))

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

    out= { 'count': len(cursor_data['perspectives']) }

    return HttpResponse( json.dumps( out ))

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

    nav_select_columns.update({ 'perspectives.issue':1 })
    cond_query.update({ 'idef': int(dataset_idef) }) # query conditions

    cursor_data= db[nav_schema].find_one(cond_query, nav_select_columns)

    out= cursor_data['perspectives'][int(view_idef)]

    return HttpResponse( json.dumps( out ))

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

    out= {}
    out['count']= len(cursor_data['perspectives'][int(view_idef)]['issue'])

    return HttpResponse( json.dumps( out ))

#-----------------------------
def get_data(request, serializer, dataset_idef, view_idef, issue, path='', db=None):
    if db is None:
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])        

    # EXTRACT metadata
    metadata_full= get_metadata_full(int(dataset_idef), int(view_idef), int(issue), db)
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
        out= { 'data': None, 'response': 'No such data' }
    else:
        out= { 'data': dt, 'metadata': metadata_full, 'response': 'OK' }

    if serializer == 'json':
        result= json.dumps( out )
        mime_tp= "application/json"
    elif serializer == 'xml':
        result= ET.tostring(dict2et(out))
        mime_tp= "text/xml"
    resp = HttpResponse()

    return HttpResponse( result, mimetype=mime_tp )


#-----------------------------
def get_metadata(request, serializer, dataset_idef, view_idef, issue, path, db=None):
    if db is None:
        # connection details
        dsn= get_db_connect('mongodb')
        connect= pymongo.Connection(dsn['host'], dsn['port'])
        db= connect[dsn['database']]
        db.authenticate(dsn['username'], dsn['password'])        

    # EXTRACT metadata
    metadata_full= get_metadata_full(int(dataset_idef), int(view_idef), int(issue), db)

    if metadata_full is None:
        out= { 'metadata': None, 'response': 'No such data' }
    else:
        # delete useless columns
        useless_keys= ['ns', 'aux', 'batchsize', 'sort', 'query', 'explorable']
        for curr in useless_keys:
            if curr in metadata_full:
                del metadata_full[curr]

        out= { 'metadata': metadata_full, 'response': 'OK' }

    return HttpResponse( json.dumps( out ))



#examples:
# http://localhost:8000/api/json/dataset/0/view/1/issue/2011/
# http://localhost:8000/api/xml/dataset/0/view/1/issue/2011/
