#!/usr/bin/python
# -*- coding: utf-8 -*-

import getpass
import pymongo
import psycopg2
import psycopg2.extras
import json

import optparse
from ConfigParser import ConfigParser
from time import time

#-----------------------------
def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    success= True
    try:
        collect.insert(data_bulk)
    except Exception as e:
        success= False
        print 'Cannot insert data:\n %s\n' % e

    return success


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
def clean_format(src):
    #format 001-002-003... to 1-2-3...
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        try:
            res_list.append('%d' % int(elm))
        except:
            res_list.append(elm)
    res= '-'.join(res_list)
    return res


#-----------------------------
def sort_format(src):
    #format 1-2-3... to 001-002-003...
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        try:
            res_list.append('%03d' % int(elm))
        except:
            res_list.append(elm)
    res= '-'.join(res_list)
    return res


#-----------------------------
def fetch_elem(tbl, conn, elem_idef):
    #extracting basic information about the element
    st= "SELECT idef, idef_sort, elem_type, elem_name FROM %s WHERE (node IS NULL OR node = 1) AND idef= '%s'" % (tbl, elem_idef)
    curs= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curs.execute(st)
    return curs.fetchone()


#-----------------------------
def work_cursor(work_tbl, connection, work_year, budget_traditional):
    out= []
    print '...quering database'
    select_statement= """
        SELECT DISTINCT elem_name, substring(parent_sort from '...') as parent2, substring(parent_sort from '...-...') as parent1, parent_sort as parent0, parent, czesc,
        SUM(v_total) AS sum_v_total, SUM(v_nation) as sum_v_nation, SUM(v_eu) as sum_v_eu
        from
    """ + work_tbl + """
        WHERE 
        (
        	((node IS NULL OR node = 1) AND (elem_level = 'd') AND (idef NOT LIKE '22-%'))
        	OR 
        	((node IS NULL OR node = 0) AND (elem_level = 'c') AND (idef LIKE '22-%'))
        )
        AND (budg_year = 
    """ + work_year + """)
        GROUP BY elem_name, parent, parent_sort, czesc
        ORDER BY elem_name, parent_sort, czesc
    """
    dict_cur= connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_statement)
    rows = dict_cur.fetchall()
    dysp_idef_count= 0
    curr_dysp= None
    dysp_dict= {}
    parent2_dict= {}
    parent1_dict= {}
    parent0_dict= {}

    grand_total_nation, grand_total_eu, grand_total= 0,0,0

#     print "%-100s %10s %10s %15s %15s %10s %10s %10s %10s" % (
#         'elem_name', 'parent2', 'parent1', 'parent0', 'parent', 'czesc', 'sum_v_total', 'sum_v_nation', 'sum_v_eu'
#         )
    print '...processing cursor data'
    for row in rows:
        # creating dysponent dict
        if curr_dysp != row['elem_name']:
            curr_dysp= row['elem_name'] # current dysponent - highest level 'a'
            dysp_idef_count += 1
            if len(dysp_dict) != 0: out.append(dysp_dict)
            dysp_dict= {}
            dysp_dict['name']= row['elem_name']
            dysp_dict['idef']= 'dt-'+str(dysp_idef_count)
            dysp_dict['idef_sort']= 'dt-'+sort_format(str(dysp_idef_count))
            dysp_dict['parent']= None
            dysp_dict['parent_sort']= None
            dysp_dict['node']= None # Dysponent is no node
            dysp_dict['leaf']= False
            dysp_dict['level']= 'a'
            dysp_dict['type']= 'Dysponent'
            dysp_dict['v_nation']= row['sum_v_nation']
            dysp_dict['v_eu']= row['sum_v_eu']
            dysp_dict['v_total']= row['sum_v_total']
            # loop control values
            curr_dysp_idef, curr_dysp_idef_sort= dysp_dict['idef'], dysp_dict['idef_sort']
            curr_parent2= None # reset - new dysponent always means new funkcja
