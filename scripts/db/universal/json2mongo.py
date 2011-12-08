#!/usr/bin/python

import simplejson as json
import pymongo
import optparse
import getpass
from ConfigParser import ConfigParser

#-----------------------------
def get_db_connect(fullpath, dbtype):
    connect_dict= {}

    defaults= {
        "basedir": fullpath
    }

    cfg= ConfigParser(defaults)
    cfg.read(fullpath)
    connect_dict["host"]= cfg.get(dbtype,"host")
    connect_dict["port"]= cfg.getint(dbtype,"port")
    connect_dict["database"]= cfg.get(dbtype,"database")
    connect_dict["username"]= cfg.get(dbtype,"username")
    try:
        connect_dict["password"]= cfg.get(dbtype,"password")
    except:
        connect_dict["password"]= None

    return connect_dict

#-----------------------------
def db_insert(data_bulk, collect, dbdel=False, query=None):
    if dbdel: # delete first
        try:
            print "...trying to remove document(s) under given condition"
            collect.remove(query)
            print "...specified documents deleted successfully"
        except Exception as e:
            print "ERROR: cannot remove data:\n %s\n" % e
            return e
        
    try: # insert
        print "...trying to insert document(s)"
        collect.insert(data_bulk, check_keys= False)
        return "...data insert successfully"
    except Exception as e:
        print "Cannot insert data:\n %s\n"
        return e

#-----------------------------
def parse_query(pth):
    result_query= {}

    test_presence= '{' and '}' in pth
    test_order= pth.find('{') < pth.find('}')
    test_count= (pth.count('{') + pth.count('}') == 2)

    if test_presence and test_order and test_count:
        path_elm_list= pth[pth.index('{')+1:-1].split(',')
        if len(path_elm_list) > 0:
            for elm in path_elm_list:
                scope_list= elm.split(':')
                if len(scope_list) == 2: # there is a correctly defined scope
                    qry_key, qry_val= scope_list[0], scope_list[1]
                    if '"' in qry_key:
                        qry_key= qry_key.strip('"')
                    if '"' in qry_val: # string
                        qry_val= str(qry_val.strip('"'))
                    else: # int
                        qry_val= int(qry_val)
                    result_query[qry_key]= qry_val
    else: # ERROR
        result_query['error']= "incorrectly defined query"

    return result_query
    

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] json_file") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-r", "--query", action="store", dest="query", help="query to indetify docs")
    cmdparser.add_option("-l", "--collect", action="store", dest="collect", help="collection name to insert into")
    cmdparser.add_option("-c", action="store_true", dest="rplc", default=False, help="replace documents (delete before insert)")

    opts, args = cmdparser.parse_args()

    try: #file
        src_filename= args[0]
    except:
        print "ERROR: No json filename specified, exiting now!"
        exit()

    try:
        src_file= open(src_filename, 'rb')
    except IOError as e:
        print "ERROR: Unable to read from file:\n %s\n" % e
        exit()

    try: #json object
        json_obj= json.load(src_file, encoding='utf-8')
        print "...JSON file %s successfully de-serialized" % src_filename
    except Exception as e:
        print "ERROR: cannot deserialize json file:\n %s\n" % e
        exit()

    # get connection details
    conn= get_db_connect(opts.conf_filename, "mongodb")
    if conn["password"] is None: #username - ask for password
        conn["password"] = getpass.getpass("MongoDB: provide password for the user %s:" % conn["username"])
    try: # connect
        mongo_conn= pymongo.Connection(conn["host"], conn["port"])
        mongo_db= mongo_conn[conn["database"]]
        print "...connected to MongoDb database", conn["database"]
    except Exception, e:
        print "ERROR: Unable to connect to the MongoDb database:\n %s\n" % e
        exit() #no connection to the database - no data processing

    if mongo_db.authenticate(conn["username"], conn["password"]) == 1:
        print "...successfully authenticated to MongoDB database"
    else:
        print "ERROR: Cannot authenticate to MongoDB, exiting now!"
        exit()

    if opts.collect is None:
        print "ERROR: No collection specified, exiting now!"
        exit()

    del_doc= opts.rplc # action before insert

    query= None
    if opts.query is not None:
        print "...checking query"
        query= parse_query(opts.query)
        if "error" in query:
            print "ERROR: %s, exiting now!" % query["error"]
            exit()

    if query is None and del_doc:
        print "WARNING: no query is specified - the whole collections will be erased before insert!"
        answ= raw_input("Continue? (y/N): ")
        if answ not in ['y', 'yes', 'Yes', 'YES']:
            del_doc= False
            print "...the data will only be inserted!"

    mongo_conn.start_request()
    print db_insert(json_obj, mongo_db[opts.collect], del_doc, query) # processing and inserting the data
    mongo_conn.end_request()

    print "Done"
