#!/usr/bin/python
# -*- coding: utf-8 -*-

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

    #db.add_son_manipulator(NamespaceInjector())

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)

    ffcurr= collect.find({'pos':1}, {"_id":0, 'perspectives.pos':1, 'perspectives.func':1, 'perspectives.name':1, 'perspectives.url':1, 'perspectives.descr':1}).sort('perspectives.pos')

    for ffkey in ffcurr:
        for ffitem in ffkey['perspectives']:
            print ffitem

#data_doc= dict(zip(('pos', 'func', 'name', 'url', 'descr'), (ffitem['pos'], ffitem['func'], ffitem['url'], ffitem['descr'])))

        #data_doc= dict(zip(('pos', 'func', 'name', 'url', 'descr'), (ffkey['perspectives']['pos'], ffkey['perspectives']['func'], ffkey['perspectives']['url'], ffkey['perspectives']['descr'])))
        #print data_doc, '\n'

    return collect.find().count()

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser() 
    cmdparser.add_option("-j", "--json", action="store", dest="json_filename", help="json file")
    cmdparser.add_option("-d", "--dbconnect", action="store", help="mongodb database and collection in a format db.collect (test.src_file if not specified)")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert")

    opts, args = cmdparser.parse_args()

    try:
        f= open(opts.json_filename, 'rb')
        json_src = f.read()
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    try:
        json_obj= json.loads(json_src)
    except Exception as e:
        print 'Unable to read json:\n %s\n' % e
        exit()
    
        #database settings
    str_dbconnect= opts.dbconnect # database connection string
    dbparam= []
    if str_dbconnect is not None: #parse it
        if '.' in str_dbconnect:
            dbparam= str_dbconnect.split('.', 2)
        else:
            print 'Interrupting script: unable to parse dbconnect - wrong format:\n %s\n' % str_dbconnect
            exit()
    else:
        dbparam= 'test', json_filename.rstrip('.json') #use defaults
    
    clean_db_first= opts.dbact # False - insert() data, True - remove() and then insert()

    if len(json_obj) > 0:
        print '... Writing data to the database'
        try:
            rec_count= mongo_update(json_obj, dbparam[0], dbparam[1], clean_db_first)
        except Exception as e:
            print 'Something went wrong while db insert! Check your db settings:\n %s\n' % e
            exit()
    else:
        print 'The file is empty'
        exit()

    print 'Database', dbparam[0]+'.'+dbparam[1], 'updated:', str(rec_count) +' records inserted'
    print 'Done'
