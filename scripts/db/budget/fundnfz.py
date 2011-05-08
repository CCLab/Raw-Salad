#!/usr/bin/python

"""
import:
NARODOWY FUNDUSZ ZDROWIA

flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

bulk of files:
- this file (fundnfz.py)
- data file CSV, produced from XLS (for example, fundnfz.csv)
- schema file JSON (for example, fundnfz-schema.json)
- conf file with mongo connection settings

type python fundnfz.py -h for instructions
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

    collect.insert(data_bulk)
    return collect.find().count()


#-----------------------------
def fill_docs(fund_data):
    # format parsed data (dict) for upload

    # add keys: idef, idef_sort, parent, parent_sort, level, leaf
    work_dict= fund_data[:]
    levels= ['a', 'b', 'c', 'd', 'e', 'f']
    for row_doc in work_dict:
        row_doc['idef']= row_doc['numer'].replace('.', '-')
        row_doc['idef_sort']= sort_format(row_doc['idef'])
        dash_count= row_doc['idef'].count('-')
        row_doc['leaf']= True # default, being filled below
        row_doc['level']= levels[dash_count]
        row_doc['parent']= None
        row_doc['parent_sort']= None
        if dash_count != 0:
            row_doc['parent']= row_doc['idef'].rsplit('-', 1)[0]
            row_doc['parent_sort']= sort_format(row_doc['parent'])

    # filling 'leaf'
    leaf_dict= work_dict[:]
    for row_doc in work_dict:
        for curr_doc in leaf_dict:
            if curr_doc['parent'] == row_doc['idef']:
                row_doc['leaf']= False
                break

    return work_dict


#-----------------------------
def csv_parse(csv_read, schema):
    # parse csv and return dict
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

                if new_type == "string":
                    dict_row[new_key] = str(field)
                elif new_type == "int":
                    if field == '':
                        dict_row[new_key] = 0
                    else:
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
                #additional fields
                dict_row['parent']= None

                i += 1

            out.append(dict_row)

    return out


#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] src_filename.csv src_schema.json")
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-t", "--collt", action="store", dest="collect_name", help="collection name")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

    opts, args = cmdparser.parse_args()

    if len(args) == 0:
        print 'No parameters specified! Type python budgnfz.py -h for help'
        exit()

    try:
        src_file= open(args[0], 'rb')
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    csv_delim= ';' #read CSV file with data
    csv_quote= '"'
    try:
        csv_read= csv.reader(src_file, delimiter= csv_delim, quotechar= csv_quote)
    except Exception as e:
        print 'Unable to read CSV file:\n %s\n' % e
        exit()

    try: #read schema file
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

    conf_filename= opts.conf_filename
    if conf_filename is None:
        print 'No configuration file is specified, exiting now'
        exit()        

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

    try:
        collect_name= opts.collect_name
    except:
        collect_name= 'dd_fund2011_nfz'
        print 'WARNING! No collection name specified, the data will be stored in the collection %s' % collect_name

    print "...parsing source file"
    obj_parsed= csv_parse(csv_read, schema)
    print "...formatting documents"
    obj_upload= fill_docs(obj_parsed)

    print '...inserting into db/n... ', db_insert(obj_upload, mongo_db, collect_name, clean_db), 'records inserted'
    print "Done (don't forget about the schema!)"