#             print "%10s; %10s; %-10s; %s; %-50s;" % (dysp_dict['idef'], '', dysp_dict['level'], dysp_dict['type'], dysp_dict['name'])
        else:
            dysp_dict['v_nation'] += row['sum_v_nation']
            dysp_dict['v_eu'] += row['sum_v_eu']
            dysp_dict['v_total'] += row['sum_v_total']

        # creating funkcja dict - level of parent2, 'b'
        if curr_parent2 != row['parent2']:
            curr_parent2= row['parent2'] # current funkcja
            if len(parent2_dict) != 0: out.append(parent2_dict)
            parent2_dict= {}
            funk_row = fetch_elem(work_tbl, connection, str(int(row['parent2'])))
            parent2_dict['idef']= curr_dysp_idef + '-'+funk_row['idef']
            parent2_dict['idef_sort']= curr_dysp_idef_sort + '-'+funk_row['idef_sort']
            parent2_dict['parent']= curr_dysp_idef
            parent2_dict['parent_sort']= curr_dysp_idef_sort
            parent2_dict['name']= funk_row['elem_name']
            parent2_dict['type']= funk_row['elem_type']
            parent2_dict['node']= None # Funkcja is no node
            parent2_dict['leaf']= False
            parent2_dict['level']= 'b'
            parent2_dict['v_nation']= row['sum_v_nation']
            parent2_dict['v_eu']= row['sum_v_eu']
            parent2_dict['v_total']= row['sum_v_total']
            # loop control values
            curr_funk_idef, curr_funk_idef_sort= parent2_dict['idef'], parent2_dict['idef_sort']
            curr_parent1= None # reset - new funkcja always means new zadanie
#             print "%10s; %10s; %-10s; %8s %s; %-50s" % (parent2_dict['idef'], parent2_dict['parent'], parent2_dict['level'], '', parent2_dict['type'], parent2_dict['name'])
        else:
            parent2_dict['v_nation'] += row['sum_v_nation']
            parent2_dict['v_eu'] += row['sum_v_eu']
            parent2_dict['v_total'] += row['sum_v_total']

        # creating zadanie dict - level of parent1, 'c'
        if curr_parent1 != row['parent1']:
            curr_parent1= row['parent1'] # current zadanie
            if len(parent1_dict) != 0:
                out.append(parent1_dict)
                parent1_dict_node1= parent1_dict.copy() # for node 1
                parent1_dict_node1['node']= 1
                if ' 22.' in parent1_dict_node1['type']:
                    parent1_dict_node1['leaf']= True # Zadanie CAN BE a leaf in node 1 (of Funk 22)
                out.append(parent1_dict_node1)
            parent1_dict= {}
            zadn_row = fetch_elem(work_tbl, connection, clean_format(row['parent1']))
            parent1_dict['idef']= curr_dysp_idef+'-'+zadn_row['idef']
            parent1_dict['idef_sort']= curr_dysp_idef_sort+'-'+zadn_row['idef_sort']
            parent1_dict['parent']= curr_funk_idef
            parent1_dict['parent_sort']= curr_funk_idef_sort
            parent1_dict['name']= zadn_row['elem_name']
            parent1_dict['type']= zadn_row['elem_type']
            parent1_dict['node']= 0 # Zadanie is a node 0
            parent1_dict['leaf']= False
            parent1_dict['level']= 'c'
            parent1_dict['v_nation']= row['sum_v_nation']
            parent1_dict['v_eu']= row['sum_v_eu']
            parent1_dict['v_total']= row['sum_v_total']
            # loop control values
            curr_zadn_idef, curr_zadn_idef_sort= parent1_dict['idef'], parent1_dict['idef_sort']
            curr_parent0= None # reset - new zadanie always means new podzadanie
