#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
import:
Budżet środków europejskich w układzie tradycyjnym

flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

bulk of files:
- this file (budgeutr.py)
- data file CSV, produced from XLS (for example, budgeutr.csv)
- conf file with mongo connection settings

type python budgeutr.py -h for instructions
"""

import getpass
import os
import optparse
import csv
import pymongo
import simplejson as json
from ConfigParser import ConfigParser

collection_budgtr= 'dd_budg2011_tr'

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
    format 1-2-3... to 0001-0002-0003...
    src should be convertable to int
    """
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        try:
            res_list.append('%04d' % int(elm))
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
def complete_elt_a(src):
    # filling totals
    rst= {}
    for kk in schema_dict()["type"].items():
        if kk[1] == 'int':
            rst[kk[0]]= src[kk[0]]
    return rst

#-----------------------------
def fill_elt_a(idef):
    # filling program
    return {
        "idef": str(idef),
        "idef_sort": sort_format(str(idef)),
        "parent": None,
        "parent_sort": None,
        "level": "a",
        "type": " ".join(["Program", str(idef)]),
        "leaf": False
        }

#-----------------------------
def fill_elt_b(src, idef_b, parent, db):
    # filling czesc
    idef= "-".join([str(parent), str(idef_b)])
    idef_sort= sort_format(idef)

    # filling Czesc from the collection of traditional budget
    czesc_idef= src["czesc"].strip()
    suppl_idef= ""
    if "/" in czesc_idef:
        czesc_idef= src["czesc"].split("/")[0].strip()
        suppl_idef= src["czesc"].split("/")[1].strip()

    elm_name= db[collection_budgtr].find_one({ "level" : "a", "idef" : czesc_idef }, { "_id": 0, "name": 1 })["name"]
    if len(suppl_idef) > 0:
        elm_name= ": ".join([ elm_name.encode('utf-8'), teryt_dict()[suppl_idef] ])

    return {
        "idef": idef,
        "idef_sort": idef_sort,
        "parent": str(parent),
        "parent_sort": sort_format(str(parent)),
        "name": elm_name,
        "level": "b",
        "type": " ".join(["Część", src["czesc"]]),
        "leaf": True
        }

#-----------------------------
def fill_docs(budg_data, db):
    # format parsed data (list of dicts) for upload
    # add keys: idef, idef_sort, parent, parent_sort, level, leaf

    out= []
    row_dict= {}
    levels= ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    max_level= 0
    idef_level_a= 0
    nss= True # whether a program of NSS (Narodowa Strategia Spójności)
    
    for row_doc in budg_data:
        if len(row_doc['name'].strip()) != 0: # name is not empty, meaning it's either a program name or 'total' field
            idef_level_b= 0
            if "OGółEM" in row_doc['name'].strip().upper():
                row_dict_a.update(complete_elt_a(row_doc))
                row_dict_a["czesc"]= None # no czesc at the level of program
                out.append(row_dict_a)
            elif "OGÓŁEM" in row_doc['name'].strip().upper() and "NSS" in row_doc['name'].strip().upper(): # NSS total
                nss= False
            elif "OGÓŁEM PROGRAMY" in row_doc['name'].strip().upper(): # grand total
                row_dict_a= row_doc.copy()
                row_dict_a['nss']= False
                row_dict_a.update(fill_elt_a("9999"))
                row_dict_a.update(complete_elt_a(row_doc))
                row_dict_a["type"]= "Total"
                row_dict_a["leaf"]= True
                row_dict_a["czesc"]= None
                out.append(row_dict_a)
            else: # ordinary record - start filling it, will fill values upon meeting 'OGółEM'
                idef_level_a += 1
                row_dict_a= row_doc.copy()
                # cleaning names before insert
                row_dict_a['name']= row_dict_a['name'].replace('\n', ' ')
                row_dict_a['name']= row_dict_a['name'].replace('Ŝ', 'ż')
                row_dict_a['nss']= nss
                row_dict_a.update(fill_elt_a(idef_level_a)) # idef, parent, leaf, level, etc.

                # immediately creating and saving elt level b
                idef_level_b += 1
                row_dict_b= row_doc.copy()
                row_dict_b.update(fill_elt_b(row_doc, idef_level_b, idef_level_a, db)) # idef, parent, leaf, level, etc.
                out.append(row_dict_b)
        else: # name is empty, dealing with czesc here
            idef_level_b += 1
            row_dict_b= row_doc.copy()
            row_dict_b.update(fill_elt_b(row_doc, idef_level_b, idef_level_a, db)) # idef, parent, leaf, level, etc.
            row_dict_b['nss']= nss
            out.append(row_dict_b)

    return out

