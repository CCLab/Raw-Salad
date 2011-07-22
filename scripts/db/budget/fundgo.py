#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
import Funduszy Celowe w ukladie Zadaniowy to mongoDB

the structure:
flat structure (each data unit is a separate doc in the collection),
  parenting is archieved through 'parent' key
Cel & Miernik are subtrees of a parent (parents can be Zadanie & Podzadanie),
  stored in the 'info' key of the element

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

    success= True
    try:
        collect.insert(data_bulk)
    except Exception as e:
        success= False
        print 'Cannot insert data:\n %s\n' % e

    return success


#-----------------------------
def check_collection(db, collname, dict_de):
    """ checking created collection for consistency """
    noerrors= True

    # first filling out "info" keys
    print '...filling info key'
    for curr_dict in dict_de:
        if curr_dict["type"] == "Cel":
            lookup= curr_dict["parent"]
        elif curr_dict["type"] == "Miernik":
            lookup= curr_dict["parent"].rsplit("-",1)[0]
        else:
            print "--! inconsistency found! Info element %s with unproper type: %s" % (curr_dict["idef"], curr_dict["type"])
            break

        curr_parent= db[collname].find({'idef':lookup})
        if curr_parent.count() > 0:
            for cp in curr_parent:
                #setting up level
                if curr_dict["type"] == "Cel":
                    lv_index= 1
                elif curr_dict["type"] == "Miernik":
                    lv_index= 2
                curr_dict["level"]= levels[levels.index(cp["level"])+lv_index]
                
                if cp["info"] is None: cp["info"]= [] # first insert
                cp["info"].append(curr_dict)
                db[collname].save(cp, safe=True)
        else:
            print "--! inconsistency found! Info element %s doesn't have a parent: %s" % (curr_dict["idef"], curr_dict["parent"])

    # set 'leaf' to False if an element have children, 'leaf':True otherwise
    null_leaf_curr= db[collname].find()
    for row in null_leaf_curr:
        curr_idef= row['idef']
        if db[collname].find({'parent':curr_idef}).count() > 0:
            leaf_status= False
        else:
            leaf_status= True
        if row['leaf'] != leaf_status:
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
def clean_text(text_in):
    """ text goes through .replace('\n', ' ') and .replace('Ŝ', 'ż') """
    text_in= text_in.replace('\n', ' ')
    text_in= text_in.replace('  ', ' ')
    text_in= text_in.replace('Ŝ', 'ż')
    return text_in

#-----------------------------
def fill_val(dict_from):
    """ copy all integer vals from src to the result dict """

    dict_to= {}
    int_list= [k for k,v in schema["type"].iteritems() if v == "int"]
    for key in int_list:
        val= dict_from[key]
        if val is None:
            val= 0
        dict_to[key]= val
    
    return dict_to

#-----------------------------
def fill_a(src_dict):
    """ fill first level - FUNDUSZ """

    idef= src_dict["idef"].strip()
    result_dict= {
        "idef": idef,
        "idef_sort": sort_format(idef),
        "parent": None,
        "parent_sort": None,
        "level": "a",
        "leaf": False,
        "name": clean_text(src_dict["fundusz"]),
        "type": " ".join([type_str, idef])
        }
    result_dict.update(fill_val(src_dict))

    return result_dict

#-----------------------------
def fill_b(src_dict):
    """ fill second level - Zadanie """

    idef= src_dict["idef"].strip()
    parent= idef.rsplit("-",1)[0]
    numer= idef.replace("-",".")
    result_dict= {
        "idef": idef,
        "idef_sort": sort_format(idef),
        "parent": parent,
        "parent_sort": sort_format(parent),
        "level": "b",
        "leaf": False, # for a while, this will be "fixed" later if necessary
        "name": clean_text(src_dict["zadanie"]),
        "type": " ".join(["Zadanie", numer])
        }
    result_dict.update(fill_val(src_dict))

    return result_dict

#-----------------------------
def fill_c(src_dict):
    """ fill third level - Podzadanie """

    idef= src_dict["idef"].strip()
    parent= idef.rsplit("-",1)[0]
    numer= idef.replace("-",".")
    result_dict= {
        "idef": idef,
        "idef_sort": sort_format(idef),
        "parent": parent,
        "parent_sort": sort_format(parent),
        "level": "c",
        "leaf": True, # for a while, this will be "fixed" later if necessary
        "name": clean_text(src_dict["podzadanie"]),
        "type": " ".join(["Podzadanie", numer])
        }
    result_dict.update(fill_val(src_dict))

    return result_dict

#-----------------------------
def fill_cel(src_dict, idef_cnt):
    """ fill level of Cel (for info key) """

    parent= src_dict["idef"].strip()
    idef= "-".join([ parent, str(idef_cnt) ])
    result_dict= {
        "idef": idef,
        "idef_sort": sort_format(idef),
        "parent": parent,
        "parent_sort": sort_format(parent),
        "level": None, # for a while, will fiil it on the last stage
        "leaf": False, # Cel can't be leaf
        "name": clean_text(src_dict["cel"]),
        "type": "Cel"
        }

    return result_dict