#             print "%10s; %10s; %-10s; %16s %s; %-50s" % (parent1_dict['idef'], parent1_dict['parent'], parent1_dict['level'], '', parent1_dict['type'], parent1_dict['name'])
        else:
            parent1_dict['v_nation'] += row['sum_v_nation']
            parent1_dict['v_eu'] += row['sum_v_eu']
            parent1_dict['v_total'] += row['sum_v_total']

        # creating podzadanie dict - level of parent1, 'd'
        if curr_parent0 != row['parent0']:
            if row['parent1'] != row['parent0']: # there is at least 1 podzadanie, creating a dict
                curr_parent0= row['parent0'] # current zadanie
                if len(parent0_dict) != 0:
                    out.append(parent0_dict)
                    parent0_dict_node1= parent0_dict.copy() # for node 1
                    parent0_dict_node1['node']= 1
                    parent0_dict_node1['leaf']= True # Podzadanie IS ALWAYS a leaf in node 1
                    out.append(parent0_dict_node1)
                parent0_dict= {}
                podz_row = fetch_elem(work_tbl, connection, row['parent'])
                parent0_dict['idef']= curr_dysp_idef+'-'+podz_row['idef']
                parent0_dict['idef_sort']= curr_dysp_idef_sort+'-'+podz_row['idef_sort']
                parent0_dict['parent']= curr_zadn_idef
                parent0_dict['parent_sort']= curr_zadn_idef_sort
                parent0_dict['name']= podz_row['elem_name']
                parent0_dict['node']= 0 # Podzadanie is a node 0
                parent0_dict['type']= podz_row['elem_type']
                parent0_dict['leaf']= False
                parent0_dict['level']= 'd'
                parent0_dict['v_nation']= row['sum_v_nation']
                parent0_dict['v_eu']= row['sum_v_eu']
                parent0_dict['v_total']= row['sum_v_total']
                # loop control values
                curr_podz_idef, curr_podz_idef_sort= parent0_dict['idef'], parent0_dict['idef_sort']
#                 print "%10s; %10s; %-10s; %20s %s; %-50s" % (row['parent'], parent0_dict['parent'], parent0_dict['level'], '', parent0_dict['type'], parent0_dict['name'])
        else:
            if row['parent1'] != row['parent0']: # there is at least 1 podzadanie, summarizing podzadanie
                parent0_dict['v_nation'] += row['sum_v_nation']
                parent0_dict['v_eu'] += row['sum_v_eu']
                parent0_dict['v_total'] += row['sum_v_total']

        # creating czesc dict - level below parent, 'e' or 'd' (in case of funk 22 where there is no podzadanie leve)
        czesc_dict= {}
        if row['parent1'] == row['parent0']: # czesc is a child of Zadanie
            czesc_dict['idef']= '-'.join([curr_zadn_idef, row['czesc']])
            czesc_dict['parent']= curr_zadn_idef
            czesc_dict['level']= 'd'
        else: # czesc is a child of Podzadanie
            czesc_dict['idef']= '-'.join([curr_podz_idef, row['czesc']])
            czesc_dict['parent']= curr_podz_idef
            czesc_dict['level']= 'e'
        czesc_dict['idef_sort']= sort_format(czesc_dict['idef'])
        czesc_dict['parent_sort']= sort_format(czesc_dict['parent'])
        czesc_dict['node']= 0 # Czesc is a node 0
        czesc_dict['leaf']= True
        czesc_dict['type']= 'Część ' + row['czesc']
        czesc_ref= row['czesc'][0:2]
        ref= budget_traditional.find_one({ 'idef': czesc_ref }, { 'name':1, '_id':0 })
        if ref is not None: # finding the name for czesc from Budzet Ksiegowy
            czesc_dict['name']= ref['name']
        else:
            czesc_dict['name']= row['czesc']
        czesc_dict['v_nation'], czesc_dict['v_eu'], czesc_dict['v_total']= row['sum_v_nation'], row['sum_v_eu'], row['sum_v_total']
        out.append(czesc_dict)
        # summarizing grand totals only on the level of czesc
        grand_total_nation += row['sum_v_nation']
        grand_total_eu += czesc_dict['v_eu']
        grand_total += row['sum_v_total']

