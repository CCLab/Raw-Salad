#!/usr/bin/python

import optparse
import csv
import pymongo
import simplejson as json


def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()



# FILL THE DATA

def fill_z_d_c_mier(db, cllname, clltmp):
    out= []

    collmain= db[cllname]
    collmn= db[cllname]
    colltmp= db[clltmp]
    collcrr_dysp= collmain.find({"level":"c", "node":1}, {"idef":1, "parent":1, "czesc":1, "name":1, "_id":0}) # first getting the list of "dysponents" and their parents
    for row in collcrr_dysp:
        zd_curr= row['parent'] # current "zadanie"
        ds_curr= row['idef'] # current "dysponent"
        ds_name= row['name'] # current "dysponent" name
        ds_czesc_curr= row['czesc'] # current "czesc"

        cl_d_num= 0
        # BOOKMARK
        # 3 levels processing here:
        # 1) 'test_z_d'=True && 'test_z_c'=True && 'test_z_m'=True
        # 2) 'test_z_d'=False && 'test_z_c'=True && 'test_z_m'=True (use zd_curr & ds_czesc_curr to identify 'cel')
        # 3) 'test_z_d'=False && 'test_z_c'=False && 'test_z_m'=True (how to identify 'cel' here???!!!)

    return out


def fill_z_d_cel(db, cllname, clltmp):
    out= []

    collmain= db[cllname]
    colltmp= db[clltmp]
    collcrr_dysp= collmain.find({"level":"c", "node":1}, {"idef":1, "parent":1, "czesc":1, "name":1, "_id":0}) # first getting the list of "dysponent" and their parents
    for row in collcrr_dysp:
        zd_curr= row['parent'] # current "zadanie"
        ds_curr= row['idef'] # current "dysponent"
        ds_name= row['name'] # current "dysponent" name
        ds_czesc_curr= row['czesc'] # current "czesc"
        
        cl_d_num= 0
        collcrr_z_c= colltmp.find({'numer':zd_curr, 'dysponent':ds_name, "test_z_d":True, "test_z_c":True}, {"_id":0}) # first processing records of both "cel" & "dysponent"
        for row_z_c in collcrr_z_c:
            ffc= {}
            ffc['name']= row_z_c['cel']
            cl_d_num += 1
            full_cl_d_num= ds_curr + '.' + str(cl_d_num)
            ffc['idef']= full_cl_d_num
            ffc['type']= 'Zadanie - cel'
            ffc['parent']= ds_curr # idef of "dysponent"
            ffc['node']= 1 # "cel" follows the direction of "dysponent"
            ffc['level']= 'd'
            ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            ffc['y2011_total']= None # no values on the level of "cel"
            ffc['y2011_state']= None
            ffc['y2011_eu']= None

            out.append(ffc)

        collcrr_z_c= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, "test_z_d":False, "test_z_c":True}, {"_id":0}) # now "cel" without "dysponent"
        for row_z_c in collcrr_z_c:
            print row_z_c
            ffc= {}
            ffc['name']= row_z_c['cel']
            cl_d_num += 1
            full_cl_d_num= ds_curr + '.' + str(cl_d_num)
            ffc['idef']= full_cl_d_num
            ffc['type']= 'Zadanie - cel'
            ffc['parent']= ds_curr # idef of "dysponent"
            ffc['node']= 1 # "cel" follows the direction of "dysponent"
            ffc['level']= 'd'
            ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            ffc['y2011_total']= None # no values on the level of "cel"
            ffc['y2011_state']= None
            ffc['y2011_eu']= None

            out.append(ffc)

    return out

