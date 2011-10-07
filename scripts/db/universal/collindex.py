#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import re

# fields to exclude from full-text search
# WARNING! that should somehow be indicated in the metadata!!!
exclude_fields= [
    'idef', 'idef_sort',
    'parent', 'parent_sort',
    'level', 'type',
    'numer', 'czesc', 'paragrafy', 'pozycja',
    'numer-umowydecyzji', 'os-priorytetowa-kod', 'dziaanie-kod', 'poddziaanie-kod', 'nip-beneficjenta', 'kod-pocztowy', 'ostatni-wniosek-o-patnosc-dla-najbardziej-aktualnej-umowyaneksu','projekt-zakonczony-wniosek-o-patnosc-koncowa','data-podpisania-umowyaneksu', 'data-utworzenia-w-ksi-simik-07-13-umowyaneksu'
    ]
exclude_words= ['i', 'a', 'lub', 'w', 'o', 'z', 'za', 'u', 'do', 'nad', 'na', 'dla', 'bez', 'przy', 'do', 'ku', 'mimo', 'śród', 'przez', 'po', 'pod', 'przez', 'między']

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

def build_keyword_list(collection, fields):

    kwd_key= '_keywords'

    coll_data= db[collection].find() # all data!

    for doc in coll_data:
        kwd_list= []
        for field in fields:

            # conditions under which we create list of keywords
            is_proc= 'processable' in field
            is_string= field['type'] == 'string'
            is_not_excl= field['key'] not in exclude_fields

            if is_string and is_proc and is_not_excl:
                if doc[field['key']] is not None:

                    curr_kwd_list= doc[field['key']].split(' ')
                    for curr_kwd in curr_kwd_list:
                        curr_kwd= curr_kwd.strip().lower()

                        if len(curr_kwd) == 0:
                            continue

                        curr_kwd= re.sub(r'^[\W[^ąćęłńóśźż]\!\?\_]+|[\W[^ąćęłńóśźż]\!\?\_]+$', '', curr_kwd, re.L)
                        new_kwd= replace_locale_symbols( curr_kwd )

                        if curr_kwd not in exclude_words:
                            kwd_list.append(curr_kwd) # append clean word
                            if new_kwd != curr_kwd:
                                kwd_list.append(new_kwd) # append word without local symbols

        doc[kwd_key]= kwd_list # always overwrite?
        db[collection].save(doc)

    return kwd_key


def replace_locale_symbols(src): # find smarter way to do it!
    return src.replace(u'ą', 'a').replace(u'ć', 'c').replace(u'ę', 'e').replace(u'ł', 'l')\
           .replace(u'ń', 'n').replace(u'ó', 'o').replace(u'ś', 's').replace(u'ź', 'z')\
           .replace(u'ż', 'z').replace(u'Ą', 'A').replace(u'Ć', 'C').replace(u'Ę', 'E')\
           .replace(u'Ł', 'L').replace(u'Ń', 'N').replace(u'Ó', 'O').replace(u'Ś', 'S')\
           .replace(u'Ź', 'Z').replace(u'Ż', 'Z')

#-----------------------------
def ensure_indexes(ns):
    curr_ns= ns['ns']
    print "collection %s (%s): \n...ensuring indexes for \"idef\" and \"parent\"" % (curr_ns, ns['name'])
    db[curr_ns].ensure_index("idef")
    db[curr_ns].ensure_index("parent")
    print "...ensuring indexes for \"level\""
    try:
        print "...ensuring indexes for \"level\""
        db[curr_ns].ensure_index("level")
    except:
        print "...no luck with \"level\" - no such key"

    sort_list_index= [] # sort
    try:
        cond_sort= ns['sort']
    except:
        cond_sort= None

    print "...ensuring indexes for sort keys"
    if cond_sort is not None:
        list_sort= [int(k) for k, v in cond_sort.iteritems()]
        list_sort.sort()
        for sort_key in list_sort:
            sort_list_index.append((cond_sort[str(sort_key)].keys()[0], cond_sort[str(sort_key)].values()[0]))

        sort_index_name= "_".join([curr_ns,"sort_default"])
        print "...ensuring index %s for sort keys %s" % (sort_index_name, sort_list_index)
        db[curr_ns].ensure_index(sort_list_index, name=sort_index_name)

    print "...ensuring indexes for query keys"
    query_list_index= [] # query
    try:
        cond_query= ns['query']
    except:
        cond_query= None

    if cond_query is not None:
        for nn in cond_query.items():
            print "...ensuring index for query key %s" % nn[0]
            db[curr_ns].ensure_index(nn[0])
    else:
        print "...no luck with query - no keys"

    print "...creating lists of keywords for full-text search %s" % curr_ns
    kwd= build_keyword_list(curr_ns, ns['columns'])
    print "...ensuring index for keyword keys"
    try:
        db[curr_ns].ensure_index(kwd)
    except Exception as e:
        print e

    print '-' * 50

#-----------------------------
def ensure_indexes_meta(coll_metadata, coll_data= None):
    err= ''
    if coll_data is not None:
        ns_item= db[coll_metadata].find_one(
            { 'ns': coll_data.strip() },
            { '_id':0, 'ns':1, 'query':1, 'sort':1, 'columns':1, 'name':1 }
            )
        if len(ns_item) == 0:
            err= "ERROR! No records found with specified collection name!"
        else:
            ensure_indexes( ns_item )
    else:
        ns_items= db[coll_metadata].find(
            {},
            {'_id':0, 'ns':1, 'query':1, 'sort':1, 'columns':1, 'name':1}
            )
        if ns_items is None:
            err= "ERROR! No records found in the specified metadata collection!"
        else:
            if ns_items.count() == 0:
                err= "ERROR! No records found in the specified metadata collection!"
            else:
                for curr_doc in ns_items:
                    ensure_indexes( curr_doc )

    if len(err) != 0:
        return err
    else:
        return 'OK'

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options]") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-m", "--meta", action="store", dest='coll_metadata',help="metadata collection name")
    cmdparser.add_option("-l", "--collect", action="store", dest='collection_name',help="data collection name (all collections if not given)")

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

    if opts.coll_metadata is not None:
        coll_meta= opts.coll_metadata
    else:
        print 'ERROR: No metadata collection specified! Exiting now...'
        exit()

    result= ensure_indexes_meta(coll_meta, opts.collection_name)
    print result

    print "Done"
