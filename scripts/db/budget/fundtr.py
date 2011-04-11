#!/usr/bin/python

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
from bson.code import Code


#-----------------------------
def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()


#-----------------------------
def fill_docs(fund_data, type_label, db, coll, cleandb):
    
    fund_list= []
    for row_doc in fund_data:
        if row_doc['leaf']: #change leaf to boolean
            row_doc['leaf']= True
        else:
            row_doc['leaf']= False

        curr_level= row_doc['idef'].count('-') # count of '-' in idef tells about the level
        row_doc['level']= type_label[curr_level]

        if curr_level > 0: # fill parent
            row_doc['parent']= row_doc['idef'].rpartition('-')[0]
            if row_doc['frst_popr'] is None: # numeric values on the lover levels shouldn't be null
                row_doc['frst_popr']= 0
            if row_doc['plan_nast'] is None:
                row_doc['plan_nast']= 0
        else:
            row_doc['parent']= None # no parent at the level a
            row_doc['frst_popr']= None # numeric values on the highest level should be null
            row_doc['plan_nast']= None

        fund_list.append(row_doc)

    print '-- ', db_insert(fund_list, db, coll, cleandb), 'records inserted'
    return fund_list


#-----------------------------
def csv_parse(csv_read, schema):
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
                #additional fields
                dict_row['parent']= None

                i += 1

            out.append(dict_row)

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
    cmdparser.add_option("-j", "--json", action="store", dest="json_filename", help="store to json file (CSV)")

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

        if not work_db.authenticate(usrname, pprompt):
            print 'Fatal error: Unable to authenticate to the db \nExiting now'
            exit()

        level_label= ['a','b','c','d','e','f','g']
        obj_rep= fill_docs(obj_parsed, level_label, work_db, collectname, clean_db) # processing and inserting the data

        #meta info - just the labels for types
        meta_info= schema['meta']

        #meta info
        meta_name= meta_info['name']
        meta_perspective= meta_info['perspective']
        meta_collnum= meta_info['idef']
        meta_explore= meta_info['explorable']
        meta_collection= dict(zip(('idef', 'name', 'perspective', 'collection', 'explorable'), (meta_collnum, meta_name, meta_perspective, collectname, meta_explore)))
        meta_collection['columns']= schema['columns']

        schema_coll= 'md_fund_scheme'
        print '-- inserting meta-data into '+ dbname +'.'+ schema_coll
        mongo_connect.start_request()
        print '-- updating schema collection', db_insert(meta_collection, work_db, schema_coll, False)

        mongo_connect.end_request()

        # saving into json file
        if opts.json_filename is not None:
            try:
                json_write= open(opts.json_filename, 'w')
            except IOError as e:
                print 'Unable to open file:\n %s\n' % e
                exit()

            full_data= {}

            cursor_data= work_db[collectname].find({},{'_id':0})
            rows= [] # first save the result into the list
            for row in cursor_data:
                rows.append(row)

            full_data['rows']= rows

            meta_data= work_db[schema_coll].find_one({'idef':meta_collnum},{'_id':0})
            for k in meta_data:
                full_data[k]= meta_data[k]

            try:
                print >>json_write, json.dumps(full_data, indent=4)
            except IOError as writerr:
                print 'Unable to save out_file:\n %s\n' % writerr
                exit()

            src_file.close()
            json_write.close()
            print "File saved: " + opts.json_filename

        print 'Done'
