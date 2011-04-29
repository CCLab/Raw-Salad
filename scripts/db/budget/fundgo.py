#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
import Funduszy Celowe w ukladie Zadaniowy to mongoDB
flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

the structure:
there are 2 'branches of the tree' of a budget structure, outlined in the
collection as 'node':null and 'node':0

nodes are:
null: [fundusz] 1-N [dzial] 1-N [zadanie] 1-N [podzadanie]
1: ...[zadanie] 1-N [miernik]

Warning! No schema create or update!

the files needed to upload the budget:
- this file (fundgo.py)
- data file CSV, produced from XLS (for example, fundgo.csv)
- schema file JSON (for example, fundgo-schema.json)

type python fundgo.py -h for instructions
"""
import getpass
import os
import optparse
import csv
import pymongo
import simplejson as json
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
def sort_format(src):
    """
    format 1-2-3... to 001-002-003...
    src should be convertable to int
    """
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
def check_collection(db, collname):
    # checking the result collection for consistency
    noerrors= True

    # 1. find those with 'leaf':null and check if they have children
    #    and update 'leaf':True if no, 'leaf':False otherwise
    null_leaf_curr= db[collname].find({'leaf':None})
    for row in null_leaf_curr:
        curr_idef= row['idef']
        if db[collname].find({'parent':curr_idef}).count() > 0:
            leaf_status= False
        else:
            leaf_status= True
        row['leaf']= leaf_status
        db[collname].save(row, safe=True)
        print '--- update leaf status to %s for element %s' % (leaf_status, curr_idef)

    # check for broken "links" in the parent keys
    curs= db[collname].find({'parent': {'$ne': None}}, {'_id':0})
    for row in curs:
        curr_parent= row['parent']
        if db[collname].find({'idef':curr_parent}).count() == 0:
            print '--! inconsistency found! Cannot find parent for element %s - idef %s not found in the collection' % (row['idef'], curr_parent)
            noerrors= False

    return noerrors

#-----------------------------
def clean_dict(src_dict):
    # delete obsolete keys
    if 'fundusz' in src_dict: del src_dict['fundusz']
    if 'dzial' in src_dict: del src_dict['dzial']
    if 'zadanie' in src_dict: del src_dict['zadanie']
    if 'podzadanie' in src_dict: del src_dict['podzadanie']
    # transform type from "blahblah X-Y-Z" to "blahblah X.Y.Z"
    type_list= src_dict['type'].rsplit(' ')
    type_list[1]= type_list[1].replace('-', '.')
    src_dict['type']= ' '.join(type_list)
    # all meaningful text fields go through .replace('\n', ' ') and .replace('Ŝ', 'ż')
    if src_dict['cel'] is not None:
        src_dict['cel']= src_dict['cel'].replace('\n', ' ')
        src_dict['cel']= src_dict['cel'].replace('Ŝ', 'ż')
    if src_dict['miernik'] is not None:
        src_dict['miernik']= src_dict['miernik'].replace('\n', ' ')
        src_dict['miernik']= src_dict['miernik'].replace('Ŝ', 'ż')
    if src_dict['name'] is not None:
        src_dict['name']= src_dict['name'].replace('\n', ' ')
        src_dict['name']= src_dict['name'].replace('Ŝ', 'ż')

    return src_dict


#-----------------------------
def csv_parse(csv_read, schema, database, datacoll):
    # parse csv data and put in into the dictionary
    out= []

    dbkey_alias= schema["alias"] # dict of aliases -> document keys in db
    dbval_types= schema["type"] # dict of types -> values types in db

    for row in csv_read:
        keys= tuple(row)
        keys_len= len(keys)
        row= iter(row)        
        for row in csv_read:
            i= 0
            dict_row= {} # this holds the data of the current row
            for field in row:
                new_key= [v for k, v in dbkey_alias.iteritems() if i == int(k)][0]
                new_type= None
                if new_key in dbval_types:
                    new_type= dbval_types[new_key]

                if len(field.strip()) == 0:
                    dict_row[new_key]= None
                else:
                    if new_type == "string":
                        dict_row[new_key] = field
                    elif new_type == "int":
                        dict_row[new_key] = int(field)
                    elif new_type == "float":
                        if ',' in field:
                            field= field.replace(',', '.')
                        dict_row[new_key]= float(field)
                    elif new_type == None:
                        try:
                            dict_row[new_key]= float(field) # then if it is a number
                            if dict_row[new_key].is_integer(): # it can be integer
                                dict_row[new_key] = int(field)
                        except:
                            dict_row[new_key] = field # no, it is a string
                i += 1

            dict_row_miernik= {} # for the case we create miernik for Zadanie

            # check the role and create an element of according type
            if dict_row['level'] == 'a': # FUNDUSZ
                dict_row['name']= dict_row['fundusz']
                dict_row['type']= 'FUNDUSZ '+str(dict_row['idef'])
                dict_row['parent']= None
                dict_row['leaf']= False
                dict_row['node']= None
                dict_row['idef_sort']= sort_format(dict_row['idef'])
                dict_row['parent_sort']= None

            elif dict_row['level'] == 'b': # Dzial
                dict_row['name']= dict_row['dzial']
                dict_row['type']= 'Dział '+str(dict_row['idef'])
                idef_list= dict_row['idef'].split('-')
                dict_row['parent']= idef_list[0]
                dict_row['leaf']= False
                dict_row['node']= None
                dict_row['idef_sort']= sort_format(dict_row['idef'])
                dict_row['parent_sort']= sort_format(dict_row['parent'])

            elif dict_row['level'] == 'c': # Zadanie
                dict_row['name']= dict_row['zadanie']
                dict_row['type']= 'Zadanie '+str(dict_row['idef'])
                idef_list= dict_row['idef'].rsplit('-', 1)
                dict_row['parent']= idef_list[0]
                dict_row['leaf']= None # check later if it's a leaf - .find({leaf:null})
                dict_row['node']= None
                dict_row['idef_sort']= sort_format(dict_row['idef'])
                dict_row['parent_sort']= sort_format(dict_row['parent'])
                # create here another node for Miernik (of Cel which belongs to Zadanie), which is coded as '...-...-...-m...'
                if dict_row['cel'] is not None:
                    dict_row_miernik= dict_row.copy()
                    dict_row_miernik['idef']= dict_row['idef']+'-m01'
                    dict_row_miernik['name']= dict_row['miernik']
                    dict_row_miernik['type']= 'Miernik '+str(dict_row_miernik['idef'])
                    dict_row_miernik['parent']= dict_row['idef'] # current Zadanie is a parent of Miernik
                    dict_row_miernik['leaf']= True # we now it's a leaf
                    dict_row_miernik['level']= 'd'
                    dict_row_miernik['cel']= None # we have cel on the level of Zadanie
                    dict_row_miernik['miernik']= None # 'miernik' becomes 'name'
                    dict_row_miernik['node']= 0 # Zadanie - Miernik is node 0
                    dict_row_miernik['idef_sort']= sort_format(dict_row_miernik['idef'])
                    dict_row_miernik['parent_sort']= sort_format(dict_row_miernik['parent'])
                    dict_row_miernik['val_2011'], dict_row_miernik['val_2012'], dict_row_miernik['val_2013']= 0,0,0 # no money on the level of miernik
                    out.append(clean_dict(dict_row_miernik))
                    # update dict row
                    dict_row['miernik']= None
                    dict_row['miernik_wartosc_bazowa']= None # clean 'miernik' from it
                    dict_row['miernik_wartosc_2011']= None
                    dict_row['miernik_wartosc_2012']= None
                    dict_row['miernik_wartosc_2013']= None
                    dict_row['leaf']= False # now we know it's not a leaf

            elif dict_row['level'] == 'd': # Podzadanie
                dict_row['name']= dict_row['podzadanie']
                dict_row['type']= 'Podzadanie '+str(dict_row['idef'])
                idef_list= dict_row['idef'].rsplit('-', 1)
                dict_row['parent']= idef_list[0]
                dict_row['leaf']= True # podzadanie is the deepest level
                dict_row['node']= None
                dict_row['idef_sort']= sort_format(dict_row['idef'])
                dict_row['parent_sort']= sort_format(dict_row['parent'])

            elif dict_row['level'] == 'd0': # Miernik
                dict_row['name']= dict_row['miernik']
                dict_row['type']= 'Miernik '+str(dict_row['idef'])
                idef_list= dict_row['idef'].rsplit('-', 1)
                dict_row['parent']= idef_list[0]
                dict_row['leaf']= True
                dict_row['node']= 0
                dict_row['level']= 'd'
                dict_row['idef_sort']= sort_format(dict_row['idef'])
                dict_row['parent_sort']= sort_format(dict_row['parent'])
                dict_row['val_2011'], dict_row['val_2012'], dict_row['val_2013']= 0,0,0 # no money on the level of miernik

            out.append(clean_dict(dict_row))

    return out

    

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] source_file.csv source_schema.json") 
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
    coll_schm= 'md_fund_scheme'
    coll_data= 'dd_fund2011_go'

    # CSV file
    try:
        src_file= open(args[0], 'rb')
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    csv_delim= ';'
    csv_quote= '"'
    try:
        csv_read= csv.reader(src_file, delimiter= csv_delim, quotechar= csv_quote)
    except Exception as e:
        print 'Unable to read CSV file:\n %s\n' % e
        exit()

    # schema file
    try:
        filename_schema= args[1]
    except:
        filename_schema= None
    if filename_schema is None:
        filename_schema= args[0].rstrip('.csv')+'-schema.json'
    try: #deserialize it into the object
        sch_src= open(filename_schema, 'rb')
        schema= json.load(sch_src, encoding='utf-8') # schema file
    except Exception as e:
        print 'Error in processing schema file:\n %s\n' % e
        exit()

    obj_parsed= csv_parse(csv_read, schema, db, coll_data) # fill data table

    if db_insert(obj_parsed, db, coll_data, clean_db):
        print '...the data successfully inserted to the collection %s' % coll_data

    print '...checking data consistency'

    if check_collection(db, coll_data):
        print '...no inconsistencies have been found in the collection %s' % coll_data
    else:
        print '...inconsistencies have been found in the collection %s - check your data' % coll_data

    print "Done (don't forget about the schema!)"
