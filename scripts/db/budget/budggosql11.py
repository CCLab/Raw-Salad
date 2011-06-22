#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        print 'Cannot execute statement: %r %s\n' % (statement, e)
    return success


#-----------------------------
def create_table(connection, schema, mode, clean_act):
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

    if clean_act:
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
        print 'Cannot create table:\n %s' % e

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
    format 1-2-3... to 0001-0002-0003...
    src should be convertable to int
    """
    src_list= src.split('-')
    res_list= []
    for elm in src_list:
        res_list.append('%04d' % int(elm))
    res= '-'.join(res_list)
    return res


#-----------------------------
def fill_work_table(curr_year, temp_tbl, work_tbl, connection):
    select_statement= "SELECT * FROM %s ORDER BY %s" % (temp_tbl, '_id')
    dict_cur= connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_statement)
    rows = dict_cur.fetchall()
    for row in rows:

        # FUNKCJA: level 'a', node NULL
        if row['test_f']:
            idef= row['numer']
            idef_sort= sort_format(idef)
            funk_type_name= row['funkcja_zadanie'].split('.', 2)
            curr_funkcja= row['numer']
            leaf= False # 'funkcja' has childrenidef
            v_total= row['ogolem']
            v_nation= row['budzet_panstwa']
            v_eu= row['budzet_srodkow_europejskich']
            if v_total != 0:
                v_proc_eu= round(float(v_eu) / float(v_total) * 100, 2) #percentage
                v_proc_nation= round(float(v_nation) / float(v_total) * 100, 2)
            if row['numer'] == '9999':
                idef_sort= row['numer']
                elem_type= 'Total'
                elem_name= row['funkcja_zadanie'].strip().decode('utf-8')
                leaf= True # in case of grand total it's the last level (no children)
            else:
                elem_name= funk_type_name[1].strip().decode('utf-8')
                elem_type= funk_type_name[0].strip().decode('utf-8')
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', NULL, NULL, NULL, '%s', 'a', '%s', '%s', NULL, NULL, NULL, %d, %d, %d, %0.2f, %0.2f, %d)
                """ % (work_tbl, idef, idef_sort, leaf, elem_type, elem_name, v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, curr_year)
            execute_sql(insert_statement, connection)

        # FUNKCJA - ZADANIE: level 'b', node NULL
        if row['test_z']:
            curr_zadanie= row['numer'].replace('.','-')
            idef= curr_zadanie
            idef_sort= sort_format(idef)
            parent= curr_funkcja
            parent_sort= sort_format(parent)
            list_name= row['funkcja_zadanie'].split('.', 2)
            elem_type= ('Zadanie ' + list_name[0].strip() + '.' + list_name[1].strip()).decode('utf-8')
            elem_name= list_name[2].strip().decode('utf-8')
            leaf= False # 'zadanie' has children
            insert_statement= """
                INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', NULL, '%s', 'b', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, curr_year)
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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, curr_year)
            execute_sql(insert_statement, connection)
            zadanie_dysp_cel_count= 0 # for incrementing children - 'cel'
            # WARNING!
            if curr_funkcja == '22': # doubling that for the node 1, as there's no 'Podzadanie' for Funk 22
                insert_statement= """
                    INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'c', '%s', '%s', '%s', NULL, NULL, %d, %d, %d, %0.2f, %0.2f, %d)
                    """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], 
                           v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, curr_year)
                execute_sql(insert_statement, connection)

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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], curr_year)
            execute_sql(insert_statement, connection) # money are NULL on that level
            zadanie_dysp_cel_mier_count= 0 # for incrementing children - 'cel'
            # WARNING!
            if curr_funkcja == '22': # doubling that for the node 1, as there's no 'Podzadanie' for Funk 22
                insert_statement= """
                    INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'd', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, NULL, NULL, %d)
                    """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], curr_year)
                execute_sql(insert_statement, connection)

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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], wartosc_bazowa, wartosc_rok_obec, curr_year)
            execute_sql(insert_statement, connection) # money are NULL on that level
            # WARNING!
            if curr_funkcja == '22': # doubling that for the node 1, as there's no 'Podzadanie' for Funk 22
                insert_statement= """
                    INSERT INTO %s VALUES ('%s', '%s', '%s', '%s', 1, '%s', 'e', '%s', '%s', '%s', '%s', '%s', NULL, NULL, NULL, NULL, NULL, %d)
                    """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], wartosc_bazowa, wartosc_rok_obec, curr_year)
                execute_sql(insert_statement, connection)

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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, curr_year)
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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], v_total, v_nation, v_eu, v_proc_nation, v_proc_eu, curr_year)
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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], curr_year)
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
                """ % (work_tbl, idef, idef_sort, parent, parent_sort, leaf, elem_type, elem_name, row['czesc'], wartosc_bazowa, wartosc_rok_obec, curr_year)
            execute_sql(insert_statement, connection)

    # now calculating totals
    print "... calculating totals"
    # for zadanie
    select_statement= """
        SELECT parent, SUM(v_total) as sum_v_total, SUM(v_nation) as sum_v_nation, SUM(v_eu) as sum_v_eu
        FROM %s WHERE node = 0 AND elem_level = 'c' AND budg_year = %d GROUP BY parent
    """ % (work_tbl, curr_year)
    dict_cur= connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_statement)
    rows = dict_cur.fetchall()
    for row in rows:
        if row['sum_v_total'] != 0:
            v_proc_eu= round(float(row['sum_v_eu']) / float(row['sum_v_total']) * 100, 2) #percentage
            v_proc_nation= round(float(row['sum_v_nation']) / float(row['sum_v_total']) * 100, 2)
        update_statement= """
            UPDATE %s SET v_total = %d, v_nation= %d, v_eu= %d, v_proc_nation= %0.2f, v_proc_eu= %0.2f WHERE idef = '%s' AND budg_year = %d
        """ % (work_tbl, row['sum_v_total'], row['sum_v_nation'], row['sum_v_eu'], v_proc_nation, v_proc_eu, row['parent'], curr_year)
        execute_sql(update_statement, connection)

    # and podzadanie
    select_statement= "SELECT parent, SUM(v_total) as sum_v_total, SUM(v_nation) as sum_v_nation, SUM(v_eu) as sum_v_eu FROM " + work_tbl + " WHERE node = 1 AND elem_level = 'd' AND idef NOT like '22%' AND budg_year = "+str(curr_year) +" GROUP BY parent"
    dict_cur= connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(select_statement)
    rows = dict_cur.fetchall()
    for row in rows:
        if row['sum_v_total'] != 0:
            v_proc_eu= round(float(row['sum_v_eu']) / float(row['sum_v_total']) * 100, 2) #percentage
            v_proc_nation= round(float(row['sum_v_nation']) / float(row['sum_v_total']) * 100, 2)
            update_statement= """
                UPDATE %s SET v_total = %d, v_nation= %d, v_eu= %d, v_proc_nation= %0.2f, v_proc_eu= %0.2f WHERE idef = '%s' AND node = 1 AND budg_year = %d
            """ % (work_tbl, row['sum_v_total'], row['sum_v_nation'], row['sum_v_eu'], v_proc_nation, v_proc_eu, row['parent'], curr_year)
        else:
            update_statement= """
                UPDATE %s SET v_total = %d, v_nation= %d, v_eu= %d WHERE idef = '%s' AND node = 1 AND budg_year = %d
            """ % (work_tbl, row['sum_v_total'], row['sum_v_nation'], row['sum_v_eu'], row['parent'], curr_year)
        execute_sql(update_statement, connection)


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

    work_year= 2011

    mode= 'temp'
    temp_table_created, temp_table= create_table(connect_postgres, schema, mode, True) # create temporary table

    csv_parse(csv_read, temp_table, schema, connect_postgres) # fill temporary table

    mode= 'work'
    table_created, work_table= create_table(connect_postgres, schema, mode, clean_db) # create work table

    fill_work_table(work_year, temp_table, work_table, connect_postgres) # fill work table
    print '... work table is filled'

    print '... dropping temporary table'
    #delete temp table
    drop_statement= "DROP TABLE %s" % (temp_table)
    execute_sql(drop_statement, connect_postgres)
    
    print 'Done'
