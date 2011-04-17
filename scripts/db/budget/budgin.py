#!/usr/bin/python
# -*- coding: utf-8 -*-

import getpass
import pymongo
import json

import optparse
from ConfigParser import ConfigParser
from time import time

#-----------------------------
def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()


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
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] collection_name") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file (CSV)")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

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

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    # get connection details
    conn= getMongoConnect(conf_filename)
    conn_host= conn['host']
    conn_port= conn['port']
    conn_db= conn['database']

    try:
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[conn_db]
        print '...connected to the database', db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    conn_user= 'admin'
    pprompt = getpass.getpass()
    if db.authenticate(conn_user, pprompt) != 1:
        print 'Cannot authenticate to db, exiting now'

    conn_schema= 'md_budg_scheme'
    conn_coll= 'dd_budg2011_go'
    conn_insert= args[0] # 'dd_budg2011_in'

    # 1. getting the list of dysponents
    distinct_dysponent= {"distinct": conn_coll, "key":"name", "query": {"node":0, "level":"c"}}
    dysponents= db.command(distinct_dysponent)['values']

    # 2. getting all the records for each dysponent, summarizing them and re-arranging for a new collection
    grand_v_nation, grand_v_eu, grand_v_total= 0,0,0
    dysp_idef_count= 0
    out_dict= []
    for dysp in dysponents:
        dysp_idef_count += 1 # must begin from 1
        dysp_dict= {} # dysponent - initial values
        dysp_dict['name']= dysp
        dysp_dict['idef']= str(dysp_idef_count)
        dysp_dict['parent']= None
        dysp_dict['leaf']= True
        dysp_dict['level']= 'a'
        dysp_dict['type']= 'Dysponent '+ dysp_dict['idef']
        dysp_dict['v_nation'], dysp_dict['v_eu'], dysp_dict['v_total']= 0,0,0
        dysp_rows= db[conn_coll].find({'name': dysp, 'node': 0}, {'_id':0}) # send query
        czesc_idef_count= 0
        for row in dysp_rows:
            czesc_idef_count += 1 # must begin from 1
            czesc_dict= {} # this - for the case we need to save Część in the collection. but then change above to - dysp_dict['leaf']= False
            czesc_dict['idef']= str(dysp_idef_count) + '-' + str(czesc_idef_count)
            czesc_dict['parent']= str(dysp_idef_count)
            czesc_dict['leaf']= True
            czesc_dict['level']= 'b'
            czesc_dict['type']= u'Część '+ row['czesc']
            czesc_dict['name']= row['czesc']
            czesc_dict['v_nation']= row['v_nation']
            czesc_dict['v_eu']= row['v_eu']
            czesc_dict['v_total']= row['v_total']

            dysp_dict['v_nation'] += czesc_dict['v_nation']
            dysp_dict['v_eu'] += czesc_dict['v_eu']
            dysp_dict['v_total'] += czesc_dict['v_total']

            #out_dict.append(czesc_dict) # adding to the list - only in case we need to save Część in the collection!

        dysp_dict['v_proc_nation']= round(float(dysp_dict['v_nation']) / float(dysp_dict['v_total']) * 100, 2)
        dysp_dict['v_proc_eu']= round(float(dysp_dict['v_eu']) / float(dysp_dict['v_total']) * 100, 2)
        out_dict.append(dysp_dict) # adding to the list only after all calculations
        
        grand_v_nation += dysp_dict['v_nation']
        grand_v_eu += dysp_dict['v_eu']
        grand_v_total += dysp_dict['v_total']

    total_dict= {} # dysponent - initial values
    total_dict['name']= u'Ogółem'
    total_dict['idef']= '999999'
    total_dict['parent']= None
    total_dict['leaf']= True
    total_dict['level']= 'a'
    total_dict['type']= u'Ogółem'
    total_dict['v_nation']= grand_v_nation
    total_dict['v_eu']= grand_v_eu
    total_dict['v_total']= grand_v_total
    total_dict['v_proc_nation']= round(float(grand_v_nation) / float(grand_v_total) * 100, 2)
    total_dict['v_proc_eu']= round(float(grand_v_eu) / float(grand_v_total) * 100, 2)

    out_dict.append(total_dict) # adding to the list only after summarizing the totals

    print '-- inserting data into '+ conn_db +'.'+ conn_coll
    conn.start_request()
    print '-- ', db_insert(out_dict, db, conn_insert, clean_db), 'records inserted'
    print 'Done'
