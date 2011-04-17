#!/usr/bin/python

import simplejson as json
import pymongo
import optparse
import getpass

#-----------------------------
def db_insert(data_bulk, collect, **parms):
    #params
    clean= parms.pop('clean', False) 
    condition_k= parms.pop('condition_k', None)
    condition_v_raw= parms.pop('condition_v', None)
    if parms: 
        raise TypeError("Unsupported configuration options %s" % list(parms))

    condition_v= None
    try:
        if '.' in condition_v_raw:
            condition_v= float(condition_v_raw)
        elif ',' in condition_v_raw:
            condition_v= float(condition_v_raw)
        else:
            condition_v= int(condition_v_raw)
    except:
        condition_v= str(condition_v_raw)
    condition= dict({condition_k : condition_v})
    if clean: # delete first
        try:
            if condition is not None:
                print '...removing document(s) under condition', condition
                collect.remove(condition, safe=True)
                print "...specified documents deleted successfully"
        except Exception as e:
            print 'Cannot delete data under:\n %s\n' % e
            return e
        
    try: # insert
        collect.insert(data_bulk, check_keys= False)
        return "...data insert successfully"
    except Exception as e:
        print 'Cannot insert data:\n %s\n'
        return e


#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] json_file database.collection") 
    cmdparser.add_option("-H", "--host", action="store", default="localhost", help="host [default: %default]")
    cmdparser.add_option("-p", "--port", action="store", default=27017, help="port to connect to the database [default: %default]")
    cmdparser.add_option("-u", "--user", action="store", help="database user login (must have rights of admin)")
    cmdparser.add_option("-w", "--password", action="store", help="user password")
    cmdparser.add_option("-c", action="store_true", dest='dbact', default=False, help="clean before insert")

    opts, args = cmdparser.parse_args()

    try: #file
        src_file= open(args[0], 'rb')
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    try: #json object
        json_obj= json.load(src_file, encoding='utf-8')
    except Exception as e:
        print 'Error in deserializing json file:\n %s\n' % e
        exit()

    conn_host= opts.host #database
    try:
        conn_port= int(opts.port)
    except Exception as e:
        print 'Error in connection details:\n %s\n' % e
        exit()

    str_dbconnect= args[1] # database connection string
    db_name= None
    dbparam= []
    if str_dbconnect is not None: #parse it
        if '.' in str_dbconnect:
            dbparam= str_dbconnect.split('.', 2)
            db_name= dbparam[0]
            db_coll= dbparam[1]
        else:
            print 'Unable to parse dbconnect - wrong format: \n %s\n' % str_dbconnect
            exit()
    if db_name is not None:
        db_user= opts.user
        db_pswd= opts.password
        if db_pswd is None:
            db_pswd = getpass.getpass()
    else:
        exit()

    try: # connection
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[db_name]
        print '...connected to the database', db_name
    except Exception as e:
        print 'Unable to connect to the database:\n %s\n' % e
        exit()

    if db.authenticate(db_user, db_pswd): # authentication
        collection= db[db_coll]
    else:
        print 'Cannot authenticate to the database with given username and password!'
        exit()

    db_act= opts.dbact # action before insert
    cond= None
    while cond is None:
        cond= raw_input('Provide condition for db.collection.find() in a form key=value:')
    cond= cond.split('=', 2)

    print '...inserting data into', str_dbconnect
    conn.start_request()
    print db_insert(json_obj, collection, clean=db_act, condition_k=cond[0], condition_v=cond[1]) # processing and inserting the data
    conn.end_request()

    print 'Done'
