#!/usr/bin/python

import getpass
import os
import optparse
import csv
import psycopg2
import psycopg2.extras
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
def execute_sql(statement, connection):
    cur = connection.cursor()
    success= True
    try:
        cur.execute(statement)
    except Exception, e:
        success= False
        print 'Cannot execute statement!: %r\n %s\n' % (statement, e)
    return success


#-----------------------------
def create_table(connection, schema, mode):
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # not to do COMMIT after every insert/update
    cur = connection.cursor()
    print '... creating', mode, "table - reading schema"
    table_name= schema[mode]['name'] # dict of aliases -> document keys in db
    colmn_name= schema[mode]['columns'] # dict of aliases -> document keys in db

    create_table_stat= 'CREATE TABLE '+ table_name +' ('
    order_list= [int(k) for k in colmn_name.keys()]
    order_list.sort()
    for curr_key in order_list:
        create_table_stat= create_table_stat + colmn_name[str(curr_key)]['name'] + ' ' + colmn_name[str(curr_key)]['type'] + ', '
    create_table_stat= create_table_stat.rstrip(', ')+')'

    try:
        cur.execute('DROP TABLE '+table_name)
    except:
        pass # no table with that name - nothing to delete

    success= True
    try:
        cur.execute(create_table_stat)
        print "... table", table_name, "successfully created"
    except Exception, e:
        success= False
        print 'Cannot create table!:\n %s\n' % e

    return success, table_name

#-----------------------------
def db_insert(data_bulk, db, collname, clean_first=False):
    collect= db[collname]

    if clean_first:
        collect.remove()

    collect.insert(data_bulk)
    return collect.find().count()

#-----------------------------
def sort_format(src):
    """
    format 1-2-3... to 001-002-003...
    src should be convertable to int
    """
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        res_list.append('%03d' % int(elm))
    res= '-'.join(res_list)
    return res