def fill_z_dysponent(db, colltmp, objlst):
    out= objlst[:]

    collect= db[colltmp]
    collcrr_zdnum= collect.find({"test_z":True}, {"numer":1,"_id":0}) # collecting the numbers of "zadanie"
    for row in collcrr_zdnum:
        zd_curr= row['numer'] # current "zadanie"
        zd_d_num= 0
        collcrr_z_d= collect.find({'numer':zd_curr, "test_z_d":True}, {"_id":0}) # getting "dysponent" of current "zadanie"
        for row_z_d in collcrr_z_d:
            fzd= {}
            zd_d_num += 1
            full_zd_d_num= row_z_d['numer'] + '.' + str(zd_d_num)
            fzd['idef']= full_zd_d_num
            fzd['type']= 'Zadanie - dysponent'
            fzd['name']= row_z_d['dysponent']
            fzd['parent']= row_z_d['numer'] # idef of "zadanie"
            fzd['node']= 1 # "dysponent" has a direction
            fzd['level']= 'c'
            fzd['czesc']= row_z_d['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            fzd['y2011_total']= row_z_d['ogolem'] # this is the last object
            fzd['y2011_state']= row_z_d['budzet_panstwa']
            fzd['y2011_eu']= row_z_d['budzet_srodkow_europejskich']

            out.append(fzd)

    return out


def fill_zadanie(db, colltmp, objlst):
    out= objlst[:]
    collect= db[colltmp]
    colltmpcrr= collect.find({"test_z":True}, {"_id":0}) # looking only for "zadanie"

    for row in colltmpcrr:
        tmpdict= dict(row)
        ffz= {}
        ffz['idef']= tmpdict['numer']
        zd_type_name= tmpdict['funkcja_zadanie'].rsplit('.', 2) # extract "funkcja_zadanie"
        ffz['type']= 'Zadanie ' + zd_type_name[0].strip() + '.' + zd_type_name[1].strip()
        ffz['name']= zd_type_name[2].strip()
        ffz['parent']= zd_type_name[0].strip() # idef of "zadanie"
        ffz['node']= None # "zadanie" is not a root, but it still doesn't have a 'direction'
        ffz['level']= 'b' # 2nd level in the hierarchy
        ffz['y2011_total']= None # no info about money on that level, in case of necessity can be summarized via map/reduce in mongo
        ffz['y2011_state']= None
        ffz['y2011_eu']= None

        out.append(ffz)

    return out


def fill_funkcja(db, colltmp):
    out= []
    collect= db[colltmp]
    colltmpcrr= collect.find({"test_f":True}, {"_id":0}) # looking only for "funkcja"
    for row in colltmpcrr:
        frr= row.copy()
        frr= dict(frr)
        for k, v in row.iteritems():
            if v is None or k.startswith('test_'): # delete records with empty values and keys of test matrix
                frr.pop(k)
        frr['idef']= frr.pop('numer') # change "numer" to "identifier"
        funk_type_name= frr.pop('funkcja_zadanie').split('.', 2) # extract "funkcja_zadanie"
        if frr['idef'] == '999999':
            frr['type']= 'total'
            frr['name']= funk_type_name[0].strip()
        else:
            frr['type']= funk_type_name[0].strip()
            frr['name']= funk_type_name[1].strip()
        frr['parent']= None # "funkcja" is the root
        frr['node']= None # "funkcja" doesn't have a 'direction'
        frr['level']= 'a' # the highest level in the hierarchy
        frr['y2011_total']= frr.pop('ogolem') # change "ogolem" to "total" of the current year
        frr['y2011_state']= frr.pop('budzet_panstwa') # the same for state budget
        frr['y2011_eu']= frr.pop('budzet_srodkow_europejskich') # the same for EU part in the budget
        
        out.append(frr)

    return out


def fill_rep(db, colltmp, collname, cleandb):
    out= []
    # filling containers for all kinds of data successively
    dict_funk= fill_funkcja(db, colltmp) # "funkcja"
    dict_zadanie= fill_zadanie(db, colltmp, dict_funk) # "zadanie"
    dict_zd_dysp= fill_z_dysponent(db, colltmp, dict_zadanie) # "dysponent"
      #and this is precisely the moment to insert the first bulk of data into the db,
      #'cause there are docs with artificially created identifiers
    print "-- inserted funkcja-zadanie-dysponent:", db_insert(dict_zd_dysp, db, collname, cleandb)
    dict_zd_dysp_cel= fill_z_d_cel(db, collname, colltmp) # "cel" (we need both updated "collname" and "colltmp" here)
    print "-- inserted cel:", db_insert(dict_zd_dysp_cel, db, collname, False) # insert the dict with "cel" (append, no db clean!)
    dict_zd_dysp_cel_mr= fill_z_d_c_mier(db, collname, colltmp) # "miernik" (we need both updated "collname" and "colltmp" here)
    # get the data from db and return for json file
    out= dict_zd_dysp
    return out


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

                if len(field.strip()) == 0:
                    dict_row[keys[i]]= None
                else:
                    if new_type == "string":
                        dict_row[new_key] = field
                    elif new_type == "int":
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
                i += 1

            # roles matrix
            dict_row['test_f']= False #funkcja
            dict_row['test_z']= False #zadanie
            dict_row['test_z_d']= False #zadanie_dysponent
            dict_row['test_z_c']= False #zadanie_cel
            dict_row['test_z_m']= False #zadanie_miernik
            dict_row['test_p']= False #podzadanie
            dict_row['test_p_d']= False #podzadanie_dysponent

            # checking the data collected in the dict_row and putting to the proper "socket" in the roles matrix
            if dict_row['numer'].count('.') == 0: # "grand grand total" or "funkcja" (the same structure of dict)
                dict_row['test_f']= True
            elif dict_row['numer'].count('.') == 1: # "zadanie + dysponent + cel + miernik" / "dysponent + cel + miernik" / "cel + miernik" / "miernik"
                if dict_row['funkcja_zadanie'] and dict_row['dysponent'] and dict_row['cel']: # "zadanie + dysponent + cel + miernik"
                    dict_row['test_z']= True #zadanie
                    dict_row['test_z_d']= True #zadanie_dysponent
                    dict_row['test_z_c']= True #zadanie_cel
                    dict_row['test_z_m']= True #zadanie_miernik
                else:
                    if dict_row['dysponent'] and dict_row['cel']: #"dysponent + cel + miernik"
                        dict_row['test_z_d']= True #zadanie_dysponent
                        dict_row['test_z_c']= True #zadanie_cel
                        dict_row['test_z_m']= True #zadanie_miernik
                    else:
                        if dict_row['cel']: #"cel + miernik"
                            dict_row['test_z_c']= True #zadanie_cel
                            dict_row['test_z_m']= True #zadanie_miernik
                        else:
                            dict_row['test_z_m']= True #zadanie_miernik
            elif dict_row['numer'].count('.') == 2: # "podzadanie + dysponent + cel + miernik" / "dysponent + cel + miernik"
                if dict_row['podzadanie']: # "podzadanie + dysponent + cel + miernik"
                    dict_row['test_p']= True #podzadanie
                    dict_row['test_p_d']= True #podzadanie_dysponent
                else:
                    dict_row['test_p_d']= True #"dysponent + cel + miernik"

            out.append(dict_row)

    return out


    

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser() 
    cmdparser.add_option("-v", "--csv", action="store", dest="csv_filename", help="input file (CSV)")
    cmdparser.add_option("-s", "--schema", action="store",help="schema for CSV file (if none than SRC_FILE-SCHEMA.JSON is used)")
    cmdparser.add_option("-d", "--dbconnect", action="store", help="mongodb database and collection in a format db.collect (no update if not specified)")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")
    cmdparser.add_option("-j", "--json", action="store", dest="json_filename", help="store to json file (CSV)")
    cmdparser.add_option("-i", "--indent", action="store", dest="jsindent", help="indent in JSON file")

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
        exit()

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

    #database settings
    str_dbconnect= opts.dbconnect # database connection string
    dbparam= []
    if str_dbconnect is not None: #parse it
        if '.' in str_dbconnect:
            dbparam= str_dbconnect.split('.', 2)
        else:
            print 'Unable to parse dbconnect - wrong format: \n %s\n' % str_dbconnect
            exit()
    else:
        dbparam= 'test', filename_csv.rstrip('.csv') #use defaults

    dbname= dbparam[0]
    collectname= dbparam[1]
    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()


    # create temporary dict
    obj_parsed= csv_parse(csv_read, schema)

    #create and fulfill temporary collection
    mongo_connect= pymongo.Connection("localhost", 27017)
    work_db= mongo_connect[dbname]
    coll_tmp= 'rap2011temp'
    # insert the object parsed from csv to the temporary collection, get the num of records
    mongo_connect.start_request()
    recs= db_insert(obj_parsed, work_db, coll_tmp, clean_db)
    print 'temporary collection created - '+ dbname +'.'+ coll_tmp + ': ' + str(recs) + ' records'
    mongo_connect.end_request()
    # create final dict
    mongo_connect.start_request()
    obj_rep= fill_rep(work_db, coll_tmp, collectname, clean_db)
    #recs_ins= db_insert(obj_rep, work_db, collectname, clean_db)
    mongo_connect.end_request()
    print 'temporary collection processed - dropping '+ dbname +'.'+ coll_tmp # add statistics of undeleted records, DON'T REMOVE the collection if there are some

    # DELETE AFTER FINISH - saving into file, just to check
    if opts.json_filename is not None:
        try:
            json_write= open(opts.json_filename, 'w')
        except IOError as e:
            print 'Unable to open file:\n %s\n' % e
            print '\n %s\n Non fatal error - continuing processing'

        try:
            print >>json_write, json.dumps(obj_rep, indent=4)
        except IOError as writerr:
            print 'Unable to save out_file:\n %s\n' % writerr
        finally:
            src_file.close()
            json_write.close()
            print "File saved: " + opts.json_filename