#-----------------------------
def csv_parse(csv_read):
    # parse csv and return dict
    out= []

    schema= schema_dict()
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
                    if field.strip() == '':
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

def schema_dict():
    return {
        "alias": {
            "0":"name",
            "1":"czesc",
            "2":"v_eu",
            "3":"v_nation_fin",
            "4":"v_nation_cofin"
            },
        "type": {
            "czesc": "string",
            "v_eu": "int",
            "v_nation_fin": "int",
            "v_nation_cofin": "int"
            }
        }

def teryt_dict():
    return {
        "02": "Dolnośląskie",
        "04": "Kujawsko-pomorskie",
        "06": "Lubelskie",
        "08": "Lubuskie",
        "10": "Łódzkie",
        "12": "Małopolskie",
        "14": "Mazowieckie",
        "16": "Opolskie",
        "18": "Podkarpackie",
        "20": "Podlaskie",
        "22": "Pomorskie",
        "24": "Śląskie",
        "26": "Świętokrzyskie",
        "28": "Warmińsko-mazurskie",
        "30": "Wielkopolskie",
        "32": "Zachodniopomorskie"
        }

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] src_filename.csv")
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--collt", action="store", dest="collect_name", help="collection name")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

    opts, args = cmdparser.parse_args()

    if len(args) == 0:
        print 'No parameters specified! Type python budgeutr.py -h for help'
        exit()

    try:
        src_file= open(args[0], 'rb')
    except IOError as e:
        print 'ERROR: Unable to open file:\n %s\n' % e
        exit()

    csv_delim= ';' #read CSV file with data
    csv_quote= '"'
    try:
        csv_read= csv.reader(src_file, delimiter= csv_delim, quotechar= csv_quote)
    except Exception as e:
        print 'ERROR: Unable to read CSV file:\n %s\n' % e
        exit()

    conf_filename= opts.conf_filename
    if conf_filename is None:
        print 'No configuration file is specified, exiting now'
        exit()        

    # get mongo connection details
    conn_mongo= get_db_connect(conf_filename, 'mongodb')

    try:
        connect= pymongo.Connection(conn_mongo['host'], conn_mongo['port'])
        mongo_db= connect[conn_mongo['database']]
        print '...connected to the database', mongo_db
    except Exception as e:
        print 'ERROR: Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    if conn_mongo['password'] is None:
        conn_mongo['password'] = getpass.getpass('Password for '+conn_mongo['username']+': ')
    if mongo_db.authenticate(conn_mongo['username'], conn_mongo['password']) != 1:
        print 'ERROR: Cannot authenticate to db, exiting now'
        exit()

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    try:
        collect_name= opts.collect_name
    except:
        pass
    if collect_name is None:
        collect_name= 'dd_budg2011_eutr'
        print 'WARNING! No collection name specified, the data will be stored in the collection %s' % collect_name

    print "...parsing source file"
    obj_parsed= csv_parse(csv_read)
    print "...formatting documents"
    obj_complete= fill_docs(obj_parsed, mongo_db)
    # for obj in obj_complete:
    #     print "%-10s %-10s %5s %-7s %-100s %10d %10d %10d" % (obj['idef_sort'], obj['parent_sort'], obj['level'], obj['leaf'], obj['name'], obj["v_eu"], obj["v_nation_fin"], obj["v_nation_cofin"])
    print '...inserting data -', db_insert(obj_complete, mongo_db, collect_name, clean_db), 'records total'
    print "Done (don't forget about the schema!)"
