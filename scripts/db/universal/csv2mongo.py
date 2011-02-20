#!/usr/bin/python

"""
parse and import polls CSV dumps into:
1. MongoDB (all collections are being automatically created)
2. External JSON file

Required: MongoDB 1.6.5 or higher, server should be started (./mongod)

Please, consult >>python csv2mongo.py --help
"""

import optparse
import csv
import simplejson as json
import itertools
import pymongo
from pymongo.son_manipulator import NamespaceInjector

#-----------------------------------------------
# insert data into specified mongo db and collection
def mongo_update(data_bulk, dbname, collname, clean_first=False):
    db= pymongo.Connection("localhost", 27017)[dbname]
    collect= db[collname]

    db.add_son_manipulator(NamespaceInjector())

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()


#-----------------------------------------------
# parse CSV, convert it to JSON and save to file
def csv_parse(filename_csv, filename_schema, delimit, quote, jsindent):
    out= []

    if filename_schema == None:
        filename_schema= filename_csv.rstrip('.csv')+'-schema.json'
    try:
        csv_src= open(filename_csv, 'rb')
        sch_src= open(filename_schema, 'rb')
    except IOError as e:
        print 'Unable to open src_file:\n %s\n' % e
    else:
        csv_read= csv.reader(csv_src, delimiter= delimit, quotechar= quote)
        
        schema= json.load(sch_src, encoding='utf-8') # schema file
        dbkey_alias= schema["alias"] # dict of aliases -> document keys in db
        dbval_types= schema["type"] # dict of types -> values types in db

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
    cmdparser = optparse.OptionParser() 
    cmdparser.add_option("--src",action="store",help="input CSV file (required)")
    cmdparser.add_option("--sch",action="store",help="schema for CSV file (if none than SRC_FILE-SCHEMA.JSON is used)")
    cmdparser.add_option("--dbconnect",action="store",help="mongodb database and collection in a format db.collect (test.src_file if not specified)")
    cmdparser.add_option("--c",action="store_true",dest='dbact',help="clean db before insert")
    cmdparser.add_option("--json",action="store",help="output JSON filename (use --json=1 for SRC_FILE.JSON)")
    cmdparser.add_option("--i",action="store",dest='indent',help="indent in JSON file (number of spaces)")

    opts, args = cmdparser.parse_args()

    if opts.src is not None:
        filename_csv= opts.src

        if opts.json is None or opts.json == '1':
            filename_json= filename_csv.rstrip('.csv')+'.json'
        else:
            filename_json= opts.json

        indt= opts.indent
        if indt is not None:
            indt= int(indt)

        #database settings
        str_dbconnect= opts.dbconnect # database connection string
        dbparam= []
        if str_dbconnect is not None: #parse it
            if '.' in str_dbconnect:
                dbparam= str_dbconnect.split('.', 2)
            else:
                print 'Interrupting script: unable to parse dbconnect - wrong format:\n %s\n' % str_dbconnect
        else:
            dbparam= 'test', filename_csv.rstrip('.csv') #use defaults
    
        clean_db_first= opts.dbact # False - insert() data, True - remove() and then insert()

        csv_delim= ';'
        csv_quote= '"'
    
        print '... Processing CSV file'
        csv_data_parsed= csv_parse(filename_csv, opts.sch, csv_delim, csv_quote, indt) #parse CSV and save it to dict

        if len(csv_data_parsed) > 0:
            if opts.json is not None: # json file write
                print '... Creating JSON file'
                json_write= open(filename_json, 'w')
                print '... Writing data to JSON file'
                print >>json_write, json.dumps(csv_data_parsed, indent=indt, ensure_ascii= False)
                json_write.close()
                print "JSON file saved:", filename_json
                
            if len(dbparam) > 0: # insert to db
                print '... Writing data to the database'
                try:
                    rec_count= mongo_update(csv_data_parsed, dbparam[0], dbparam[1], clean_db_first)
                except:
                    print 'Interrupting script: something went wrong while db insert! Check your db settings:\n %s\n' % str_dbconnect
                finally:
                    print 'Database', dbparam[0]+'.'+dbparam[1], 'updated:', str(rec_count) +' records inserted'
            print 'Done'
        else:
            print 'The file is empty'
