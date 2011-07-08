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

there are 2 nodes:
0 - aggregated
1 - split up to regions

type python fundnfz.py -h for instructions

pay attention to # WARNING! comment!
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
def check_collection(db, collname):
    """ checking created collection for consistency """
    noerrors= True

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
def clean_info(lst, info_idefs, cut_prefix):
    fin_list= lst[:]
    print "...move defined elements to the info key of their parents: %s" % info_idefs
    for info_idef in info_idefs:
        parent_idef= info_idef.rsplit("-",1)[0]
        index_parent, index_info= -1, -1
        i= 0
        print "...looking for idefs: info %s; parent %s" % (info_idef, parent_idef)
        for curr_doc in fin_list:
            if cut_prefix:
                curr_idef= curr_doc["idef"].split("-",1)[1]
            else:
                curr_idef= curr_doc["idef"]

            if curr_idef == parent_idef:
                index_parent= i
                parent_dict= curr_doc
            if curr_idef == info_idef:
                index_info= i
                info_dict= curr_doc
            if index_parent > 0 and index_info > 0: # ok, we've got them both
                break
            i += 1

        if index_parent < 0 and index_info < 0:
            print "ERROR: can't move elements to the info key - impossible to find them and/or their parents!"
        else:
            if parent_dict["info"] is None:
                parent_dict["info"]= []
            print "...setting up info key for element %s" % parent_dict["idef"]
            del info_dict["info"]
            del info_dict["node"]
            parent_dict["info"].append(info_dict)
            del fin_list[index_info]

    return fin_list

#-----------------------------
def split_obj(full_list, info_idefs, cut_prefix):
    """ splits full dict into parts based on TERYT code and send them to clean info """
    result_list= []
    for key in schema["teryt"]:
        temp_list= []
        for elm in full_list:
            if key in elm["idef"]:
                if elm["level"] == 'a':
                    result_list.append(elm)
                else:
                    temp_list.append(elm)
        temp_list= clean_info(temp_list, info_idefs, cut_prefix)
        result_list += temp_list

    return result_list

#-----------------------------
def fill_detail(fund_aggr):
    node_1= []
    teryt_list= schema['teryt']
    for teryt in teryt_list.items():
#         print teryt[0], teryt[1].keys()[0]
        woj_dict= {}
        woj_dict['node']= 1 # node:1 is for data drill down to TERYTs
        woj_dict['leaf']= False
        woj_dict['level']= levels[0] # the highest, the rest will have to move 1 level deeper
        woj_dict['parent']= None
        woj_dict['parent_sort']= None
        curr_teryt= teryt[0]
        curr_woj_key= teryt[1].keys()[0]
        woj_dict['idef']= curr_teryt
        woj_dict['idef_sort']= curr_teryt
        woj_dict['type']= curr_teryt
        woj_dict['name']= teryt[1].values()[0]
        woj_dict['val']= 0 # until we find a proper total
        for aggr_row in fund_aggr:
            if aggr_row['idef'] == 'I': # total
                woj_dict['val']= aggr_row[curr_woj_key]
                continue
            new_dict= {}
            new_dict['idef']= curr_teryt + '-' + aggr_row['idef']
            new_dict['idef_sort']= curr_teryt + '-' + aggr_row['idef_sort']
            if aggr_row['parent'] is None:
                new_dict['parent']= curr_teryt
                new_dict['parent_sort']= curr_teryt
            else:
                new_dict['parent']= curr_teryt + '-' + aggr_row['parent']
                new_dict['parent_sort']= curr_teryt + '-' + aggr_row['parent_sort']
            new_dict['node']= 1
            new_dict['leaf']= aggr_row['leaf'] # leaves remain unchanged
            new_dict['level']= levels[levels.index(aggr_row['level'])+1] # 1 level deeper
            new_dict['type']= aggr_row['type']
            new_dict['name']= aggr_row['name']
            new_dict['val']= aggr_row[curr_woj_key]
            new_dict['info']= None
            node_1.append(new_dict)

        node_1.append(woj_dict)

    return node_1

