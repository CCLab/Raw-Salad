#!/usr/bin/python

"""
import Budzet Zadaniowy to mongo db
flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

the structure:
there are 2 'branches of the tree' of a budget structure, outlined in the
collection as 'node':0 and 'node':1. first two levels are common, so
they are labelled as 'node':null

nodes are:
0 - [funkcja] 1-N [zadanie] 1-N [dysponent : [[cel] 1-N [miernik]] ]
1 - [funkcja] 1-N [zadanie] 1-N [podzadanie] 1-N [dysponent : [[cel] 1-N [miernik]]]

the lowest level in both nodes for which values (money) are given is 'dysponent'
thus, if a= (total of funkcja[N].zadanie[M].dysponent[K].value where node= 0)
and b= (total of funkcja[N].zadanie[M].podzadanie[NM]dysponent[K].value where node= 1)
than a == b is True (a should be equal to b)


the script also inserts a doc into the schema collection
(warning! if there's already a schema for the budget collection, it should first
be removed manually from the collection data_zz_schema)

the files needed to upload the budget:
- this file (budggo.py)
- data file CSV, produced from PostgreSQL (for example, budggo2011.csv)
- schema file JSON (for example, budggo-schema.json)

type python budggo.py -h for instructions
"""
import os
import getpass
import optparse
import pymongo
import psycopg2
import psycopg2.extras
from ConfigParser import ConfigParser

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
def build_obj(curr_year, nosql_db, nosql_coll, sql_conn, sql_table, translate, reference):
    """
    extract data from PostgreSQL table
    re-format and store into the list of dicts
    """
    out= []

    info_useless_keys= ['node', 'czesc', 'v_total', 'v_nation', 'v_eu', 'v_proc_nation','v_proc_eu', 'budg_year']

    # first selecting and filling the result with not leaves only
    # (in the new structure it's Funkcja -> Zadanie -> Podzadanie)
    select_statement= "SELECT * FROM %s WHERE (budg_year = %d) AND ((node IS NULL) OR (node = 1 AND elem_level = 'c' and elem_type NOT LIKE 'Dysponent'))" % (sql_table, curr_year)
    cursor= sql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(select_statement)
    rows = cursor.fetchall()
    for row in rows:
        curr_dict= {}
        for kv in translate.items():
            key_dict, key_trans, key_type= kv[0], kv[1][0], kv[1][1]
            if row[key_trans] is None:
                curr_dict[key_dict]= None
            else:
                if key_type == 'int':
                    curr_dict[key_dict]= int(row[key_trans])
                elif key_type == 'float':
                    curr_dict[key_dict]= float(row[key_trans])
                elif key_type == 'string':
                    curr_dict[key_dict]= str(row[key_trans])
                else:
                    curr_dict[key_dict]= row[key_trans]
        curr_dict['info']= None # None on this level, but on level deeper will be filled by Cel -> Miernik subtree
        curr_dict['czesc_name']= None # None on this level, but on level deeper will be filled with data extracted from traditional budget
        if 'wartosc_bazowa' in curr_dict: del curr_dict['wartosc_bazowa']
        if 'wartosc_rok_obec' in curr_dict: del curr_dict['wartosc_rok_obec']
        out.append(curr_dict)

    # now selecting and filling Dysponents
    # placing into their 'info' keys their children - Cel -> Miernik subtree
    select_statement= "SELECT * FROM "+sql_table+" WHERE budg_year = "+str(curr_year)+" AND (node IN (0, 1)) AND (elem_type NOT IN ('Cel', 'Miernik')) AND (elem_type NOT LIKE 'Podzadanie%')"
    cursor= sql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(select_statement)
    rows = cursor.fetchall()
    for row in rows:
        curr_dict= {}
        for kv in translate.items():
            key_dict, key_trans, key_type= kv[0], kv[1][0], kv[1][1]
            if row[key_trans] is None:
                curr_dict[key_dict]= None
            else:
                if key_type == 'int':
                    curr_dict[key_dict]= int(row[key_trans])
                elif key_type == 'float':
                    curr_dict[key_dict]= float(row[key_trans])
                elif key_type == 'string':
                    curr_dict[key_dict]= str(row[key_trans])
                else:
                    curr_dict[key_dict]= row[key_trans]
        if 'wartosc_bazowa' in curr_dict: del curr_dict['wartosc_bazowa']
        if 'wartosc_rok_obec' in curr_dict: del curr_dict['wartosc_rok_obec']
        curr_dict['czesc_name']= None # fill with data extracted from traditional budget!!!
        curr_dict['leaf']= True # in the new structure Dysponent is always a leaf

        # filling 'info' key with Cel -> Miernik subtree
        curr_dict['info']= []
        select_statement= "SELECT * FROM "+sql_table+" WHERE budg_year = "+str(curr_year)+" AND (node = "+ str(curr_dict['node']) +") AND (idef like '"+ curr_dict['idef'] +"-%')"
        cursor_children= sql_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor_children.execute(select_statement)
        rows_children = cursor_children.fetchall()
        for row_child in rows_children:
            for k in info_useless_keys: #first delete useless keys
                if k in row_child: del row_child[k]
            row_child['type']= row_child.pop('elem_type')
            row_child['name']= row_child.pop('elem_name')
            row_child['level']= row_child.pop('elem_level')
            curr_dict['info'].append(row_child) # and then append the result to 'info' key of Dysponent

        # filling 'czescz_name' key with data extracted from traditional budget
        key_compare= curr_dict[reference['key_compare']]
        if '/' in key_compare: # czescz can have format '00/00', we nee only first part
            key_compare= key_compare[0:2]
        collect= nosql_db[reference['ns']]
        ref= collect.find_one({ reference['key_ref']: key_compare }, { reference['key_value']:1, '_id':0 })
        curr_dict['czescz_name']= ref[reference['key_value']]
