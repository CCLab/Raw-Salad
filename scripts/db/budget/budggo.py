#!/usr/bin/python

"""
import Budzet Zadaniowy to mongo db
flat structure (each data unit is a separate doc in the collection)
parenting is archieved through 'parent' key

the structure:
there are 2 'branches of the tree' of a budget structure, outlined in the
collection as 'node':0 and 'node':1. first two levels are common, so
they are labelled as 'node':null

nodes are:
0: [funkcja] 1-N [zadanie] 1-N [dysponent] 1-N [cel] 1-N [miernik]
1: [funkcja] 1-N [zadanie] 1-N [podzadanie] 1-N [dysponent, cel, miernik]

the lowest level in both nodes for which values (money) are given is 'dysponent'
thus, if a= (total of funkcja[N].zadanie[M].dysponent[K].value where node= 0)
and b= (total of funkcja[N].zadanie[M].podzadanie[NM]dysponent[K].value where node= 1)
than a == b is True (a should be equal to b)


the script also inserts a doc into the schema collection
(warning! if there's already a schema for the budget collection, it should first
be removed manually from the collection data_zz_schema)

the files needed to upload the budget:
- this file (budget.py)
- data file CSV, produced from XLS (for example, budget.csv)
- schema file JSON (for example, budget-schema.json)

type python budget.py -h for instructions
"""
import getpass
import os
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

# copy dysponent from node 0 to 1:
# if there is no 'podzadanie' in some function in node 1,
# list of 'dysponents' should be copied as (!!!)child elements of zadanie(!!!)
def copy_dysp(db, collname, func_num):
    out= []
    collect= db[collname]
    collcrr_p_d= collect.find({'node':0 ,'level':'c','idef':{'$regex':func_num+'.'}},{'_id':0}) # collecting all 'dysponents' of specified function
    for row in collcrr_p_d:
        new_row= row.copy()
        new_row['leaf']= True # changing just a bit
        new_row['node']= 1
        out.append(new_row)

    return out


# node 1
def fill_p_dysp(db, collname, colltmp, objlst):
    out= objlst[:] # copy of list containing 'podzadanie'

    clltmp= db[colltmp]
    cllact= db[collname]

    for podz in objlst: # iterating through podzadanie
        podz_curr= podz['idef'].replace('-','.') # have to look through old codes with '.' separator
        collcrr_p_d= clltmp.find({'test_p_d':True, 'numer':podz_curr}, {'_id':0}) # collecting all 'dysponents' of all 'podzadanie'
        tmp, podz_v_eu, podz_v_nation, podz_v_total = 0, 0, 0, 0
        for row in collcrr_p_d:
            fpd= {}
            tmp += 1
            name_p_d= row['dysponent'].strip()
            czesc_p_d= row['czesc']
            curr_zd_idef_lst= row['numer'].split('.')
            curr_zd_idef= curr_zd_idef_lst[0] + '-' + curr_zd_idef_lst[1] # have to search in the scope of current 'zadanie'
            #we already have 'idef' for all dysponents of zadanie - just look for it in the previously inserted data
            p_d_idef= cllact.find_one({'node':0, 'level':'c', 'czesc':czesc_p_d, 'parent':curr_zd_idef, 'name':name_p_d}, {'idef':1, '_id':0})
            fpd['idef']= p_d_idef['idef']
            fpd['type']= 'Dysponent'
            fpd['name']= name_p_d
            fpd['parent']= row['numer'].replace('.', '-') # idef of "podzadanie"
            fpd['node']= 1 # "dysponent" has a direction
            fpd['level']= 'd'
            fpd['leaf']= True # this level is the deepest one in node 1
            fpd['czesc']= czesc_p_d
            fpd['cel']= row['cel']
            fpd['miernik_nazwa']= row['miernik_nazwa']
            fpd['miernik_wartosc_bazowa']= row['miernik_wartosc_bazowa']
            fpd['miernik_wartosc_rb']= row['miernik_wartosc_rok_obec']
            fpd['v_total']= row['ogolem'] # this is the last object
            fpd['v_nation']= row['budzet_panstwa']
            fpd['v_eu']= row['budzet_srodkow_europejskich']
            if fpd['v_total'] != 0:
                fpd['v_proc_eu']= round(float(fpd['v_eu']) / float(fpd['v_total']) * 100, 2) # percentage
                fpd['v_proc_nation']= round(float(fpd['v_nation']) / float(fpd['v_total']) * 100, 2)
            podz_v_eu += fpd['v_eu'] # calculating totals for current podzadanie
            podz_v_nation += fpd['v_nation']
            podz_v_total += fpd['v_total']
        
            out.append(fpd)

        podz_curr= podz_curr.replace('.','-') # changing back - now we look through updated codes
        for elem in out: # update totals of current podzadanie
            if elem['idef'] == podz_curr:
                elem['v_total'], elem['v_nation'], elem['v_eu'] = podz_v_total, podz_v_nation, podz_v_eu
                if elem['v_total'] != 0:
                    elem['v_proc_eu']= round(float(elem['v_eu']) / float(elem['v_total']) * 100, 2) # percentage
                    elem['v_proc_nation']= round(float(elem['v_nation']) / float(elem['v_total']) * 100, 2)
                break

    return out



