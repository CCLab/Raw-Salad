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
    try:
        connect_dict['password']= cfg.get('mongodb','password')
    except:
        connect_dict['password']= None

    return connect_dict


#-----------------------------
def sort_format(src):
    """
    format 1-2-3... to 001-002-003...
    src should be convertable to int
    """
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        res_list.append('%03d' % int(elm))
    res= '-'.join(res_list)
    return res


#-----------------------------
def fill_dysp_parent0(dysp_parent0, czesc, database, collection):
    level_dysp_parent0= database[collection].find({'idef': dysp_parent0, 'node':{ '$in':[None,1]}}, {'_id':0}) # the record of dysponent itself
    for ldp0_row in level_dysp_parent0:
        print "%10s %20s %05s %05s %-100r" % (ldp0_row['idef'], ldp0_row['type'], czesc, ldp0_row['level'], ldp0_row['name'].encode('utf-8'))



#-----------------------------
def fill_dysp(dysponent_name, dysponent_idef, database, collection):
    level_dysponent= database[collection].find({'name': dysponent_name, 'node': 1}, {'_id':0}) # the record of dysponent itself
    for ld_row in level_dysponent:
        fill_dysp_parent0(ld_row['parent'], ld_row['czesc'], database, collection)
        
        
        # BOOKMARK
        # summarize values here
        # and go 'upper' in the hierarchy every time checking the level

#-----------------------------
if __name__ == "__main__":
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] collection_name") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
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

    conn_schema= 'md_budg_scheme'
    conn_coll= 'dd_budg2011_go'
    conn_insert= args[0] # 'dd_budg2011_in'

    # 1. getting the list of dysponents
    distinct_dysponent= {"distinct": conn_coll, "key":"name", "query": {"node":1, "type":"Dysponent", "level":{"$in":["c","d"]}}}
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
        dysp_dict['idef_sort']= sort_format(dysp_dict['idef'])
        dysp_dict['parent']= None
        dysp_dict['parent_sort']= None
        dysp_dict['leaf']= False
        dysp_dict['level']= 'a'
        dysp_dict['type']= 'Dysponent '+ dysp_dict['idef']
        dysp_dict['v_nation'], dysp_dict['v_eu'], dysp_dict['v_total']= 0,0,0

        #print dysp_dict['idef'], dysp_dict['name'].encode('utf-8')

        # 2.1. gathering 'Część' for current 'Dysponent'
        dysp_rows= db[conn_coll].find({'name': dysp, 'node': 1}, {'_id':0}) # send query
        czesc_idef_count= 0
        for row in dysp_rows:
            czesc_idef_count += 1 # must begin from 1
            czesc_dict= {} # this - for the case we need to save Część in the collection. but then change above to - dysp_dict['leaf']= False
            czesc_dict['idef']= dysp_dict['idef'] + '-' + str(czesc_idef_count)
            czesc_dict['parent']= dysp_dict['idef']
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

        print "%030s %05s %-100r" % (dysp_dict['idef'], dysp_dict['level'], dysp.encode('utf-8'))
        dp= fill_dysp(dysp, dysp_dict['idef'], db, conn_coll)
        print '\n'{"distinct": conn_coll, "key":"name", "query": {"node":1, "type":"Dysponent", "level":{"$in":["c","d"]}}}
        
        grand_v_nation += dysp_dict['v_nation']
        grand_v_eu += dysp_dict['v_eu']
        grand_v_total += dysp_dict['v_total']

    # 3. Grand Total
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

    print '-- inserting data into '+ conn_db +'.'+ conn_insert
    connection.start_request()
    print '-- ', db_insert(out_dict, db, conn_insert, clean_db), 'records inserted'
    connection.end_request()
    print 'Done'