#         print "\n%-5d %-15s %s %-10s %s" % (curr_dict['node'], curr_dict['idef'], key_compare, curr_dict['czesc'], curr_dict['name'])
#         print "\n%-5d %-15s %-10s %-50s %s" % (curr_dict['node'], curr_dict['idef'], curr_dict['czesc'], curr_dict['czescz_name'].encode('utf-8'), curr_dict['name'])
#         for cd in curr_dict['info']:
#             print cd

        out.append(curr_dict)

    return out

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] collection")
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-y", "--year", action="store", dest="budg_year", help="budgeting year")    
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

    opts, args = cmdparser.parse_args()

    if len(args) == 0:
        print 'No parameters specified! Type $python budggo.py -h for help'
        exit()

    if opts.budg_year is None:
        print 'Year isn\'t specified! Exiting now.'
        exit()

    conf_filename= opts.conf_filename
    if conf_filename is None:
        print 'No configuration file is specified, exiting now'
        exit()

    # get mongo connection
    conn_mongo= get_db_connect(conf_filename, 'mongodb')
    conn_mongo_host= conn_mongo['host']
    conn_mongo_port= conn_mongo['port']
    conn_mongo_db= conn_mongo['database']
    try:
        connect= pymongo.Connection(conn_mongo_host, conn_mongo_port)
        mongo_db= connect[conn_mongo_db]
        print '...connected to MongoDb database', mongo_db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()
    # authentication
    conn_mongo_username= conn_mongo['username']
    conn_mongo_password= conn_mongo['password']
    if conn_mongo_password is None:
        conn_mongo_password = getpass.getpass("MongoDB: provide password for the user %s:" % conn_mongo_username)
    if mongo_db.authenticate(conn_mongo_username, conn_mongo_password) != 1:
        print 'Cannot authenticate to MongoDB, exiting now!'
        exit()

    # get postgres connection
    conn_pg= get_db_connect(conf_filename, 'postgresql')
    conn_pg_host= conn_pg['host']
    conn_pg_port= conn_pg['port']
    conn_pg_db= conn_pg['database']
    conn_pg_username= conn_pg['username']
    conn_pg_password= conn_pg['password']
    #username - ask for password
    if conn_pg_password is None:
        conn_pg_password = getpass.getpass("PostgreSQL: provide password for the user %s:" % conn_pg_username)
    try:
        connect_postgres = psycopg2.connect(host= conn_pg_host, port= conn_pg_port, database=conn_pg_db, user= conn_pg_username, password= conn_pg_password)
        print "... connected to PostgreSQL database", conn_pg_db
    except Exception, e:
        print 'Unable to connect to the PostgreSQL database:\n %s\n' % e
        exit() #no connection to the database - no data processing

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    try:
        collect_name= args[0]
    except:
        collect_name= 'dd_budgYYYY_go'
        print 'WARNING! No collection name specified, the data will be stored in the collection %s' % collect_name

    table_name= 'budg_go'
    key_translation= {
      "idef": ["idef", "string"],
      "idef_sort": ["idef_sort", "string"],
      "parent": ["parent", "string"],
      "parent_sort": ["parent_sort", "string"],
      "node": ["node", "int"],
      "leaf": ["leaf", "boolean"],
      "level": ["elem_level", "string"],
      "type": ["elem_type", "string"],
      "name": ["elem_name", "string"],
      "czesc": ["czesc", "string"],
      "wartosc_bazowa": ["wartosc_bazowa", "string"],
      "wartosc_rok_obec": ["wartosc_rok_obec", "string"],
      "v_total": ["v_total", "int"],
      "v_nation": ["v_nation", "int"],
      "v_eu": ["v_eu", "int"],
      "v_proc_nation": ["v_proc_nation", "float"],
      "v_proc_eu": ["v_proc_eu", "float"]
        }

    foreign_ref= { "key_compare": "czesc", "ns": "dd_budg2011_tr", "key_ref": "idef", "key_value": "name"}

    print "... structuring documents for insert (sorry, gonna take some time)"
    obj_insert= build_obj(int(opts.budg_year), mongo_db, collect_name, connect_postgres, table_name, key_translation, foreign_ref)

    if db_insert(obj_insert, mongo_db, collect_name, clean_db):
        print "... %d records successfully inserted to the collection %s" % (len(obj_insert), collect_name)
    else:
        print '--- something went wrong during insert, exiting now'
        exit()

    print "Done (don't forget to fix meta-data!)"
