import getpass
import pymongo
import json

import optparse
from ConfigParser import ConfigParser
from time import time

#-----------------------------
def getMongoConnect(fullpath):
    connect_dict= {}

    defaults= {
        'basedir': fullpath # at the moment - fictional dir, will be used later for locating log file
    }

    cfg= ConfigParser(defaults)
    cfg.read(fullpath)
    connect_dict['host']= cfg.get('mongodb','host')
    connect_dict['port']= int(cfg.get('mongodb','port'))
    connect_dict['database']= cfg.get('mongodb','database')
    connect_dict['username']= cfg.get('mongodb','username')

    return connect_dict
    

#-----------------------------
if __name__ == "__main__":
    # WARNING!!!
    # ADD CMD LINE OPTIONS - SEE budgin.py !!!
    # .conf file, conn_schema, perspective_id
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] schema_collection") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file (CSV)")
    cmdparser.add_option("-i", "--id", action="store", dest="persp_id", help="perspective id")

    opts, args = cmdparser.parse_args()

    conf_filename= opts.conf_filename
    if conf_filename is None:
        print 'No configuratuion file specified!'
        exit()

    try:
        f_temp= open(conf_filename, 'rb')
    except Exception as e:
        print 'Cannot open .conf file:\n %s\n' % e
        exit()

    # get connection details
    conn= getMongoConnect(conf_filename)
    conn_host= conn['host']
    conn_port= conn['port']
    conn_db= conn['database']
    conn_user= conn['username']

    try:
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[conn_db]
        print '...connected to the database', db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    if db.authenticate(conn_user, '') != 1:
        print 'Error when trying to authenticate, exiting now...'
        exit()

    conn_schema= args[0] #'md_budg_scheme'
    # django should give me these parameters
    perspective_id= int(opts.persp_id)

    full_data= {}

    # EXTRACT metadata
    cursor_metadata= db[conn_schema].find_one({ 'idef' : perspective_id}, { '_id' : 0 })
    full_data= cursor_metadata.copy()
    # get rid of useless schema keys
    if 'query' in full_data: full_data.pop('query')
    if 'ns' in full_data: full_data.pop('ns')
    if 'aux' in full_data: full_data.pop('aux')
    if 'sort' in full_data: full_data.pop('sort')
    if 'batchsize' in full_data: full_data.pop('batchsize')

    conn_coll= cursor_metadata['ns'] # collection name

    md_select_columns= {'_id':0} # _id is never returned
    cond_aux= cursor_metadata['aux'] # list of aux columns to be returned
    md_select_columns.update(cond_aux)
    md_columns= cursor_metadata['columns'] # list of main columns to be returned
    for clm in md_columns:
        md_select_columns[clm['key']]= 1

    cond_query= cursor_metadata['query'] # query conditions

    try: # batch size
        cursor_batchsize= cursor_metadata['batchsize']
    except:
        cursor_batchsize= 'default'

    cursor_sort= [] # sort
    try:
        cond_sort= cursor_metadata['sort']
    except:
        cond_sort= None

    if cond_sort is not None:
        list_sort= [int(k) for k, v in cond_sort.iteritems()]
        list_sort.sort()
        for sort_key in list_sort:
            cursor_sort.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

    # EXTRACT data (rows)
    if cursor_batchsize in ['default', None]:
        cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort)
    else:
        cursor_data= db[conn_coll].find(cond_query, md_select_columns, sort=cursor_sort).batch_size(cursor_batchsize)
    print cursor_data.count(), 'documents extracted'
    dt_rows= []
    for row in cursor_data:
        dt_rows.append(row)
    full_data['rows']= dt_rows

    filename_json= conn_coll+'.json'
    json_write= open(filename_json, 'w')
    print '...writing data to JSON file', filename_json
    print >>json_write, json.dumps(full_data, indent=4)
    json_write.close()
    print 'Done'