#         if row['parent1'] == row['parent0']: # czesc is a child of Zadanie
#             print "%10s; %10s; %-10s; %20s %s; %-50s" % (czesc_dict['idef'], czesc_dict['parent'], czesc_dict['level'], '', czesc_dict['type'], czesc_dict['name'])
#         else:
#             print "%10s; %10s; %-10s; %24s %s; %-50s" % (czesc_dict['idef'], czesc_dict['parent'], czesc_dict['level'], '', czesc_dict['type'], czesc_dict['name'])

    # and now append last filled dicts
    out.append(dysp_dict)
    out.append(parent2_dict)
    out.append(parent1_dict)
    out.append(parent0_dict)
    # node 1 - Zadanie
    parent1_dict_node1= parent1_dict.copy() # for node 1
    parent1_dict_node1['node']= 1
    if ' 22.' in parent1_dict_node1['type']:
        parent1_dict_node1['leaf']= True # Zadanie CAN BE a leaf in node 1 (of Funk 22)
    out.append(parent1_dict_node1)
    # node 1 - Podzadanie
    parent0_dict_node1= parent0_dict.copy() # for node 1
    parent0_dict_node1['node']= 1
    parent0_dict_node1['leaf']= True # Podzadanie IS ALWAYS a leaf in node 1
    out.append(parent0_dict_node1)

    total_dict= {}
    total_dict['idef']= 'dt-9999'
    total_dict['idef_sort']= 'dt-9999'
    total_dict['parent']= None
    total_dict['parent_sort']= None
    total_dict['level']= 'a'
    total_dict['leaf']= True
    total_dict['type']= 'total'
    total_dict['name']= 'Ogółem'
    total_dict['v_nation']= grand_total_nation
    total_dict['v_eu']= grand_total_eu
    total_dict['v_total']= grand_total
    out.append(total_dict)

    # counting percentage
    for doc_in in out:
        if doc_in['v_total'] != 0:
            doc_in['v_proc_eu']= round(float(doc_in['v_eu']) / float(doc_in['v_total']) * 100, 2)
            doc_in['v_proc_nation']= round(float(doc_in['v_nation']) / float(doc_in['v_total']) * 100, 2)

    print '..data processed: total recs %d' % len(out)
    return out


#-----------------------------
if __name__ == "__main__":
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] collection_name") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-y", "--year", action="store", dest="budg_year", help="budgeting year")    
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

    opts, args = cmdparser.parse_args()

    conf_filename= opts.conf_filename
    if conf_filename is None:
        print 'No configuratuion file specified!'
        exit()

    if opts.budg_year is None:
        print 'Year isn\'t specified! Exiting now.'
        exit()

    try:
        f_temp= open(conf_filename, 'rb')
    except Exception as e:
        print 'Cannot open .conf file:\n %s\n' % e
        exit()

    # get connection details
    conn= get_db_connect(conf_filename, 'postgresql')
    conn_host= conn['host']
    conn_port= conn['port']
    conn_db= conn['database']
    conn_username= conn['username']
    conn_password= conn['password']
    #username - ask for password
    if conn_password is None:
        conn_password = getpass.getpass('Password for '+conn_username+': ')

    try:
        connect_postgres = psycopg2.connect(host= conn_host, port= conn_port, database=conn_db, user= conn_username, password= conn_password)
        print "... connected to db", conn_db
    except Exception, e:
        print 'Unable to connect to the PostgreSQL database:\n %s\n' % e
        exit() #no connection to the database - no data processing

    # get mongo connection details
    conn_mongo= get_db_connect(conf_filename, 'mongodb')
    conn_mongo_host= conn_mongo['host']
    conn_mongo_port= conn_mongo['port']
    conn_mongo_db= conn_mongo['database']

    try:
        connect= pymongo.Connection(conn_mongo_host, conn_mongo_port)
        mongo_db= connect[conn_mongo_db]
        print '...connected to the database', mongo_db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    conn_mongo_username= conn_mongo['username']
    conn_mongo_password= conn_mongo['password']
    if conn_mongo_password is None:
        conn_mongo_password = getpass.getpass()
    if mongo_db.authenticate(conn_mongo_username, conn_mongo_password) != 1:
        print 'Cannot authenticate to db, exiting now'
        exit()

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    # data & meta-data collections
    coll_schm= 'md_fund_scheme'
    coll_data= args[0] #'dd_bugd2011_in'

    wrk_table= "budg_go"
    budget_ref= mongo_db['dd_budg2011_tr']
    obj_parsed= work_cursor(wrk_table, connect_postgres, opts.budg_year, budget_ref)

    print "...no errors so far - inserting data into mongo collection"

    if db_insert(obj_parsed, mongo_db, coll_data, clean_db):
        print '...the data successfully inserted to the collection %s' % coll_data
    else:
        print '...something went wrong during insert, exiting now'
        exit()

    print "Done (don't forget about the schema!)"