def fill_podzadanie(db, clltmp):
    out= []

    collect= db[clltmp]
    collcrr_p= collect.find({'test_p':True}, {'_id':0}) # getting list of "podzadanie"
    for row_p in collcrr_p:
        fpz= {}
        fpz['idef']= row_p['numer'].replace('.', '-')
        fpz['type']= 'Podzadanie '+row_p['numer']
        fpz_zd_idef= row_p['numer'].split('.', 3)
        fpz['parent']= fpz_zd_idef[0]+'-'+fpz_zd_idef[1] # idef of "zadanie"
        name_tmp= row_p['podzadanie'].lstrip(row_p['numer'])
        fpz['name']= name_tmp.strip()
        fpz['node']= 1 # "podzadanie" has a direction
        fpz['level']= 'c'
        fpz['leaf']= False
        fpz['v_total']= None # no data on this level
        fpz['v_nation']= None
        fpz['v_eu']= None
        fpz['v_proc_eu']= None
        fpz['v_proc_nation']= None

        out.append(fpz)

    return out


# node 0
def fill_z_d_c_mier(db, cllname, clltmp):
    out= []
    check_id= []

    collmain= db[cllname]
    collmn= db[cllname]
    colltmp= db[clltmp]
    collcrr_dysp= collmain.find({'level':'d', 'node':0}, {'idef':1, 'parent':1, 'czesc':1, 'name':1, '_id':0}) # first getting the list of "cel" and their parents
    for row in collcrr_dysp:
        ds_curr= row['parent'] # current "dysponent" of "zadanie"
        collcrr_tmp= collmn.find_one({'idef':ds_curr}, {'name':1, '_id':0})
        ds_name= collcrr_tmp['name'] # "dysponent" name
        zd_curr_str= ds_curr.split('-', 3)
        zd_curr= zd_curr_str[0]+'.'+zd_curr_str[1] # current "zadanie" ('.' is just to look through temp table, where all the codes separated by '.')
        cl_curr= row['idef'] # current "cel"
        cl_name= row['name'] # current "cel" name
        ds_czesc_curr= row['czesc'] # current "czesc"

        cl_m_num= 0 # 'miernik' numerator

        # this is the last level, so, every other time we add the doc to [out], we delete it from collection
        # so that it will not be doubled

        # first processing records where we have everything: "dysponent", "cel", and "miernik"
        collcrr_m1= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'dysponent':ds_name, 'cel': cl_name, 'test_z_d':True, 'test_z_c':True, 'test_z_m':True})
        if collcrr_m1.count() != 0:
            for row_z_m in collcrr_m1:
                if row_z_m['_id'] not in check_id:
                    ffm= {}
                    cl_m_num += 1
                    ffm['name']= row_z_m['miernik_nazwa']
                    full_cl_m_num= cl_curr + '-' + str(cl_m_num)
                    ffm['idef']= full_cl_m_num
                    ffm['type']= 'Miernik'
                    ffm['parent']= cl_curr # idef of "cel"
                    ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
                    ffm['level']= 'e'
                    ffm['leaf']= True # now - this level is the deepest in node 0
                    ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
                    ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
                    ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
                    ffm['v_total']= None # no values on the level of "miernik"
                    ffm['v_nation']= None
                    ffm['v_eu']= None
                    ffm['v_proc_eu']= None
                    ffm['v_proc_nation']= None

                    out.append(ffm)
                    check_id.append(row_z_m['_id'])

        # second - "cel", and "miernik"
        collcrr_m2= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'cel': cl_name, 'test_z_d':False, 'test_z_c':True, 'test_z_m':True})
        if collcrr_m2.count() != 0:
            for row_z_m in collcrr_m2:
                if row_z_m['_id'] not in check_id:
                    ffm= {}
                    cl_m_num += 1
                    ffm['name']= row_z_m['miernik_nazwa']
                    full_cl_m_num= cl_curr + '-' + str(cl_m_num)
                    ffm['idef']= full_cl_m_num
                    ffm['type']= 'Miernik'
                    ffm['parent']= cl_curr # idef of "cel"
                    ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
                    ffm['level']= 'e'
                    ffm['leaf']= True # now - this level is the deepest in node 0
                    ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
                    ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
                    ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
                    ffm['v_total']= None # no values on the level of "miernik"
                    ffm['v_nation']= None
                    ffm['v_eu']= None
                    ffm['v_proc_eu']= None
                    ffm['v_proc_nation']= None

                    out.append(ffm)
                    check_id.append(row_z_m['_id'])

        # third - "miernik" only
        collcrr_m3= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, 'cel':None, 'test_z_d':False, 'test_z_c':False, 'test_z_m':True})
        if collcrr_m3.count() != 0:
            for row_z_m in collcrr_m3:
                if row_z_m['_id'] not in check_id:
                    ffm= {}
                    cl_m_num += 1
                    ffm['name']= row_z_m['miernik_nazwa']
                    full_cl_m_num= cl_curr + '-' + str(cl_m_num)
                    ffm['idef']= full_cl_m_num
                    ffm['type']= 'Miernik'
                    ffm['parent']= cl_curr # idef of "cel"
                    ffm['node']= 0 # "miernik" follows the direction of "zadanie-dysponent-cel"
                    ffm['level']= 'e'
                    ffm['leaf']= True # now - this level is the deepest in node 0
                    ffm['czesc']= row_z_m['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
                    ffm['miernik_wartosc_bazowa']= row_z_m['miernik_wartosc_bazowa']
                    ffm['miernik_wartosc_rb']= row_z_m['miernik_wartosc_rok_obec']
                    ffm['v_total']= None # no values on the level of "miernik"
                    ffm['v_nation']= None
                    ffm['v_eu']= None
                    ffm['v_proc_eu']= None
                    ffm['v_proc_nation']= None

                    out.append(ffm)
                    check_id.append(row_z_m['_id'])
    return out


def fill_z_d_cel(db, cllname, clltmp):
    out= []

    collmain= db[cllname]
    colltmp= db[clltmp]
    collcrr_dysp= collmain.find({"level":"c", "node":0}, {"idef":1, "parent":1, "czesc":1, "name":1, "_id":0}) # first getting the list of "dysponent" and their parents
    for row in collcrr_dysp:
        zd_curr= row['parent'].replace('-','.') # current "zadanie" (replace '-' to '.' for search in temp table)
        ds_curr= row['idef'] # current "dysponent"
        ds_name= row['name'] # current "dysponent" name
        ds_czesc_curr= row['czesc'] # current "czesc"
        
        cl_d_num= 0
        # first processing records of both "cel" & "dysponent"
        collcrr_z_c= colltmp.find({'numer':zd_curr, 'dysponent':ds_name, "test_z_d":True, "test_z_c":True}, {"_id":0})
        for row_z_c in collcrr_z_c:
            ffc= {}
            ffc['name']= row_z_c['cel']
            cl_d_num += 1
            full_cl_d_num= ds_curr + '-' + str(cl_d_num)
            ffc['idef']= full_cl_d_num
            ffc['type']= 'Cel'
            ffc['parent']= ds_curr # idef of "dysponent"
            ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            ffc['node']= 0 # "cel" follows the direction of "dysponent"
            ffc['level']= 'd'
            ffc['leaf']= False # it isn't the deepest level
            ffc['v_total']= None # no values on the level of "cel"
            ffc['v_nation']= None
            ffc['v_eu']= None
            ffc['v_proc_eu']= None
            ffc['v_proc_nation']= None


            out.append(ffc)

        # now "cel" without "dysponent", looking for it via "czesc"
        collcrr_z_c= colltmp.find({'numer':zd_curr, 'czesc':ds_czesc_curr, "test_z_d":False, "test_z_c":True}, {"_id":0})
        for row_z_c in collcrr_z_c:
            ffc= {}
            ffc['name']= row_z_c['cel']
            cl_d_num += 1
            full_cl_d_num= ds_curr + '-' + str(cl_d_num)
            ffc['idef']= full_cl_d_num
            ffc['type']= 'Cel'
            ffc['parent']= ds_curr # idef of "dysponent"
            ffc['czesc']= row_z_c['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            ffc['node']= 0 # "cel" follows the direction of "dysponent"
            ffc['level']= 'd'
            ffc['leaf']= False # it isn't the deepest level
            ffc['v_total']= None # no values on the level of "cel"
            ffc['v_nation']= None
            ffc['v_eu']= None
            ffc['v_proc_eu']= None
            ffc['v_proc_nation']= None

            out.append(ffc)

    return out

def fill_z_dysponent(db, colltmp, objlst):
    out= objlst[:]

    collect= db[colltmp]
    collcrr_zdnum= collect.find({"test_z":True}, {"numer":1, "_id":0}) # collecting the numbers of "zadanie"
    for row in collcrr_zdnum:
        zd_curr= row['numer'] # current "zadanie"
        zd_d_num, zd_v_eu, zd_v_nation, zd_v_total = 0, 0, 0, 0
        collcrr_z_d= collect.find({'numer':zd_curr, "test_z_d":True}, {"_id":0}) # getting "dysponent" of current "zadanie"
        for row_z_d in collcrr_z_d:
            fzd= {}
            zd_d_num += 1
            full_zd_d_num= row_z_d['numer'].replace('.','-') + '-dt' + str(zd_d_num) # 'dysponent' code becomes N-M-dtK
            fzd['idef']= full_zd_d_num
            fzd['type']= 'Dysponent'
            fzd['name']= row_z_d['dysponent']
            fzd['parent']= row_z_d['numer'].replace('.', '-') # idef of "zadanie"
            fzd['czesc']= row_z_d['czesc'] # technical key for connecting 'parent-child' links dysponent-cel and cel-miernik
            fzd['node']= 0 # "dysponent" has a direction
            fzd['level']= 'c'
            fzd['leaf']= False # it isn't the deepest level
            fzd['v_total']= row_z_d['ogolem'] # this is the last object
            fzd['v_nation']= row_z_d['budzet_panstwa']
            fzd['v_eu']= row_z_d['budzet_srodkow_europejskich']
            if fzd['v_total'] != 0:
                fzd['v_proc_eu']= round(float(fzd['v_eu']) / float(fzd['v_total']) * 100, 2) # percentage
                fzd['v_proc_nation']= round(float(fzd['v_nation']) / float(fzd['v_total']) * 100, 2)
            zd_v_eu += fzd['v_eu']
            zd_v_nation += fzd['v_nation']
            zd_v_total += fzd['v_total']

            out.append(fzd)

        zd_curr= zd_curr.replace('.','-') # now we look through updated codes
        for elem in out: # update totals of current zadanie
            if elem['idef'] == zd_curr:
                elem['v_total'], elem['v_nation'], elem['v_eu'] = zd_v_total, zd_v_nation, zd_v_eu # values
                if elem['v_total'] != 0:
                    elem['v_proc_eu']= round(float(elem['v_eu']) / float(elem['v_total']) * 100, 2) # percentages
                    elem['v_proc_nation']= round(float(elem['v_nation']) / float(elem['v_total']) * 100, 2)
                break
    
    return out


def fill_zadanie(db, colltmp, objlst):
    out= objlst[:]
    collect= db[colltmp]
    colltmpcrr= collect.find({"test_z":True}, {"_id":0}) # looking only for "zadanie"

    for row in colltmpcrr:
        tmpdict= dict(row)
        ffz= {}
        ffz['idef']= tmpdict['numer'].replace('.','-')
        zd_type_name= tmpdict['funkcja_zadanie'].rsplit('.', 2) # extract "funkcja_zadanie"
        ffz['type']= 'Zadanie ' + zd_type_name[0].strip() + '.' + zd_type_name[1].strip()
        ffz['name']= zd_type_name[2].strip()
        ffz['parent']= zd_type_name[0].strip() # idef of "zadanie"
        ffz['node']= None # "zadanie" is not a root, but it still doesn't have a 'direction'
        ffz['level']= 'b' # 2nd level in the hierarchy
        ffz['leaf']= False # it isn't the deepest level
        ffz['v_total']= None # no info about money on that level
        ffz['v_nation']= None
        ffz['v_eu']= None
        ffz['v_proc_eu']= None
        ffz['v_proc_nation']= None

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
        frr['idef']= frr.pop('numer').replace('.', '-') # change "numer" to "identifier" replaceing dots with dashes
        funk_type_name= frr.pop('funkcja_zadanie').split('.', 2) # extract "funkcja_zadanie"
        if frr['idef'] == '999999':
            frr['type']= 'total'
            frr['name']= funk_type_name[0].strip()
            frr['leaf']= True # in case of grand total it's the last level (no children)
        else:
            frr['type']= funk_type_name[0].strip()
            frr['name']= funk_type_name[1].strip()
            frr['leaf']= False # not the deepest level
        frr['parent']= None # "funkcja" is the root
        frr['node']= None # "funkcja" doesn't have a 'direction'
        frr['level']= 'a' # the highest level in the hierarchy
        frr['leaf']= False # not the deepest level
        frr['v_total']= frr.pop('ogolem') # change "ogolem" to "total" of the current year
        frr['v_nation']= frr.pop('budzet_panstwa') # the same for state budget
        frr['v_eu']= frr.pop('budzet_srodkow_europejskich') #the same for EU part in the budget
        if frr['v_total'] != 0:
            frr['v_proc_eu']= round(float(frr['v_eu']) / float(frr['v_total']) * 100, 2) #percentage
            frr['v_proc_nation']= round(float(frr['v_nation']) / float(frr['v_total']) * 100, 2)
        out.append(frr)

    return out


def fill_rep(db, colltmp, collname, cleandb):
    out= []
    # filling containers for all kinds of data successively
    dict_funk= fill_funkcja(db, colltmp) # "funkcja"
    print '-- funkcja:', len(dict_funk)
    dict_zadanie= fill_zadanie(db, colltmp, dict_funk) # "zadanie"
    print '-- funkcja-zadanie:', len(dict_zadanie)

    # filling out node 1 (zadanie - dysponent - cel - miernik)
    dict_zd_dysp= fill_z_dysponent(db, colltmp, dict_zadanie) # "dysponent"
      #and this is precisely the moment to insert the first bulk of data into the db,
      #'cause there are already docs with artificially created identifiers
    print '-- node 0: funkcja-zadanie-dysponent:', len(dict_zd_dysp), '; total:', db_insert(dict_zd_dysp, db, collname, cleandb)
    dict_zd_dysp_cel= fill_z_d_cel(db, collname, colltmp) # "cel"
    print '-- node 0: funkcja-zadanie-dysponent-cel:', len(dict_zd_dysp_cel), '; total:', db_insert(dict_zd_dysp_cel, db, collname, False) # append, no db clean!
    dict_zd_dysp_cel_mr= fill_z_d_c_mier(db, collname, colltmp) # "miernik"
    print '-- node 0: funkcja-zadanie-dysponent-cel-miernik:', len(dict_zd_dysp_cel_mr), '; total:', db_insert(dict_zd_dysp_cel_mr, db, collname, False) # append, no db clean!

    # filling out node 1 (zadanie - podzadanie - dysponent (with cel and miernik at the same level))
    dict_podz= fill_podzadanie(db, colltmp) # "podzadanie"
    print '-- node 1: podzadanie:', len(dict_podz) # no insert here, because it's necessary to calculate totals for podzadanie
    dict_podz_dysp= fill_p_dysp(db, collname, colltmp, dict_podz) # "dysponent" (we need both updated "collname" and "colltmp" here)
    print '-- node 1: podzadanie-dysponent:', len(dict_podz_dysp), '; total:', db_insert(dict_podz_dysp, db, collname, False)
    # VERY SPECIFIC - FOR TASK 22 ONLY
    dict_copy_dysp= copy_dysp(db, collname, '22') # "dysponent" (we need both updated "collname" and "colltmp" here)
    print '-- node 0 to 1: copy dysponent:', len(dict_copy_dysp), '; total:', db_insert(dict_copy_dysp, db, collname, False)
    # get the data from db and return for json file
    out= db[collname].find({}, {'_id':0}) # collecting everything
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
    cmdparser.add_option("-u", "--usr", action="store", help="database admin login")
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

    #username - ask for password
    usrname= opts.usr
    pprompt = getpass.getpass()

    #try to connect and authenticate
    try:
        mongo_connect= pymongo.Connection("localhost", 27017)
        work_db= mongo_connect[dbname]
    except Exception as e:
        print 'Unable to connect to the database:\n %s\n' % e
        exit()

    try:
        work_db.authenticate(usrname, pprompt)
    except Exception as e:
        print 'Unable to authenticate to the database:\n %s\n' % e
        exit()
    
    coll_tmp= collectname + 'temp' # collection for temporary results

    # insert the object parsed from csv to the temporary collection, get the num of records
    mongo_connect.start_request()
    recs= db_insert(obj_parsed, work_db, coll_tmp, clean_db)
    print 'temporary collection created - '+ dbname +'.'+ coll_tmp + ': ' + str(recs) + ' records'
    mongo_connect.end_request()
    # create final dict
    mongo_connect.start_request()
    obj_rep= fill_rep(work_db, coll_tmp, collectname, clean_db)
    mongo_connect.end_request()

    print 'temporary collection processed - dropping '+ dbname +'.'+ coll_tmp
    #work_db[coll_tmp].drop()

    # saving into json file
    if opts.json_filename is not None:
        try:
            json_write= open(opts.json_filename, 'w')
        except IOError as e:
            print 'Unable to open file:\n %s\n' % e
            print '\n %s\n Non fatal error - continuing processing'

        rows= [] # first save the result into the list
        for obj in obj_rep:
            rows.append(obj)

        try:
            print >>json_write, json.dumps(rows, indent=4)
        except IOError as writerr:
            print 'Unable to save out_file:\n %s\n' % writerr
        finally:
            src_file.close()
            json_write.close()
            print "File saved: " + opts.json_filename

    #meta info
    meta_info= schema['meta']
    meta_name= meta_info['name']
    meta_perspective= meta_info['perspective']
    meta_collnum= meta_info['idef']
    meta_explore= meta_info['explorable']
    meta_collection= dict(zip(('idef', 'name', 'perspective', 'collection', 'explorable'), (meta_collnum, meta_name, meta_perspective, collectname, meta_explore)))
    meta_collection['columns']= schema['columns']

    schema_coll= 'md_budg_scheme'
    print 'updating schema collection:', db_insert(meta_collection, work_db, schema_coll, False), 'records in', schema_coll
    print 'Done'
