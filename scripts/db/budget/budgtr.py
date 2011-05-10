#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
import budzet tradycijny to mongo db
flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

the structure: 1 branch - [czesc] 1:N [dzial] 1:N [rozdzial]

the script also inserts a doc into the schema collection
(warning! if there's already a schema for the budget collection, it should first
be removed manually from the collection data_zz_schema)

the files needed to upload the budget:
- this file (budgtr.py)
- data file CSV, produced from XLS (for example, budgtr.csv)
- schema file JSON (for example, budgtr-schema.json)

type python budgtr.py -h for instructions
"""

import getpass
import os
import optparse
import csv
import pymongo
import simplejson as json
from bson.code import Code


#-----------------------------
def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()


#-----------------------------
def fill_rbt(budg_data, type_label):
    levels= ['a', 'b', 'c', 'd', 'e', 'f']
    out= budg_data[:]

    for row_doc in out:
        if row_doc['parent'] == '':
            row_doc['parent']= None
        row_doc['level']= levels[row_doc['level']]
        if '/' in row_doc['czesc']:
            row_doc['czesc']= row_doc['czesc'].partition('/')[0]
        row_doc['czesc']= int(row_doc['czesc']) #convert to int for the possibility to be compared against 'budzet zadaniowy'
        row_doc['type']= type_label[row_doc['level']] + ' ' + str(row_doc['numer'])
        if row_doc['idef'] == '999999':
            row_doc['type']= 'Total' # specific type
        row_doc['v_nation']= row_doc['dot_sub'] + row_doc['swiad_fiz'] + row_doc['wyd_jednostek'] + row_doc['wyd_majatk'] + row_doc['wyd_dlug'] # recalculate v_nation
        row_doc['v_eu']= row_doc['sw_eu'] + row_doc['wspolfin_eu'] # recalculate v_eu
        row_doc['v_proc_eu']= round(float(row_doc['v_eu']) / float(row_doc['v_total']) * 100, 2) # percentage
        row_doc['v_proc_nation']= round(float(row_doc['v_nation']) / float(row_doc['v_total']) * 100, 2)

    # filling out 'leaf'
    budg_list= out[:]
    for bd in out:
        for bl in budg_list:
            if bl['parent'] == bd['idef']:
                bd['leaf']= False
                break
    return out


#-----------------------------
def csv_parse(csv_read, schema):
    out= []

    dbkey_alias= schema['alias'] # dict of aliases -> document keys in db
    dbval_types= schema['type'] # dict of types -> values types in db
    dbkeys_summ= list(v['key'] for v in schema['columns'] if v.get('checkable')) # the keys whose value should be summarized for grand total
    total_dict= {} # this will become 'total' doc in the collection
    for kk in dbkeys_summ:
        total_dict[kk]= 0

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
                    dict_row[new_key] = field
                elif new_type == "int":
                    if field is None or field == '':
                        dict_row[new_key] = 0 # money shouldn't be null, but 0
                    else:
                        dict_row[new_key] = int(field)
                elif new_type == "float":
                    if '.' in field:
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
                dict_row['type']= None
                dict_row['leaf']= True
                dict_row['v_nation']= 0
                dict_row['v_eu']= 0
                dict_row['v_proc_eu']= 0
                dict_row['v_proc_nation']= 0

                i += 1

            if dict_row['level'] == 0:                
                for k in dbkeys_summ: #totalling here all the summarizable values
                    total_dict[k]= total_dict[k] + dict_row[k]
            out.append(dict_row)

    #complete 'total' dict (some of the keys will anyway be deleted on the 2nd pass)
    total_dict['idef']= '999999'
    total_dict['czesc']= '0'
    total_dict['pozycja']= 0
    total_dict['name']= 'Ogółem'
    total_dict['numer']= ''
    total_dict['parent']= None
    total_dict['leaf']= True
    total_dict['level']= 0
    total_dict['v_nation']= 0
    total_dict['v_eu']= 0
    total_dict['v_proc_eu']= 0
    total_dict['v_proc_nation']= 0

    out.append(total_dict)

    return out


#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser() 
    cmdparser.add_option("-v", "--csv", action="store", dest="csv_filename", help="input file (CSV)")
    cmdparser.add_option("-s", "--schema", action="store",help="schema for CSV file (if none than SRC_FILE-SCHEMA.JSON is used)")
    cmdparser.add_option("-d", "--dbconnect", action="store", help="database and collection to insert to, given as db.collect (no update if not specified!)")
    cmdparser.add_option("-u", "--usr", action="store", help="database admin login")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean before insert (ignored if db is not being updated)")

    opts, args = cmdparser.parse_args()

    try:
        src_file= open(opts.csv_filename, 'rb')
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    csv_delim= ';'
    csv_quote= '"'

    #read CSV file with data
    try:
        csv_read= csv.reader(src_file, delimiter= csv_delim, quotechar= csv_quote)
    except Exception as e:
        print 'Unable to read CSV file:\n %s\n' % e

    #read schema file
    filename_schema= opts.schema
    if filename_schema is None:
        filename_schema= opts.csv_filename.rstrip('.csv')+'-schema.json'
    #deserialize it into the object
    try:
        sch_src= open(filename_schema, 'rb')
        schema= json.load(sch_src, encoding='utf-8') # schema file
    except Exception as e:
        print 'Error in processing schema file:\n %s\n' % e
        exit()


    # create temporary dict
    obj_parsed= csv_parse(csv_read, schema)

    #database settings
    work_db= None #no update if it remain None
    str_dbconnect= opts.dbconnect # database connection string
    dbparam= []
    if str_dbconnect is not None: #parse it
        if '.' in str_dbconnect:
            dbparam= str_dbconnect.split('.', 2)
            dbname= dbparam[0]
            collectname= dbparam[1]
            clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

            mongo_connect= pymongo.Connection("localhost", 27017)
            work_db= mongo_connect[dbname]
            #try to connect and authenticate
            try:
                mongo_connect= pymongo.Connection("localhost", 27017)
                work_db= mongo_connect[dbname]
            except Exception as e:
                print 'Unable to connect to the database:\n %s\n' % e
                exit()
        else:
            print 'Unable to parse dbconnect - wrong format: \n %s\n' % str_dbconnect

    if work_db is not None:
        #username - ask for password
        usrname= opts.usr
        pprompt = getpass.getpass()

        try:
            work_db.authenticate(usrname, pprompt)
        except Exception as e:
            print 'Unable to authenticate to the database:\n %s\n' % e
            exit()

        #meta info - just the labels for types
        meta_info= schema['meta']
        meta_level_label= meta_info['level_label']

        print '-- inserting data into '+ dbname +'.'+ dbname
        mongo_connect.start_request()
        obj_rep= fill_rbt(obj_parsed, meta_level_label) # processing and inserting the data
        print "-- %d records inserted" % db_insert(obj_rep, work_db, collectname, clean_db)

        #meta info
        meta_name= meta_info['name']
        meta_perspective= meta_info['perspective']
        meta_collnum= meta_info['idef']
        meta_explore= meta_info['explorable']
        meta_collection= dict(zip(('idef', 'name', 'perspective', 'collection', 'explorable'), (meta_collnum, meta_name, meta_perspective, collectname, meta_explore)))
        meta_collection['columns']= schema['columns']

        schema_coll= 'md_budg_scheme'
        print '-- updating schema collection', db_insert(meta_collection, work_db, schema_coll, False)

        mongo_connect.end_request()

        print 'Done'