#-----------------------------
def fill_docs(fund_data):
    # format parsed data (dict) for upload

    # add keys: idef, idef_sort, parent, parent_sort, level, leaf, node, osrodki_wojewodzkie (count total)
    work_list= fund_data[:]
    max_level= 0
    for row_doc in work_list:
        row_doc['node']= 0 # node:0 is for aggregated data
        row_doc['idef']= row_doc['type'].replace('.', '-')
        row_doc['idef_sort']= sort_format(row_doc['idef'])
        dash_count= row_doc['idef'].count('-')
        row_doc['leaf']= True # default, being filled below
        row_doc['level']= levels[dash_count]
        if dash_count > max_level:
            max_level= dash_count
        row_doc['parent']= None
        row_doc['parent_sort']= None
        if dash_count != 0:
            row_doc['parent']= row_doc['idef'].rsplit('-', 1)[0]
            row_doc['parent_sort']= sort_format(row_doc['parent'])
        row_doc['osrodki_wojewodzkie']= row_doc['dolnoslaskie']+row_doc['kujawskopomorskie']+row_doc['lubelski']+row_doc['lubuski']+row_doc['lodzki']+row_doc['malopolski']+row_doc['mazowiecki']+row_doc['opolski']+row_doc['podkarpacki']+row_doc['podlaski']+row_doc['pomorski']+row_doc['slaski']+row_doc['swietokrzyski']+row_doc['warminskomazurski']+row_doc['wielkopolski']+row_doc['zachodniopomorski']

    print '...info: aggregated data - max level is', levels[max_level]

    return work_list


#-----------------------------
def csv_parse(csv_read):
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
                dict_row['info']= None

                i += 1

            out.append(dict_row)

    return out


#-----------------------------
if __name__ == "__main__":
    # globals & defaults
    schema= {}
    levels= ['a','b','c','d','e','f','g','h']

    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] src_filename.csv src_schema.json")
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--collt", action="store", dest="collect_name", help="collection name")
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
    try:
        connect= pymongo.Connection(conn_mongo['host'], conn_mongo['port'])
        mongo_db= connect[conn_mongo['database']]
        print '...connected to the database', mongo_db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()
    # authentication
    if conn_mongo['password'] is None:
        conn_mongo['password'] = getpass.getpass('Password for '+conn_mongo['username']+': ')
    if mongo_db.authenticate(conn_mongo['username'], conn_mongo['password']) != 1:
        print 'Cannot authenticate to db, exiting now'
        exit()

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    try:
        collect_name= opts.collect_name
    except:
        collect_name= 'dd_fund2011_nfz'
        print 'WARNING! No collection name specified, the data will be stored in the collection %s' % collect_name

    print "...parsing source file"
    obj_parsed= csv_parse(csv_read)
    print "...formatting documents"
    obj_aggr= fill_docs(obj_parsed)
    obj_detl= fill_detail(obj_aggr)

    # WARNING! pecularity: move defined elements to the info key of their parents
    info_idef_list= ["A-3-1", "A-14-1", "D-3-1-1"]
    obj_aggr= clean_info(obj_aggr, info_idef_list, cut_prefix=False)
    obj_detl= split_obj(obj_detl, info_idef_list, cut_prefix=True)

    print '...inserting into db aggregated data -', db_insert(obj_aggr, mongo_db, collect_name, clean_db), 'records total'
    print '...inserting into db detailed data -', db_insert(obj_detl, mongo_db, collect_name, False), 'records total'

    print '...checking data consistency'
    if check_collection(mongo_db, collect_name):
        print '...no inconsistencies have been found'
    else:
        print '...inconsistencies have been found in the collection %s - check your data' % collect_name
    
    print "Done (don't forget about the schema!)"
