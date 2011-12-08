#!/usr/bin/python

"""
parse and import polls CSV dumps into:
1. MongoDB (all collections are being automatically created)
2. External JSON file

Required: MongoDB 1.6.5 or higher, server should be started (./mongod)

Please, consult >>python csv2mongo.py --help
"""

import getpass
import os
import optparse
import csv
import simplejson as json
import itertools
import pymongo
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
        try:
            collect.remove()
        except Exception as e:
            print 'Unable to remove data from the collection:\n %s\n' % e

    try:
        collect.insert(data_bulk)
    except Exception as e:
        print 'Unable to remove data from the collection:\n %s\n' % e

    return collect.find().count()

#-----------------------------
def sort_format(src):
    """
    format 1-2-3... to 00001-00002-00003...
    src should be convertable to int
    """
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        try:
            res_list.append('%05d' % int(elm))
        except:
            res_list.append(elm)
    res= '-'.join(res_list)
    return res

#-----------------------------
def complete_data(data_parsed):
    out= data_parsed[:]

    # filling totals
    val_fields_list= [k for k, v in dbval_types.iteritems() if v in ['int','float']]
    if len(val_fields_list) > 0:

        total_dict= {} # prepare total dict
        for field in val_fields_list:
            total_dict[field]= 0
        
        print "... calculating totals"
        for row in out:
            if row['level'] == 'a':
                for field in val_fields_list:
                    total_dict[field] += row[field]
        # finishing total dict
        total_dict['idef']= '99999'
        total_dict['parent']= None
        total_dict['type']= 'Total'
        total_dict['name']= 'GRAND TOTAL'
        total_dict['level']= 'a'
        out.append(total_dict)

    print "... filling _sort keys"
    for row in out:
        row['idef_sort']= sort_format(row['idef'])
        if row['parent'] is None:
            row['parent_sort']= None
        else:
            row['parent_sort']= sort_format(row['parent'])
        #simultaneously preparing to the next step
        row['leaf']= True

    print "... filling leaves"
    data_children= out[:]
    for data_row in out:
        for data_child in data_children:
            if data_row['idef'] == data_child['parent']:
                data_row['leaf']= False
                break

    return out

#-----------------------------------------------
# parse CSV, convert it to JSON and save to file
def csv_parse(filename_csv, filename_schema, delimit, quote):
    out= []

    if filename_schema == None:
        filename_schema= filename_csv.rstrip('.csv')+'-schema.json'
    try:
        csv_src= open(filename_csv, 'rb')
    except IOError as e:
        print 'Unable to open src_file:\n %s\n' % e
    else:
        csv_read= csv.reader(csv_src, delimiter= delimit, quotechar= quote)

        for row in csv_read:
            keys= tuple(row)
            row= iter(row)
            
            for row in csv_read:
                i= 0
                row_dict= {}
                for field in row:
                    new_key= [v for k, v in dbkey_alias.iteritems() if i == int(k)][0]

                    new_type= None
                    if new_key in dbval_types:
                        new_type= dbval_types[new_key]

                    if field == "":
                        row_dict[new_key] = None # first check if there is any value at all
                    else:
                        if new_type == "string":
                            row_dict[new_key] = field
                        elif new_type == "int":
                            row_dict[new_key] = int(field)
                        elif new_type == "float":
                            if ',' in field:
                                field= field.replace(',', '.')
                            row_dict[new_key]= float(field)
                        elif new_type == "boolean":
                            if field in ['t', 'T', 'true', 'TRUE', 1]:
                                row_dict[new_key]= True
                            elif field in ['f', 'F', 'false', 'FALSE', 0]:
                                row_dict[new_key]= False
                        elif new_type == None:
                            try:
                                row_dict[new_key]= float(field) # then if it is a number
                                if row_dict[new_key].is_integer(): # it can be integer
                                    row_dict[new_key] = int(field)
                            except:
                                row_dict[new_key] = field # no, it is a string

                    i += 1
                out.append(row_dict)
    return out

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] src_filename.csv src_schema.json")
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--coll", action="store", dest="collect_name", help="collection name")
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

    #schema file
    try:
        filename_schema= args[1]
    except:
        filename_schema= None
    if filename_schema is None:
        filename_schema= args[0].rstrip('.csv')+'-schema.json'

    try:
        sch_src= open(filename_schema, 'rb')
    except:
        "ERROR: Can't open schema file, exiting now"
        exit()

    schema= json.load(sch_src, encoding='utf-8') # schema file
    dbkey_alias= schema["alias"] # dict of aliases -> document keys in db
    dbval_types= schema["type"] # dict of types -> values types in db


    conf_filename= opts.conf_filename
    if conf_filename is None:
        print "ERROR: Can't find configuration, exiting now"
        exit()

    # get mongo connection details
    conn_mongo= get_db_connect(conf_filename, 'mongodb')
    conn_mongo_host= conn_mongo['host']
    conn_mongo_port= conn_mongo['port']
    conn_mongo_db= conn_mongo['database']

    try:
        connect= pymongo.Connection(conn_mongo_host, conn_mongo_port)
        mongo_db= connect[conn_mongo_db]
        print '... connected to the database', mongo_db
    except Exception as e:
        print 'ERROR: Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    conn_mongo_username= conn_mongo['username']
    conn_mongo_password= conn_mongo['password']
    if conn_mongo_password is None:
        conn_mongo_password = getpass.getpass()
    if mongo_db.authenticate(conn_mongo_username, conn_mongo_password) != 1:
        print 'ERROR: Cannot authenticate to db, exiting now'
        exit()

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    try:
        collect_name= opts.collect_name
    except:
        print 'ERROR: No collection name specified!'
        exit()

    csv_delim= ';'
    csv_quote= '"'

    print '... reading and parsing CSV file'
    #parse CSV and save it to dict
    obj_parsed= csv_parse(args[0], filename_schema, csv_delim, csv_quote)

    if len(obj_parsed) != 0:
        obj_final= complete_data(obj_parsed)
    else:
        print "The file %s is empty" % src_file
        exit()

    print '... inserting data to the database'
    print db_insert(obj_final, mongo_db, collect_name, clean_db), 'records in the collection %s' % collect_name

    print 'Done'
        
