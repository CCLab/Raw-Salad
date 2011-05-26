# -*- coding: utf-8 -*-

import pymongo
from ConfigParser import ConfigParser

conn_schema= "md_budg_scheme"
nav_schema= "ms_nav"
conf_filename= "/home/cecyf/www/projects/rawsalad/src/rawsalad/site_media/media/rawsdata.conf"


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
def get_metadata_full(ds_id, ps_id, is_id, dbase):
    """
    returns complete set of metadata (with "sort", "aux" and "query")
    """
    metadata_full= dbase[conn_schema].find_one(
        { 'dataset': ds_id, 'idef' : ps_id, 'issue': is_id },
        { '_id' : 0 }
        )
    return metadata_full



#-----------------------------
def get_metadata(dataset_id, perspective_id, issue_num):
    """
    returns metadata used for representation (without "sort", "aux" and "query")
    """

    md_ds= int(dataset_id)
    md_ps= int(perspective_id)
    md_is= str(issue_num)

    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    md_db= connect[dsn['database']]
    md_db.authenticate(dsn['username'], dsn['password'])

    # EXTRACT metadata
    mdata= get_metadata_full(md_ds, md_ps, md_is, md_db)
    keys_to_delete= ['sort', 'query', 'aux', 'batchsize']
    for k in keys_to_delete:
        if k in mdata:
            del mdata[k]

    return mdata



#-----------------------------
def extract_docs(dataset_id, perspective_id, issue_num, query_aux):
    """
    extracts data for given dataset and perspective
    query_aux represents special cases
    (for example, extract only highest level or children of a parent)
    """

    ds= int(dataset_id)
    ps= int(perspective_id)
    iss= str(issue_num)
    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    db= connect[dsn['database']]
    db.authenticate(dsn['username'], dsn['password'])

    # EXTRACT metadata
    metadata_full= get_metadata_full(ds, ps, iss, db)
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



#-----------------------------
def extract_nav(keys_aux=None, query_aux=None):
    """
    extracts navigation data
    keys_aux represents special cases like extract only dataset without perspectives
    query_aux represents special cases like extract specified dataset with perspectives
    """

    # connection details
    dsn= get_db_connect('mongodb')
    connect= pymongo.Connection(dsn['host'], dsn['port'])
    db= connect[dsn['database']]
    db.authenticate(dsn['username'], dsn['password'])

    if keys_aux is None:
        keys_aux= {}
    if query_aux is None:
        query_aux= {}

    nav_select_columns= {'_id':0} # _id is never returned
    nav_select_columns.update(keys_aux)

    cond_query= {} # query conditions
    cond_query.update(query_aux) # additional query, depends on the call

    cursor_data= db[nav_schema].find(cond_query, nav_select_columns)

    out= []
    for row in cursor_data:
        out.append(row)

    return out

