#!/usr/bin/python

"""
indexing collections in mongodb
type python collindex.py -h for instructions
"""

import getpass
import os
import optparse
import csv
import simplejson as json
from ConfigParser import ConfigParser

import pymongo
from pymongo import ASCENDING, DESCENDING

#-----------------------------
def get_db_connect(fullpath, dbtype):
    connect_dict= {}

    defaults= {
        'basedir': fullpath
    }

    cfg= ConfigParser(defaults)
    cfg.read(fullpath)
    connect_dict['host']= cfg.get(dbtype,'host')
    connect_dict['port']= cfg.getint(dbtype,'port')
    connect_dict['database']= cfg.get(dbtype,'database')
    connect_dict['username']= cfg.get(dbtype,'username')
    try:
        connect_dict['password']= cfg.get(dbtype,'password')
    except:
        connect_dict['password']= None

    return connect_dict

#-----------------------------
def ensure_indexes(db, md_coll):
    ns_items= db[md_coll].find({}, {'_id':0, 'ns':1, 'query':1, 'sort':1})
    for ns in ns_items:
        curr_ns= ns['ns']
        print "collection %s: \n...ensure indexes for \"idef\" and \"parent\"" % curr_ns
        db[curr_ns].ensure_index("idef")
        db[curr_ns].ensure_index("parent")
        print "...trying to ensure indexes for \"level\""
        try:
            print "...ensure indexes for \"level\""
            db[curr_ns].ensure_index("level")
        except:
            print "...no luck with \"level\" - no such key"

        sort_list_index= [] # sort
        try:
            cond_sort= ns['sort']
        except:
            cond_sort= None

        print "...trying to ensure indexes for sort keys"
        if cond_sort is not None:
            list_sort= [int(k) for k, v in cond_sort.iteritems()]
            list_sort.sort()
            for sort_key in list_sort:
                sort_list_index.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

            sort_index_name= "_".join([curr_ns,"sort_default"])
            print "...ensure index %s for sort keys %s" % (sort_index_name, sort_list_index)
            db[curr_ns].ensure_index(sort_list_index, name=sort_index_name)

        print "...trying to ensure indexes for query keys"
        query_list_index= [] # query
        try:
            cond_query= ns['query']
        except:
            cond_query= None

        if cond_query is not None:
            for nn in cond_query.items():
                print "...ensure index for query key %s" % nn[0]
                db[curr_ns].ensure_index(nn[0])
        else:
            print "...no luck with query - no keys"


#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options]") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--collect", action="store",dest='collection_name',help="collection name where metadata is stored")

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
    conn= get_db_connect(conf_filename, 'mongodb')
    conn_host= conn['host']
    conn_port= conn['port']
    conn_db= conn['database']

    try:
        connection= pymongo.Connection(conn_host, conn_port)
        db= connection[conn_db]
        print '...connected to the database', db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    conn_username= conn['username']
    conn_password= conn['password']
    if conn_password is None:
        conn_password = getpass.getpass()
    if db.authenticate(conn_username, conn_password) != 1:
        print 'Cannot authenticate to db, exiting now'
        exit()

    # data & meta-data collections
    if opts.collection_name is not None:
        coll_metadata= opts.collection_name
    else:
        print 'ERROR: No collection for metadata specified! Exiting now...'
        exit()
    
    ensure_indexes(db, coll_metadata)

    print "Done"
