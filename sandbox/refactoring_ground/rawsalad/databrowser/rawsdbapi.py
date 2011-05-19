# -*- coding: utf-8 -*-

import pymongo
from ConfigParser import ConfigParser

conn_schema= 'md_budg_scheme'
conf_filename= "/Users/deniskolokol/dev/rawsalad/repo/rawsdata.conf"
#global conf_filename= "/home/cecyf/www/projects/rawsalad/rawsdata.conf" 


#-----------------------------
def get_db_connect(dbtype):
    connect_dict= {}
    defaults= {
        'basedir': conf_filename
    }
    cfg= ConfigParser(defaults)
    cfg.read(conf_filename)
    connect_dict['host']= cfg.get(dbtype,'host')
    connect_dict['port']= cfg.getint(dbtype,'port')
    connect_dict['database']= cfg.get(dbtype,'database')
    connect_dict['username']= cfg.get(dbtype,'username')
    try:
        connect_dict['password']= cfg.get(dbtype,'password')
    except:
        connect_dict['password']= '' # password must be an instance of basestring

    return connect_dict



#-----------------------------
def get_metadata_full(ds_id, ps_id, dbase):
    # returns complete set of metadata (with "sort", "aux" and "query")
    metadata_full= dbase[conn_schema].find_one({ 'dataset': ds_id, 'idef' : ps_id }, { '_id' : 0 })
    return metadata_full



#-----------------------------
def get_metadata(dataset_id, perspective_id):
    # returns metadata used for representation (without "sort", "aux" and "query")
    #
    # WARNING! there should be optional parameter - connection
    # calling this func from views.py without connection means that we have to do get_db_connect first
    # but if connection is given, just use it for extraction

    ds= int(dataset_id)
    ps= int(perspective_id)

    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    db= connect[dsn['database']]
    db.authenticate(dsn['username'], dsn['password'])

    # EXTRACT metadata
    md= get_metadata_full(ds, ps, db)
    keys_to_delete= ['sort', 'query', 'aux', 'batchsize']
    for k in keys_to_delete:
        if k in md:
            del md[k]

    return md


#-----------------------------
def extract_docs(dataset_id, perspective_id, query_aux):
    # extracts initial data - level 'a' of a given collection

    ds= int(dataset_id)
    ps= int(perspective_id)
    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    db= connect[dsn['database']]
    db.authenticate(dsn['username'], dsn['password'])

    # EXTRACT metadata
    metadata_full= get_metadata_full(ds, ps, db)
    conn_coll= metadata_full['ns'] # collection name

    md_select_columns= {'_id':0} # _id is never returned
    cond_aux= metadata_full['aux'] # list of aux columns to be returned
    md_select_columns.update(cond_aux)
    md_columns= metadata_full['columns'] # list of main columns to be returned
    for clm in md_columns:
        md_select_columns[clm['key']]= 1

    try: # batch size
        cursor_batchsize= metadata_full['batchsize']
    except:
        cursor_batchsize= 'default'

    cursor_sort= [] # sort
    try:
        cond_sort= metadata_full['sort']
    except:
        cond_sort= None

    if cond_sort is not None:
        list_sort= [int(k) for k, v in cond_sort.iteritems()]
        list_sort.sort()
        for sort_key in list_sort:
            cursor_sort.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

    cond_query= metadata_full['query'] # query conditions
    cond_query.update(query_aux) # additional query, depends on the call

    # EXTRACT data (rows)
    if cursor_batchsize in ['default', None]:
        cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort)
    else:
        cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort).batch_size(cursor_batchsize)

    out= []
    for row in cursor_data:
        out.append(row)

    return out



# aa= {'parent':'15'}
# for ii in extract_docs(1, 1, aa):
#     print ii