#-----------------------------
def fill_work_table(temp_tbl, work_tbl, connection):
    select_statement= "SELECT * FROM %s ORDER BY %s" % (temp_tbl, '_id')
    dict_cur= connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_statement)
    rows = dict_cur.fetchall()
    for row in rows:

        # FUNKCJA: level 'a', node NULL
        if row['test_f']:
            idef= row['numer']
            idef_sort= '%03d' % int(row['numer'])
            funk_type_name= row['funkcja_zadanie'].split('.', 2)
            curr_funkcja= row['numer']
            leaf= False # 'funkcja' has children
            v_total= row['ogolem']
            v_nation= row['budzet_panstwa']
            v_eu= row['budzet_srodkow_europejskich']
            if v_total != 0:
                v_proc_eu= round(float(v_eu) / float(v_total) * 100, 2) #percentage
                v_proc_nation= round(float(v_nation) / float(v_total) * 100, 2)
            if row['numer'] == '999999':
                idef_sort= row['numer']
                elem_type= 'Total'
                elem_name= row['funkcja_zadanie'].strip().decode('utf-8')
                leaf= True # in case of grand total it's the last level (no children)
            else:
                elem_name= funk_type_name[1].strip().decode('utf-8')
                elem_type= funk_type_name[0].strip().decode('utf-8')
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', NULL, NULL, NULL, '%s', 'a', '%s', '%s', NULL, NULL, NULL, %d, %d, %d, %0.2f, %0.2f, %d)
                """ % (work_tbl, idef, idef_sort, leaf, elem_type, elem_name, v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, 2011)
            execute_sql(insert_statement, connection)

        # FUNKCJA - ZADANIE: level 'b', node NULL
        if row['test_z']:
            curr_zadanie= row['numer'].replace('.','-')
            idef= curr_zadanie
            idef_sort= sort_format(idef)
            parent= curr_funkcja
            parent_sort= int(curr_funkcja)
            list_name= row['funkcja_zadanie'].split('.', 2)
            elem_type= ('Zadanie ' + list_name[0].strip() + '.' + list_name[1].strip()).decode('utf-8')
            elem_name= list_name[2].strip().decode('utf-8')
            leaf= False # 'zadanie' has children
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%03d', NULL, '%s', 'b', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, 2011)
            execute_sql(insert_statement, connection) # money are NULL on that level
            zadanie_dysp_count= 0 # for incrementing children - 'dysponent'

        # ZADANIE - DYSPONENT: level 'c', node 0
        if row['test_z_d']:
            zadanie_dysp_count += 1
            parent= curr_zadanie
            parent_sort= sort_format(parent)
            idef= curr_zadanie+'-'+str(zadanie_dysp_count)
            curr_zadanie_dysponent= idef
            idef_sort= sort_format(idef)
            elem_type= 'Dysponent'
            elem_name= row['dysponent'].strip().decode('utf-8')
            leaf= False # 'dysponent' has children
            v_total= row['ogolem']
            v_nation= row['budzet_panstwa']
            v_eu= row['budzet_srodkow_europejskich']
            if v_total != 0:
                v_proc_eu= round(float(v_eu) / float(v_total) * 100, 2) #percentage
                v_proc_nation= round(float(v_nation) / float(v_total) * 100, 2)
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 0, '%s', 'c', '%s', '%s', '%s', NULL, NULL, %d, %d, %d, %0.2f, %0.2f, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, 2011)
            execute_sql(insert_statement, connection)
            zadanie_dysp_cel_count= 0 # for incrementing children - 'cel'

        # ZADANIE - DYSPONENT - CEL: level 'd', node 0
        if row['test_z_c']:
            zadanie_dysp_cel_count += 1
            parent= curr_zadanie_dysponent
            parent_sort= sort_format(parent)
            idef= curr_zadanie_dysponent+'-'+str(zadanie_dysp_cel_count)
            curr_zadanie_dysponent_cel= idef
            idef_sort= sort_format(idef)
            elem_type= 'Cel'
            elem_name= row['cel'].strip().decode('utf-8')
            leaf= False # 'cel' has children
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 0, '%s', 'd', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], 2011)
            execute_sql(insert_statement, connection) # money are NULL on that level
            zadanie_dysp_cel_mier_count= 0 # for incrementing children - 'cel'

        # ZADANIE - DYSPONENT - CEL - MIERNIK: level 'e', node 0, leaf= True
        if row['test_z_m']:
            zadanie_dysp_cel_mier_count += 1
            parent= curr_zadanie_dysponent_cel
            parent_sort= sort_format(parent)
            idef= curr_zadanie_dysponent_cel+'-'+str(zadanie_dysp_cel_mier_count)
            idef_sort= sort_format(idef)
            elem_type= 'Miernik'
            elem_name= row['miernik_nazwa'].strip().decode('utf-8')
            wartosc_bazowa= row['miernik_wartosc_bazowa']
            wartosc_rok_obec= row['miernik_wartosc_rok_obec']
            if wartosc_bazowa is not None:
                wartosc_bazowa= wartosc_bazowa.strip().decode('utf-8')
            if wartosc_rok_obec is not None:
                wartosc_rok_obec= wartosc_rok_obec.strip().decode('utf-8')
            leaf= True # 'miernik' is the deepest level
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 0, '%s', 'e', '%s', '%s', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], wartosc_bazowa, wartosc_rok_obec, 2011)
            execute_sql(insert_statement, connection) # money are NULL on that level

        # ZADANIE - PODZADANIE: level 'c', node 1
        if row['test_p']:
            parent= curr_zadanie
            parent_sort= sort_format(parent)
            idef= row['numer'].replace('.','-')
            idef_sort= sort_format(idef)
            curr_podzadanie= idef
            list_name= row['podzadanie'].split('.', 3)
            elem_type= ('Podzadanie ' + list_name[0].strip() + '.' + list_name[1].strip() + '.' + list_name[2].strip()).decode('utf-8')
            elem_name= list_name[3].strip().decode('utf-8')
            leaf= False # 'podzadanie' has children
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'c', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, 2011)
            execute_sql(insert_statement, connection) # money are NULL on that level
            podzadanie_dysp_count= 0 # for incrementing children - 'dysponent'

        # ZADANIE - PODZADANIE - DYSPONENT: level 'd', node 1
        if row['test_p_d']:
            podzadanie_dysp_count += 1
            parent= curr_podzadanie
            parent_sort= sort_format(parent)
            idef= curr_podzadanie+'-'+str(podzadanie_dysp_count)
            curr_podzadanie_dysp= idef
            idef_sort= sort_format(idef)
            elem_type= 'Dysponent'
            elem_name= row['dysponent'].strip().decode('utf-8')
            leaf= False # 'dysponent' has children - TO CONFIRM BY IGNACY!!! (*)
            v_total= row['ogolem']
            v_nation= row['budzet_panstwa']
            v_eu= row['budzet_srodkow_europejskich']
            if v_total != 0:
                v_proc_eu= round(float(v_eu) / float(v_total) * 100, 2) #percentage
                v_proc_nation= round(float(v_nation) / float(v_total) * 100, 2)
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'd', '%s', '%s', '%s', NULL, NULL, %d, %d, %d, %0.2f, %0.2f, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, 2011)
            execute_sql(insert_statement, connection)
            zadanie_dysp_cel_count= 0 # for incrementing children - 'cel'

        # (*) next 2 blocks - until Ignacy confirms that we fulfill next 2 levels with 1 successive element in each case

        # ZADANIE - PODZADANIE - DYSPONENT - CEL: level 'e', node 1
            parent= curr_podzadanie_dysp
            parent_sort= sort_format(parent)
            idef= curr_podzadanie_dysp+'-1' # to change depends on (*)
            curr_podzadanie_dysp_cel= idef
            idef_sort= sort_format(idef)
            elem_type= 'Cel'
            elem_name= row['cel'].strip().decode('utf-8')
            leaf= False # 'cel' has children - TO BE CONFIRMED (*)
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'e', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], 2011)
            execute_sql(insert_statement, connection)
            zadanie_dysp_cel_mier_count= 0 # for incrementing children - 'cel'

        # ZADANIE - PODZADANIE - DYSPONENT - CEL - MIERNIK: level 'f', node 1
            parent= curr_podzadanie_dysp_cel
            parent_sort= sort_format(parent)
            idef= curr_podzadanie_dysp_cel+'-1' # to change depends on (*)
            idef_sort= sort_format(idef)
            elem_type= 'Miernik'
            elem_name= row['miernik_nazwa'].strip().decode('utf-8')
            wartosc_bazowa= row['miernik_wartosc_bazowa']
            wartosc_rok_obec= row['miernik_wartosc_rok_obec']
            if wartosc_bazowa is not None:
                wartosc_bazowa= wartosc_bazowa.strip().decode('utf-8')
            if wartosc_rok_obec is not None:
                wartosc_rok_obec= wartosc_rok_obec.strip().decode('utf-8')
            leaf= True # 'miernik' is the deepest level
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'f', '%s', '%s', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], wartosc_bazowa, wartosc_rok_obec, 2011)
            execute_sql(insert_statement, connection)




#-----------------------------
def csv_parse(csv_read, table, schema, conn):
    colmn_name= schema['temp']['columns']

    for row in csv_read:
        keys= tuple(row)
        keys_len= len(keys)
        row= iter(row)        
        for row in csv_read:
            insert_statement= "INSERT INTO "+ table + " VALUES("
            i= 0
            for field in row:
                if field == '':
                    curr_field= "NULL"
                else:
                    if 'integer' in colmn_name[str(i)]['type']:
                        curr_field= field
                    else:
                        curr_field= "'" + field.decode('utf-8') + "'"

                insert_statement= insert_statement + curr_field + ', '

                i += 1

            # checking the data collected in the dict_row and putting to the proper "socket" in the roles matrix
            if row[0].count('.') == 0: # row[0] is 'numer': ('grand grand total' or 'funkcja')
                #True: test_f
                insert_statement= insert_statement + "'true', 'false', 'false', 'false', 'false', 'false', 'false', "
            elif row[0].count('.') == 1: # "zadanie + dysponent + cel + miernik" OR "dysponent + cel + miernik" OR "cel + miernik" OR "miernik"
                if row[1] and row[3] and row[5]: # row[1] zadanie + row[3] dysponent + row[5] cel + miernik
                    #True: test_z (zadanie), test_z_d (zadanie_dysponent), test_z_c (zadanie_cel), test_z_m (zadanie_miernik)
                    insert_statement= insert_statement + "'false', 'true', 'true', 'true', 'true', 'false', 'false', "
                else:
                    if row[3] and row[5]: # row[3] dysponent + row[5] cel + miernik
                        #True: test_z_d (zadanie_dysponent), test_z_c (zadanie_cel), test_z_m (zadanie_miernik)
                        insert_statement= insert_statement + "'false', 'false', 'true', 'true',  'true',  'false', 'false', "
                    else:
                        if row[5]: #row[5] cel + miernik
                            #True: test_z_c (zadanie_cel), test_z_m (zadanie_miernik)
                            insert_statement= insert_statement + "'false', 'false', 'false', 'true', 'true', 'false', 'false', "
                        else: # zadanie_miernik
                            #True: test_z_m
                            insert_statement= insert_statement + "'false', 'false', 'false', 'false', 'true', 'false', 'false', "
            elif row[0].count('.') == 2: # row[0] is 'numer': "podzadanie + dysponent + cel + miernik" / "dysponent + cel + miernik"
                if row[2]: # row[2] is podzadanie: "podzadanie + dysponent + cel + miernik"
                    #True: test_p (podzadanie), test_p_d (podzadanie_dysponent)
                    insert_statement= insert_statement + "'false', 'false', 'false', 'false', 'false', 'true', 'true', "
                else: # dysponent + cel + miernik
                    #True: test_p_d (podzadanie_dysponent)
                    insert_statement= insert_statement + "'false', 'false', 'false', 'false', 'false', 'false', 'true', "

            insert_statement= insert_statement + "DEFAULT)"

            execute_sql(insert_statement, conn)
    

#-----------------------------
if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] src_filename.csv src_schema.json") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file (CSV)")
    cmdparser.add_option("-c", action="store_true",dest='dbact',help="clean db before insert (ignored if db is not updated)")

    opts, args = cmdparser.parse_args()

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
        filename_schema= args[0].rstrip('.csv')+'-sql.json'
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

    # get connection details
    conn= get_db_connect(conf_filename, 'postgresql')
    conn_host= conn['host']
    conn_port= conn['port']
    conn_db= conn['database']
    conn_username= conn['username']
    conn_password= conn['password']

    #username - ask for password
    if conn_password is None:
        conn_password = getpass.getpass('Password for '+conn_username+': ')

    try:
        connect_postgres = psycopg2.connect(host= conn_host, port= conn_port, database=conn_db, user= conn_username, password= conn_password)
        print "... connected to db", conn_db
    except Exception, e:
        print 'Unable to connect to the PostgreSQL database:\n %s\n' % e
        exit() #no connection to the database - no data processing

    clean_db= opts.dbact # False - insert() data, True - remove() and then insert()

    mode= 'temp'
    temp_table_created, temp_table= create_table(connect_postgres, schema, mode) # create temporary table
    if not temp_table_created:
        print 'FATAL ERROR: something went wrong while creating %s table: %s' % (mode, temp_table)

    csv_parse(csv_read, temp_table, schema, connect_postgres) # fill temporary table

    mode= 'work'
    table_created, work_table= create_table(connect_postgres, schema, mode) # create work table
    if not table_created:
        print 'FATAL ERROR: something went wrong while creating %s table: %s' % (mode, work_table)

    fill_work_table(temp_table, work_table, connect_postgres) # fill work table
    print '... work table is filled'

    print '... dropping temporary table'
    #delete temp table
    drop_statement= "DROP TABLE %s" % (temp_table)
    execute_sql(drop_statement, connect_postgres)
    
    print 'Done'



# # old code
# # FILL THE DATA

# # copy dysponent from node 0 to 1:
# # if there is no 'podzadanie' in some function in node 1,
# # list of 'dysponents' should be copied as (!!!)child elements of zadanie(!!!)
# def copy_dysp(db, collname, func_num):
#     out= []
#     collect= db[collname]
#     collcrr_p_d= collect.find({'node':0 ,'level':'c','idef':{'$regex':func_num+'.'}},{'_id':0}) # collecting all 'dysponents' of specified function
#     for row in collcrr_p_d:
#         new_row= row.copy()
#         new_row['leaf']= True # changing just a bit
#         new_row['node']= 1
#         out.append(new_row)

#     return out


# # node 1
# def fill_p_dysp(db, collname, colltmp, objlst):
#     out= objlst[:] # copy of list containing 'podzadanie'

#     clltmp= db[colltmp]
#     cllact= db[collname]

#     for podz in objlst: # iterating through podzadanie
#         podz_curr= podz['idef'].replace('-','.') # have to look through old codes with '.' separator
#         collcrr_p_d= clltmp.find({'test_p_d':True, 'numer':podz_curr}, {'_id':0}) # collecting all 'dysponents' of all 'podzadanie'
#         tmp, podz_v_eu, podz_v_nation, podz_v_total = 0, 0, 0, 0
#         for row in collcrr_p_d:
#             fpd= {}
#             tmp += 1
#             name_p_d= row['dysponent'].strip()
#             czesc_p_d= row['czesc']
#             curr_zd_idef_lst= row['numer'].split('.')
#             curr_zd_idef= curr_zd_idef_lst[0] + '-' + curr_zd_idef_lst[1] # have to search in the scope of current 'zadanie'
#             #we already have 'idef' for all dysponents of zadanie - just look for it in the previously inserted data
#             p_d_idef= cllact.find_one({'node':0, 'level':'c', 'czesc':czesc_p_d, 'parent':curr_zd_idef, 'name':name_p_d}, {'idef':1, '_id':0})
#             fpd['idef']= p_d_idef['idef']
#             fpd['type']= 'Dysponent'
#             fpd['name']= name_p_d
#             fpd['parent']= row['numer'].replace('.', '-') # idef of "podzadanie"
#             fpd['node']= 1 # "dysponent" has a direction
#             fpd['level']= 'd'
#             fpd['leaf']= True # this level is the deepest one in node 1
#             fpd['czesc']= czesc_p_d
#             fpd['cel']= row['cel']
#             fpd['miernik_nazwa']= row['miernik_nazwa']
#             fpd['miernik_wartosc_bazowa']= row['miernik_wartosc_bazowa']
#             fpd['miernik_wartosc_rb']= row['miernik_wartosc_rok_obec']
#             fpd['v_total']= row['ogolem'] # this is the last object
#             fpd['v_nation']= row['budzet_panstwa']
#             fpd['v_eu']= row['budzet_srodkow_europejskich']
#             if fpd['v_total'] != 0:
#                 fpd['v_proc_eu']= round(float(fpd['v_eu']) / float(fpd['v_total']) * 100, 2) # percentage
#                 fpd['v_proc_nation']= round(float(fpd['v_nation']) / float(fpd['v_total']) * 100, 2)
#             podz_v_eu += fpd['v_eu'] # calculating totals for current podzadanie
#             podz_v_nation += fpd['v_nation']
#             podz_v_total += fpd['v_total']
        
#             out.append(fpd)

#         podz_curr= podz_curr.replace('.','-') # changing back - now we look through updated codes
#         for elem in out: # update totals of current podzadanie
#             if elem['idef'] == podz_curr:
#                 elem['v_total'], elem['v_nation'], elem['v_eu'] = podz_v_total, podz_v_nation, podz_v_eu
#                 if elem['v_total'] != 0:
#                     elem['v_proc_eu']= round(float(elem['v_eu']) / float(elem['v_total']) * 100, 2) # percentage
#                     elem['v_proc_nation']= round(float(elem['v_nation']) / float(elem['v_total']) * 100, 2)
#                 break

#     return out



# def fill_podzadanie(db, clltmp):
#     out= []

#     collect= db[clltmp]
#     collcrr_p= collect.find({'test_p':True}, {'_id':0}) # getting list of "podzadanie"
#     for row_p in collcrr_p:
#         fpz= {}
#         fpz['idef']= row_p['numer'].replace('.', '-')
#         fpz['type']= 'Podzadanie '+row_p['numer']
#         fpz_zd_idef= row_p['numer'].split('.', 3)
#         fpz['parent']= fpz_zd_idef[0]+'-'+fpz_zd_idef[1] # idef of "zadanie"
#         name_tmp= row_p['podzadanie'].lstrip(row_p['numer'])
#         fpz['name']= name_tmp.strip()
#         fpz['node']= 1 # "podzadanie" has a direction
#         fpz['level']= 'c'
#         fpz['leaf']= False
#         fpz['v_total']= None # no data on this level
#         fpz['v_nation']= None
#         fpz['v_eu']= None
#         fpz['v_proc_eu']= None
#         fpz['v_proc_nation']= None

#         out.append(fpz)

#     return out


# # node 0
# def fill_z_d_c_mier(db, cllname, clltmp):
#     out= []
#     check_id= []

#     collmain= db[cllname]
#     collmn= db[cllname]
#     colltmp= db[clltmp]
#     collcrr_dysp= collmain.find({'level':'d', 'node':0}, {'idef':1, 'parent':1, 'czesc':1, 'name':1, '_id':0}) # first getting the list of "cel" and their parents
#     for row in collcrr_dysp:
#         ds_curr= row['parent'] # current "dysponent" of "zadanie"
#         collcrr_tmp= collmn.find_one({'idef':ds_curr}, {'name':1, '_id':0})
#         ds_name= collcrr_tmp['name'] # "dysponent" name
#         zd_curr_str= ds_curr.split('-', 3)
#         zd_curr= zd_curr_str[0]+'.'+zd_curr_str[1] # current "zadanie" ('.' is just to look through temp table, where all the codes separated by '.')
#         cl_curr= row['idef'] # current "cel"
#         cl_name= row['name'] # current "cel" name
#         ds_czesc_curr= row['czesc'] # current "czesc"

#         cl_m_num= 0 # 'miernik' numerator

#         # this is the last level, so, every other time we add the doc to [out], we delete it from collection
#         # so that it will not be doubled

#         # first processing records where we have everything: "dysponent", "cel", and "miernik"
#         collcrr_m1= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'dysponent':ds_name, 'cel': cl_name, 'test_z_d':True, 'test_z_c':True, 'test_z_m':True})
#         if collcrr_m1.count() != 0:
#             for row_z_m in collcrr_m1:
#                 if row_z_m['_id'] not in check_id:
#                     ffm= {}
#                     cl_m_num += 1
#                     ffm['name']= row_z_m['miernik_nazwa']
#                     full_cl_m_num= cl_curr + '-' + str(cl_m_num)
#                     ffm['idef']= full_cl_m_num
#                     ffm['type']= 'Miernik'
#                     ffm['parent']= cl_curr # idef of "cel"
#                     ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
#                     ffm['level']= 'e'
#                     ffm['leaf']= True # now - this level is the deepest in node 0
#                     ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#                     ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
#                     ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
#                     ffm['v_total']= None # no values on the level of "miernik"
#                     ffm['v_nation']= None
#                     ffm['v_eu']= None
#                     ffm['v_proc_eu']= None
#                     ffm['v_proc_nation']= None

#                     out.append(ffm)
#                     check_id.append(row_z_m['_id'])

#         # second - "cel", and "miernik"
#         collcrr_m2= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'cel': cl_name, 'test_z_d':False, 'test_z_c':True, 'test_z_m':True})
#         if collcrr_m2.count() != 0:
#             for row_z_m in collcrr_m2:
#                 if row_z_m['_id'] not in check_id:
#                     ffm= {}
#                     cl_m_num += 1
#                     ffm['name']= row_z_m['miernik_nazwa']
#                     full_cl_m_num= cl_curr + '-' + str(cl_m_num)
#                     ffm['idef']= full_cl_m_num
#                     ffm['type']= 'Miernik'
#                     ffm['parent']= cl_curr # idef of "cel"
#                     ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
#                     ffm['level']= 'e'
#                     ffm['leaf']= True # now - this level is the deepest in node 0
#                     ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#                     ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
#                     ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
#                     ffm['v_total']= None # no values on the level of "miernik"
#                     ffm['v_nation']= None
#                     ffm['v_eu']= None
#                     ffm['v_proc_eu']= None
#                     ffm['v_proc_nation']= None

#                     out.append(ffm)
#                     check_id.append(row_z_m['_id'])

#         # third - "miernik" only
#         collcrr_m3= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'cel':None, 'test_z_d':False, 'test_z_c':False, 'test_z_m':True})
#         if collcrr_m3.count() != 0:
#             for row_z_m in collcrr_m3:
#                 if row_z_m['_id'] not in check_id:
#                     ffm= {}
#                     cl_m_num += 1
#                     ffm['name']= row_z_m['miernik_nazwa']
#                     full_cl_m_num= cl_curr + '-' + str(cl_m_num)
#                     ffm['idef']= full_cl_m_num
#                     ffm['type']= 'Miernik'
#                     ffm['parent']= cl_curr # idef of "cel"
#                     ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
#                     ffm['level']= 'e'
#                     ffm['leaf']= True # now - this level is the deepest in node 0
#                     ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#                     ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
#                     ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
#                     ffm['v_total']= None # no values on the level of "miernik"
#                     ffm['v_nation']= None
#                     ffm['v_eu']= None
#                     ffm['v_proc_eu']= None
#                     ffm['v_proc_nation']= None

#                     out.append(ffm)
#                     check_id.append(row_z_m['_id'])
#     return out


# def fill_z_d_cel(db, cllname, clltmp):
#     out= []

#     collmain= db[cllname]
#     colltmp= db[clltmp]
#     collcrr_dysp= collmain.find({"level":"c", "node":0}, {"idef":1, "parent":1, "czesc":1, "name":1, "_id":0}) # first getting the list of "dysponent" and their parents
#     for row in collcrr_dysp:
#         zd_curr= row['parent'].replace('-','.') # current "zadanie" (replace '-' to '.' for search in temp table)
#         ds_curr= row['idef'] # current "dysponent"
#         ds_name= row['name'] # current "dysponent" name
#         ds_czesc_curr= row['czesc'] # current "czesc"
        
#         cl_d_num= 0
#         # first processing records of both "cel" & "dysponent"
#         collcrr_z_c= colltmp.find({'numer':zd_curr, 'dysponent':ds_name, "test_z_d":True, "test_z_c":True}, {"_id":0})
#         for row_z_c in collcrr_z_c:
#             ffc= {}
#             ffc['name']= row_z_c['cel']
#             cl_d_num += 1
#             full_cl_d_num= ds_curr + '-' + str(cl_d_num)
#             ffc['idef']= full_cl_d_num
#             ffc['type']= 'Cel'
#             ffc['parent']= ds_curr # idef of "dysponent"
#             ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#             ffc['node']= 0 # "cel" follows the direction of "dysponent"
#             ffc['level']= 'd'
#             ffc['leaf']= False # it isn't the deepest level
#             ffc['v_total']= None # no values on the level of "cel"
#             ffc['v_nation']= None
#             ffc['v_eu']= None
#             ffc['v_proc_eu']= None
#             ffc['v_proc_nation']= None


#             out.append(ffc)

#         # now "cel" without "dysponent", looking for it via "czesc"
#         collcrr_z_c= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, "test_z_d":False, "test_z_c":True}, {"_id":0})
#         for row_z_c in collcrr_z_c:
#             ffc= {}
#             ffc['name']= row_z_c['cel']
#             cl_d_num += 1
#             full_cl_d_num= ds_curr + '-' + str(cl_d_num)
#             ffc['idef']= full_cl_d_num
#             ffc['type']= 'Cel'
#             ffc['parent']= ds_curr # idef of "dysponent"
#             ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#             ffc['node']= 0 # "cel" follows the direction of "dysponent"
#             ffc['level']= 'd'
#             ffc['leaf']= False # it isn't the deepest level
#             ffc['v_total']= None # no values on the level of "cel"
#             ffc['v_nation']= None
#             ffc['v_eu']= None
#             ffc['v_proc_eu']= None
#             ffc['v_proc_nation']= None

#             out.append(ffc)

#     return out

# def fill_z_dysponent(db, colltmp, objlst):
#     out= objlst[:]

#     collect= db[colltmp]
#     collcrr_zdnum= collect.find({"test_z":True}, {"numer":1, "_id":0}) # collecting the numbers of "zadanie"
#     for row in collcrr_zdnum:
#         zd_curr= row['numer'] # current "zadanie"
#         zd_d_num, zd_v_eu, zd_v_nation, zd_v_total = 0, 0, 0, 0
#         collcrr_z_d= collect.find({'numer':zd_curr, "test_z_d":True}, {"_id":0}) # getting "dysponent" of current "zadanie"
#         for row_z_d in collcrr_z_d:
#             fzd= {}
#             zd_d_num += 1
#             full_zd_d_num= row_z_d['numer'].replace('.','-') + '-dt' + str(zd_d_num) # 'dysponent' code becomes N-M-dtK
#             fzd['idef']= full_zd_d_num
#             fzd['type']= 'Dysponent'
#             fzd['name']= row_z_d['dysponent']
#             fzd['parent']= row_z_d['numer'].replace('.', '-') # idef of "zadanie"
#             fzd['czesc']= row_z_d['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
#             fzd['node']= 0 # "dysponent" has a direction
#             fzd['level']= 'c'
#             fzd['leaf']= False # it isn't the deepest level
#             fzd['v_total']= row_z_d['ogolem'] # this is the last object
#             fzd['v_nation']= row_z_d['budzet_panstwa']
#             fzd['v_eu']= row_z_d['budzet_srodkow_europejskich']
#             if fzd['v_total'] != 0:
#                 fzd['v_proc_eu']= round(float(fzd['v_eu']) / float(fzd['v_total']) * 100, 2) # percentage
#                 fzd['v_proc_nation']= round(float(fzd['v_nation']) / float(fzd['v_total']) * 100, 2)
#             zd_v_eu += fzd['v_eu']
#             zd_v_nation += fzd['v_nation']
#             zd_v_total += fzd['v_total']

#             out.append(fzd)

#         zd_curr= zd_curr.replace('.','-') # now we look through updated codes
#         for elem in out: # update totals of current zadanie
#             if elem['idef'] == zd_curr:
#                 elem['v_total'], elem['v_nation'], elem['v_eu'] = zd_v_total, zd_v_nation, zd_v_eu # values
#                 if elem['v_total'] != 0:
#                     elem['v_proc_eu']= round(float(elem['v_eu']) / float(elem['v_total']) * 100, 2) # percentages
#                     elem['v_proc_nation']= round(float(elem['v_nation']) / float(elem['v_total']) * 100, 2)
#                 break
    
#     return out


# def fill_zadanie(db, colltmp, objlst):
#     out= objlst[:]
#     collect= db[colltmp]
#     colltmpcrr= collect.find({"test_z":True}, {"_id":0}) # looking only for "zadanie"

#     for row in colltmpcrr:
#         tmpdict= dict(row)
#         ffz= {}
#         ffz['idef']= tmpdict['numer'].replace('.','-')
#         zd_type_name= tmpdict['funkcja_zadanie'].rsplit('.', 2) # extract "funkcja_zadanie"
#         ffz['type']= 'Zadanie ' + zd_type_name[0].strip() + '.' + zd_type_name[1].strip()
#         ffz['name']= zd_type_name[2].strip()
#         ffz['parent']= zd_type_name[0].strip() # idef of "zadanie"
#         ffz['node']= None # "zadanie" is not a root, but it still doesn't have a 'direction'
#         ffz['level']= 'b' # 2nd level in the hierarchy
#         ffz['leaf']= False # it isn't the deepest level
#         ffz['v_total']= None # no info about money on that level
#         ffz['v_nation']= None
#         ffz['v_eu']= None
#         ffz['v_proc_eu']= None
#         ffz['v_proc_nation']= None

#         out.append(ffz)

#     return out


# def fill_funkcja(db, colltmp):
#     out= []
#     collect= db[colltmp]
#     colltmpcrr= collect.find({"test_f":True}, {"_id":0}) # looking only for "funkcja"
#     for row in colltmpcrr:
#         frr= row.copy()
#         frr= dict(frr)
#         for k, v in row.iteritems():
#             if v is None or k.startswith('test_'): # delete records with empty values and keys of test matrix
#                 frr.pop(k)
#         frr['idef']= frr.pop('numer').replace('.', '-') # change "numer" to "identifier" replaceing dots with dashes
#         funk_type_name= frr.pop('funkcja_zadanie').split('.', 2) # extract "funkcja_zadanie"
#         if frr['idef'] == '999999':
#             frr['type']= 'total'
#             frr['name']= funk_type_name[0].strip()
#             frr['leaf']= True # in case of grand total it's the last level (no children)
#         else:
#             frr['type']= funk_type_name[0].strip()
#             frr['name']= funk_type_name[1].strip()
#             frr['leaf']= False # not the deepest level
#         frr['parent']= None # "funkcja" is the root
#         frr['node']= None # "funkcja" doesn't have a 'direction'
#         frr['level']= 'a' # the highest level in the hierarchy
#         frr['leaf']= False # not the deepest level
#         frr['v_total']= frr.pop('ogolem') # change "ogolem" to "total" of the current year
#         frr['v_nation']= frr.pop('budzet_panstwa') # the same for state budget
#         frr['v_eu']= frr.pop('budzet_srodkow_europejskich') #the same for EU part in the budget
#         if frr['v_total'] != 0:
#             frr['v_proc_eu']= round(float(frr['v_eu']) / float(frr['v_total']) * 100, 2) #percentage
#             frr['v_proc_nation']= round(float(frr['v_nation']) / float(frr['v_total']) * 100, 2)
#         out.append(frr)

#     return out


# def fill_rep(db, colltmp, collname, cleandb):
#     out= []
#     # filling containers for all kinds of data successively
#     dict_funk= fill_funkcja(db, colltmp) # "funkcja"
#     print '-- funkcja:', len(dict_funk)
#     dict_zadanie= fill_zadanie(db, colltmp, dict_funk) # "zadanie"
#     print '-- funkcja-zadanie:', len(dict_zadanie)

#     # filling out node 1 (zadanie - dysponent - cel - miernik)
#     dict_zd_dysp= fill_z_dysponent(db, colltmp, dict_zadanie) # "dysponent"
#       #and this is precisely the moment to insert the first bulk of data into the db,
#       #'cause there are already docs with artificially created identifiers
#     print '-- node 0: funkcja-zadanie-dysponent:', len(dict_zd_dysp), '; total:', db_insert(dict_zd_dysp, db, collname, cleandb)
#     dict_zd_dysp_cel= fill_z_d_cel(db, collname, colltmp) # "cel"
#     print '-- node 0: funkcja-zadanie-dysponent-cel:', len(dict_zd_dysp_cel), '; total:', db_insert(dict_zd_dysp_cel, db, collname, False) # append, no db clean!
#     dict_zd_dysp_cel_mr= fill_z_d_c_mier(db, collname, colltmp) # "miernik"
#     print '-- node 0: funkcja-zadanie-dysponent-cel-miernik:', len(dict_zd_dysp_cel_mr), '; total:', db_insert(dict_zd_dysp_cel_mr, db, collname, False) # append, no db clean!

#     # filling out node 1 (zadanie - podzadanie - dysponent (with cel and miernik at the same level))
#     dict_podz= fill_podzadanie(db, colltmp) # "podzadanie"
#     print '-- node 1: podzadanie:', len(dict_podz) # no insert here, because it's necessary to calculate totals for podzadanie
#     dict_podz_dysp= fill_p_dysp(db, collname, colltmp, dict_podz) # "dysponent" (we need both updated "collname" and "colltmp" here)
#     print '-- node 1: podzadanie-dysponent:', len(dict_podz_dysp), '; total:', db_insert(dict_podz_dysp, db, collname, False)
#     # VERY SPECIFIC - FOR TASK 22 ONLY
#     dict_copy_dysp= copy_dysp(db, collname, '22') # "dysponent" (we need both updated "collname" and "colltmp" here)
#     print '-- node 0 to 1: copy dysponent:', len(dict_copy_dysp), '; total:', db_insert(dict_copy_dysp, db, collname, False)
#     # get the data from db and return for json file
#     out= db[collname].find({}, {'_id':0}) # collecting everything
#     return out
