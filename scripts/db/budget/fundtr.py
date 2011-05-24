#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
import:
PLANY FINANSOWE PANSTWOWYCH FUNDUSZY CELOWYCH
W UKLADIE TRADYCIJNEM

flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

the script also inserts a doc into the schema collection
(warning! if there's already a schema for the budget collection, it should first
be removed manually from the collection data_zz_schema)

the files needed to upload the budget:
- this file (fundtr.py)
- data file CSV, produced from XLS (for example, fundtr.csv)
- schema file JSON (for example, fundtr-schema.json)

type python fundtr.py -h for instructions
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
    print '-- filling out missing information'

    level_label= ['a','b','c','d','e','f','g']
    deepest_level= 0

    total_frst_popr= 0
    total_plan_nast= 0


    for row_doc in fund_data:
        row_doc['idef_sort']= sort_format(row_doc['idef'])
        row_doc['leaf']= True # for a while, will fill correctly later
        curr_level= row_doc['idef'].count('-') # count of '-' in idef tells about the level
        row_doc['level']= level_label[curr_level]
        if curr_level > deepest_level:
           deepest_level= curr_level

        if row_doc['frst_popr'] is None: # numeric values shouldn't be null
            row_doc['frst_popr']= 0
        if row_doc['plan_nast'] is None:
            row_doc['plan_nast']= 0

        if curr_level > 0: # fill parent
            row_doc['parent']= row_doc['idef'].rpartition('-')[0]
            row_doc['parent_sort']= sort_format(row_doc['parent'])
        else:
            row_doc['parent']= None # no parent at the level a
            row_doc['parent_sort']= None
            total_frst_popr += row_doc['frst_popr'] # calculating totals
            total_plan_nast += row_doc['plan_nast']

        # cleaning names
        row_doc['name']= row_doc['name'].replace('\n', ' ')
        row_doc['name']= row_doc['name'].replace('Ŝ', 'ż')
        
    print '-- !!! deepest_level is', level_label[deepest_level]
    print '-- filling out totals'
    total_doc= {}
    total_doc['idef']= '999999'
    total_doc['idef_sort']= '999999'
    total_doc['parent']= None
    total_doc['parent_sort']= None
    total_doc['level']= 'a'
    total_doc['leaf']= True
    total_doc['type']= 'Total'
    total_doc['name']= 'Ogółem'
    total_doc['paragrafy']= None
    total_doc['frst_popr']= total_frst_popr
    total_doc['plan_nast']= total_plan_nast
    fund_data. append(total_doc)

    # filling leaves
    print '-- correcting leaves'
    fund_data_children= fund_data[:]
    for fund_data_row in fund_data:
        for fund_data_child in fund_data_children:
            if fund_data_row['idef'] == fund_data_child['parent']:
                fund_data_row['leaf']= False
                break

    return fund_data


#-----------------------------
def csv_parse(csv_read, schema):
    print '-- parsing csv file'
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
                        dict_row[new_key] = None
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

                i += 1

            out.append(dict_row)

    return out


#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] source_file.csv source_schema.json") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--collect", action="store",dest='collection_name',help="collection name")
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

    # data collection
    if opts.collection_name is None:
        print 'Collection name not given - the name dd_xxxxyyyy_xx will be used'
        collectname= 'dd_xxxxyyyy_xx'
    else:
        collectname= opts.collection_name

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

    # create temporary dict
    obj_parsed= csv_parse(csv_read, schema)

    # fill it out with real data
    obj_rep= fill_docs(obj_parsed) # processing and inserting the data
    for ii in obj_rep:
        print "%-15s %-20s %-15s %-20s %5s %-7s %-10s %-50s %10d %10d" % (
            ii['idef'], ii['idef_sort'], ii['parent'], ii['parent_sort'], ii['level'], ii['leaf'], ii['type'], ii['name'], ii['plan_nast'], ii['frst_popr']
            )
    print '-- inserting into the db'
    print '-- ', db_insert(obj_rep, db, collectname, clean_db), 'records inserted'

    print 'Done'