#-----------------------------
def fill_miernik(src_dict, parent, idef_cnt):
    """ fill level of Miernik (for info key) """

    idef= "-".join([ parent, str(idef_cnt) ])
    result_dict= {
        "idef": idef,
        "idef_sort": sort_format(idef),
        "parent": parent,
        "parent_sort": sort_format(parent),
        "level": None, # for a while, will fiil it on the last stage
        "leaf": True, # Miernik is always leaf
        "name": clean_text(src_dict["miernik"]),
        "type": "Miernik",
        "miernik_wartosc_bazowa": clean_text(str(src_dict["miernik_wartosc_bazowa"])),
        "miernik_wartosc_2011": clean_text(str(src_dict["miernik_wartosc_2011"])),
        "miernik_wartosc_2012": clean_text(str(src_dict["miernik_wartosc_2012"])),
        "miernik_wartosc_2013": clean_text(str(src_dict["miernik_wartosc_2013"]))
        }

    return result_dict

#-----------------------------
def fill_levels(raw_list):
    """ first pass: create 2 separate lists of dicts:
    1. core data structure (Fund, Zadanie, Podzadanie)
    2. list of Cel & Miernik with the parent info """

    out_tree, out_info= [], []
    total_dict= {}
    count_d, count_e= 1, 1 
    for elt in raw_list:

        curr_dict_tree= {} # dict for main data (levels a, b, c)
        curr_dict_info= {} # dict for info list (d, e)

        # filling a, b, c
        if elt['test_f'] == 1: # level 'a' FUNDUSZ
            curr_dict_tree= fill_a(elt)
            # counting totals on the highest level
            if len(total_dict) == 0: # first pass, it's empty
                total_dict= fill_val(curr_dict_tree)
            else: # summarizing
                curr_val= fill_val(curr_dict_tree)
                for k in total_dict:
                    total_dict[k] += curr_val[k]
        elif elt['test_z'] == 1: # level 'b' Zadanie
            curr_dict_tree= fill_b(elt)
        elif elt['test_p'] == 1: # level 'c' Podzadanie
            curr_dict_tree= fill_c(elt)

        if len(curr_dict_tree) > 0: # updating result only if it's level a, b, or c
            curr_dict_tree["info"]= None # info should be present even if there's no Cel & Miernik
            out_tree.append(curr_dict_tree)
            count_d= 1 # if it's a, b or c, it definitely has a new Cel


        # filling d, e
        if elt['test_c'] == 1: # info level 'd' Cel
            if elt['test_z'] == 0 and elt['test_p'] == 0: # meanin' it's Cel only
                count_d += 1
            curr_dict_info= fill_cel(elt, count_d)
            curr_cel_idef= curr_dict_info["idef"]
            count_e= 1 # if it's a new Cel, it will definitely have a new Miernik
            if len(curr_dict_info) > 0: # updating result only if it's level d
                out_info.append(curr_dict_info)

        if elt['test_m'] == 1: # info level 'e' Miernik
            if elt['test_z'] == 0 and elt['test_p'] == 0 and elt['test_c'] == 0: # meanin' it's Miernik only
                count_e += 1
            curr_dict_info= fill_miernik(elt, curr_cel_idef, count_e)
            if len(curr_dict_info) > 0: # updating result only if it's level e
                out_info.append(curr_dict_info)

    # ordinary keys in total dict
    total_dict.update({
        "idef": "9999",
        "idef_sort": "9999",
        "parent": None,
        "parent_sort": None,
        "level": "a",
        "leaf": True,
        "name": "OGÓŁEM",
        "type": "Total"
        })
    out_tree.append(total_dict) # total doc

    return out_tree, out_info

#-----------------------------
def csv_parse(csv_read):
    # parse csv data and put in into the dictionary
    out= []

    dbkey_alias= schema["alias"] # dict of aliases -> document keys in db
    dbval_types= schema["type"] # dict of types -> values types in db

    total_val_2011, total_val_2012, total_val_2013= 0,0,0 # for totals

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

            dict_row['info']= None # filling only for those who have info key

            out.append(dict_row)

    return out

#-----------------------------
if __name__ == "__main__":
    # globals & defaults
    schema= {}
    type_str= 'ELEMENT'
    levels= ['a','b','c','d','e','f','g','h']

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

    try:
        connection= pymongo.Connection(conn['host'], conn['port'])
        db= connection[conn['database']]
        print '...connected to the database', db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    # authentication
    if conn['password'] is None:
        conn['password'] = getpass.getpass()
    if db.authenticate(conn['username'], conn['password']) != 1:
        print 'Cannot authenticate to db, exiting now'
        exit()

    # data & meta-data collections
    # data collection
    if opts.collection_name is None:
        print 'Collection name not given - the name dd_xxxxyyyy_xx will be used'
        coll_data= 'dd_xxxxyyyy_xx'
    else:
        coll_data= opts.collection_name

    if coll_data.find('agnc') <> -1:
        type_str= 'AGENCJA'
    elif coll_data.find('fund') <> -1:
        type_str= 'FUNDUSZ'

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

    obj_parsed= csv_parse(csv_read) # fill data table
    obj_struct, obj_info= fill_levels(obj_parsed)
    # for obj in obj_info:
    #     print "%-10s %-8s %5s %-20s %-80s" % (obj['idef'], obj['parent'], obj['level'], obj['type'], obj['name'])

    if db_insert(obj_struct, db, coll_data, clean_db):
        print '...the data successfully inserted to the collection %s' % coll_data

    print '...checking data consistency'

    if check_collection(db, coll_data, obj_info):
        print '...no inconsistencies have been found in the collection %s' % coll_data
    else:
        print '...inconsistencies have been found in the collection %s - check your data' % coll_data

    print "Done (don't forget about the schema!)"
