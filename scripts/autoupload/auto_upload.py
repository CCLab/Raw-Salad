# -*- coding: utf-8 -*-

'''
Created on 31-08-2011
'''

import os
import optparse
import csv
import pymongo
import simplejson as json
from ConfigParser import ConfigParser
from universal.data_validator import DataValidator
from universal.data_wrapper import CsvFile, CsvData, Data
from universal.hierarchy_inserter import HierarchyInserter
from universal.schema_modifier import SchemaModifier



def get_db_connect(fullpath, dbtype):
    """Returns dict representing Connection to db.
    Arguments:
    fullpath -- path to config file
    dbtype -- type of db to connect
    """
    connect_dict= {}

    defaults= {
        'basedir': fullpath
    }

    cfg= ConfigParser(defaults)
    cfg.read(fullpath)
    connect_dict['host'] = cfg.get(dbtype,'host')
    connect_dict['port'] = cfg.getint(dbtype,'port')
    connect_dict['database'] = cfg.get(dbtype,'database')
    connect_dict['username'] = cfg.get(dbtype,'username')
    try:
        connect_dict['password'] = cfg.get(dbtype,'password')
    except:
        connect_dict['password'] = None

    return connect_dict


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


def db_insert_data(data_bulk, db, collname):
    """Inserts data to db. Data is divided to smaller parts which are then
    uploaded to db.
    
    Arguments:
    data_bulk -- list of rows to insert to database
    db -- object representing database
    collname -- name of collection that data should be inserted into
    """
    collect = db[collname]
    collect.remove()
    # TODO: check if there is better way to solve the problem
    magic_nr = 10000
    parts_nr = (len(data_bulk) / magic_nr) + 1
    for i in range(parts_nr):
        if i < parts_nr - 1:
            data_bulk_part = data_bulk[i*magic_nr:(i+1)*magic_nr]
        else:
            data_bulk_part = data_bulk[i*magic_nr:]
        collect.insert(data_bulk_part)
    return collect.find().count()


def db_insert_metadata(data_bulk, db, collname, query=None):
    """Inserts metadata to db. If query is not None, then removes
    data from db specified by that query before inserting.
    
    Arguments:
    data_bulk -- data to insert
    db -- object representing database
    collname -- name of collection in database where metadata will be inserted
    """
    collect = db[collname]
    if query is not None:
        collect.remove(query)
        collect.insert(data_bulk, check_keys=False)
        return collect.find(query).count()
    else:
        collect.insert(data_bulk, check_keys=False)


def fill_docs(data):
    """Fills information for each row in data: idef_sort, leaf,
    parent, parent_sort.
    
    Arguments:
    data -- list of rows-dicts form
    """ 
    print '-- filling out missing information'

    level_label= ['a','b','c','d','e','f']
    deepest_level= 0

    for row_doc in data:
        row_doc['idef_sort']= sort_format(row_doc['idef'])
        row_doc['leaf'] = True # for a while, will fill correctly later
        curr_level = row_doc['idef'].count('-') # count of '-' in idef tells about the level
        row_doc['level'] = level_label[curr_level]
        if curr_level > deepest_level:
            deepest_level = curr_level

        if curr_level > 0: # fill parent
            row_doc['parent'] = row_doc['idef'].rpartition('-')[0]
            row_doc['parent_sort'] = sort_format(row_doc['parent'])
        else:
            row_doc['parent'] = None # no parent at the level a
            row_doc['parent_sort'] = None
        
    print '-- correcting leaves'
    parents = {}
    for data_row in data:
        if data_row['parent'] is not None:
            parents[data_row['parent']] = True
    
    for data_row in data:
        if data_row['idef'] in parents:
            data_row['leaf'] = False
             
    print '-- !!! deepest_level is', level_label[deepest_level]

    return data



def csv_parse(csv_read, schema):
    """Parses csv file and returns data as list of dicts using schema.
    For each field, tries to cast it on the type that is described
    in schema. Because of a few ways to write float values, for float values
    tries to modify value so that it can be casted to float.
    
    Arguments:
    csv_read -- csv.Reader object created for csv file with data
    schema -- schema describing data in the file
    """
    print '-- parsing csv file'
    out= []

    dbkey_alias= schema["alias"] # dict of aliases -> document keys in db
    dbval_types= schema["type"] # dict of types -> values types in db

    for row in csv_read:
        row = iter(row)        
        for row in csv_read:
            i = 0
            dict_row = {} # this holds the data of the current row
            for field in row:
                new_key = [v for k, v in dbkey_alias.iteritems() if i == int(k)][0]
                new_type = None
                if new_key in dbval_types:
                    new_type = dbval_types[new_key]

                if new_type == "string":
                    dict_row[new_key] = str(field)
                elif new_type == "int":
                    if field == '':
                        dict_row[new_key] = None
                    else:
                        dict_row[new_key] = int(field)
                elif new_type == "float":
                    commas_in_field = field.count(',')
                    dots_in_field = field.count('.')
                    if commas_in_field > 0:
                        if dots_in_field > 0:
                            field = field.replace(',', '', commas_in_field)
                        else:
                            field = field.replace(',', '', commas_in_field - 1)
                            field = field.replace(',', '.')
                    if field == '': # fields in hierarchy rows may have empty fields
                        field = 0.0
                    dict_row[new_key] = float(field)
                elif new_type == None:
                    try:
                        dict_row[new_key] = float(field) # then if it is a number
                        if dict_row[new_key].is_integer(): # it can be integer
                            dict_row[new_key] = int(field)
                    except:
                        dict_row[new_key] = field # no, it is a string

                i += 1

            out.append(dict_row)

    return out


def open_files(csv_name, schema_descr_name, hierarchy_name):
    """Opens files with data, schema and hierarchy. Returns tuple
    containing those files.
    
    Arguments:
    csv_name -- name of csv file with data
    schema_desct_name -- name of file with schema description
    hierarchy_name -- name of file with hierarchy
    """
    print 'Trying to open csv file.'   
    try:
        csv_file = CsvFile(csv_name, quote='"', delim=';')
    except IOError:
        exit('Error: can\'t open file %s. Exiting now.' % csv_name)
        
    print 'Trying to open json file with schema description'
    try:
        schema_descr_file = open(schema_descr_name, 'rb')
        schema_descr = json.load(schema_descr_file, encoding='utf-8')
        schema_descr_file.close()
    except:
        exit('Error: during processing schema file %s. Exiting now.' % schema_descr_name)
    print 'Successfully opened file with schema'
    
    print 'Trying to open json file with hierarchy schema'
    try:
        hierarchy_file = open(hierarchy_name, 'rb')
        json_hierarchy = json.load(hierarchy_file, encoding='utf-8')
        hierarchy_file.close()
    except IOError:
        exit('Error: during processing hierarchy file.' % hierarchy_name)
    print 'Successfully opened file with hierarchy'

    return (csv_file, schema_descr, json_hierarchy)


def validate_data(csv_file, schema_descr):
    """Tries to validate data in csv file using schema description.
    Any errors that are found, are saved in file
    consts['validator_errors_name']. Returns True if no errors were found,
    otherwise False.
    
    Arguments:
    csv_file -- CsvFile object representing data
    schema_descr -- schema describing fields in collection
    """
    csv_file.reset()
    csv_data = CsvData(csv_file)
    validator = DataValidator(csv_data, schema_descr)
    validator.check_all()
    
    correct = validator.is_all_correct()
    if correct:
        print 'No errors have been found during validation.'
    else:
        print 'Errors have been found during validation.'
        errors_file_name = consts['validator_errors_name']
        print 'Saving errors to file %s' % errors_file_name
        
        try:
            errors_file = open(errors_file_name, 'wb')
        except IOError:
            print 'Can not open file %s, no info will be saved.' % errors_file_name
        else:
            errors_file.write(validator.get_errors_log())
        
    return correct


def insert_hierarchy(csv_file, json_hierarchy):
    """Inserts hierarchy into csv_file using hierarchy schema.
    
    Arguments:
    csv_file -- CsvFile object representing data
    json_hierarchy -- hierarchy schema
    """
    print 'Trying to clean hierarchy in data'
    csv_file.reset()
    csv_data = CsvData(csv_file)
    hierarchy_cleaner = HierarchyInserter(csv_data, json_hierarchy, add_id=True)
    hierarchy_cleaner.insert_hierarchy()
    if hierarchy_cleaner.all_rows_correct():
        print 'All rows have correct hierarchy'
    else:
        error_file_name = consts['hierarchy_errors_name']
        print 'Some errors in hierarchy have been found:'
        print 'Saving them to file %s' % error_file_name
        try:
            error_file = open(error_file_name, 'wb')
        except IOError:
            print 'Can not open file %s, no information will be saved.' % error_file_name
        else:
            error_file.write(hierarchy_cleaner.get_hierarchy_errors_log())
            error_file.close()
        exit()
    
    clean_data = hierarchy_cleaner.get_modified_rows()
    print 'Successfully cleaned hierarchy'
    
    csv_name = csv_file.get_filename()
    new_csv_name = csv_name.rstrip('.csv') + '_upload.csv'
    
    print 'Trying to save data with cleaned hierarchy in %s' % new_csv_name
    try:
        data_file = Data(clean_data, new_csv_name)
        data_file.save()
    except IOError:
        exit('Error: can\'t open file %s. Exiting now.' % new_csv_name)
    else:
        print 'Successfully saved data in %s' % new_csv_name
    
    return new_csv_name
        
        
def modify_schemas(json_schema, json_hierarchy, params_dict):
    """Modifies schemas and saves new schemas in new files. Returns objects
    representing modified schema and collection description.
    
    Arguments:
    json_schema -- initial schema describing fields
    json_hierarchy -- schema describing hierarchy in collection
    params_dict -- additional parameters used to create collection description
    """
    print 'Trying to create updated schema files'
    
    dataset_name = json_schema['dataset_name']
    words = dataset_name.split(' ')
    for i in range(len(words)):
        words[i] = words[i][0]
    new_schema_file_name = ''.join(words) + '-schema.json'
    modifier = SchemaModifier(json_schema, json_hierarchy)
    modifier.modify_schema(add_id=True)
    modifier.modify_coll_descr(params_dict, add_id=True)
    coll_descr_file_name = 'budg' + str(params_dict['dataset']) + str(params_dict['perspective']) +\
                           '_' + json_schema['issue'] + '.json'
    try:
        modifier.save(new_schema_file_name, coll_descr_file_name)
    except IOError:
        print 'Can not create one of files: %s, %s.' % (new_schema_file_name, coll_descr_file_name)
        return None
    else:
        print 'New schema files successfully created and saved in: %s, %s' % (new_schema_file_name, coll_descr_file_name)
    
    return (modifier.get_new_schema(), modifier.get_coll_descr())


def update_site_navigator(coll_descr, schema_descr):
    """Uses collection description and schema descr to create updated
    version of navigator. Returns this object.
    
    Arguments:
    coll_descr -- schema describing collection
    schema_descr -- initial schema description
    """
    
    nav_obj, file_name = open_last_nav_object()
    
    update_navigator_object(nav_obj, coll_descr, schema_descr)
    
    prefix = consts['navigator_name_prefix']
    last_ok = int( file_name.lstrip(prefix).rstrip('.json') )
    new_nav_file_name = prefix + str(last_ok + 1) +'.json'
    print 'Trying to save new navigator schema file.'
    try:
        new_nav_file = open(new_nav_file_name, 'wb')
        new_nav_file.write(json.dumps(nav_obj, encoding='utf-8', sort_keys=True, indent=4))
    except Exception:
        print 'Unable to save new navigator schema file.'
        exit()
    
    print 'Successfully saved navigator schema file.'
    return nav_obj


def open_last_nav_object():
    """Opens last file containing navigator object and returns it
    as object"""
    
    prefix = consts['navigator_name_prefix']
    last_ok = -2
    file_found = True
    # find last file with navigator object
    while file_found:
        last_ok += 1
        test_file_name = prefix + str(last_ok + 1) + '.json'
        file_found = os.path.isfile(test_file_name)
        
    if last_ok == -1:
        print 'Unable to find and update navigator schema file.'
        exit()
    
    
    nav_file_name = prefix + str(last_ok) + '.json'
    
    try:
        nav_file = open(nav_file_name, 'rb')
    except IOError:
        print 'Unable to open navigator schema file.'
        exit()
    
    try:
        nav_obj = json.load(nav_file, encoding='utf-8')
    except Exception as e:
        print 'Unable to process navigator schema %s.' % e
        
    nav_file.close()
    
    return (nav_obj, nav_file_name)


def update_navigator_object(nav_obj, coll_descr, schema_descr):
    """Updates navigator object. Inserts new dataset, new perspective
    or new issue, it depends on what collections are in navigator object
    already.
    
    nav_obj -- previous navigator object
    coll_descr -- schema describing collection
    schema_descr -- initial schema describing collection
    """
    dataset_found = False
    i = 0
    for dataset in nav_obj:
        if dataset['idef'] == coll_descr['dataset']:
            dataset_found = True
            break
        i += 1

    if dataset_found:
        j = 0
        persp_found = False
        for persp in nav_obj[i]['perspectives']:
            if persp['idef'] == coll_descr['idef']:
                persp_found = True
                break
            j += 1
        
        if persp_found:
            issues = nav_obj[i]['perspectives'][j]['issues']
            if coll_descr['issue'] in issues:
                pass
            else:
                nav_obj[i]['perspectives'][j]['issues'].append(coll_descr['issue'])
        else:
            perspective_descr = {
                "idef": coll_descr['idef'],
                "name": schema_descr['perspective_name'],
                "description": schema_descr['perspective_descr'],
                "long_description": schema_descr['perspectve_long_descr'],
                "issues": [ coll_descr['issue'] ]
            }
            nav_obj[i]['perspectives'].append(perspective_descr)
    else:
        dataset_descr = {
                "idef": coll_descr['dataset'],
                "name": schema_descr['dataset_name'],
                "description": schema_descr['dataset_descr'],
                "long_description": schema_descr['dataset_long_descr'],
                "perspectives": [
                    {
                        "idef": coll_descr['idef'],
                        "name": schema_descr['perspective_name'],
                        "description": schema_descr['perspective_descr'],
                        "long_description": schema_descr['perspectve_long_descr'],
                        "issues": [ coll_descr['issue'] ]
                    }
                ]
            }
        nav_obj.append(dataset_descr)


def get_collection_values(schema_descr):
    """Returns numbers of dataset and perspective that should be used to upload
    data to db, checks descriptions of previous collections in the last version
    of navigator file.
    
    Arguments:
    schema_descr -- description of collection
    collection -- collection with meta data
    """
    
    nav_obj = open_last_nav_object()[0]
    dataset_nr = 0
    persp_nr = 0
    for dataset in nav_obj:
        if dataset['name'] == schema_descr['dataset_name']:
            for perspective in dataset['perspectives']:
                if perspective['name'] == schema_descr['perspective_name']:
                    break
                persp_nr += 1
            break
        dataset_nr += 1
    return {
        'dataset': dataset_nr,
        'perspective': persp_nr
    }

consts = {
    'conf_filename': '$HOME\projects\rawsalad\src\rawsalad\site_media\rawsdata.conf',
    'coll_name': 'dd_test_2011',
    'scheme_coll_name': 'md_budg_scheme',
    'validator_errors_name': 'validator_errors.log',
    'hierarchy_errors_name': 'hierarchy_errors.log',
    'coll_descr_name': 'coll_descr.json',
    'navigator_name_prefix': 'ms_nav_structure_v',
    'navigator_coll_name': 'ms_nav'
}


def upload(args, conf_filename=None, coll_name=None, scheme_coll_name=None):
    if len(args) != 3:
        print 'Wrong number of arguments. Should be exactly 3(data, schema, hierarchy).'
        exit()
    
    if conf_filename is None:
        print 'No configuration file name specified. Using default configuration file.'
        conf_filename = consts['conf_filename']
    
    if coll_name is None:
        print 'No collection name specified. Using default collection name.'
        coll_name = consts['coll_name']
        
    if scheme_coll_name is None:
        print 'No metacollection name specified. Using default metacollection name.'
        scheme_coll_name = consts['scheme_coll_name']
    
    data_file_name = args[0]
    schema_file_name = args[1]
    hierarchy_file_name = args[2]
    
    print 'Trying to open files.'
    csv_file, schema_descr, json_hierarchy = open_files(data_file_name, schema_file_name, hierarchy_file_name)
    print 'All files were successfully opened.'
                                                    
    
    print 'Trying to validate data.'
    
    # TODO: remove when script is done
    ignore = True
    validated = validate_data(csv_file, schema_descr)
    if validated or ignore:
        print 'Data was validated.'
        new_data_file_name = insert_hierarchy(csv_file, json_hierarchy)
        
        params_dict = get_collection_values(schema_descr)
        params_dict['ns'] = coll_name
        result = modify_schemas(schema_descr, json_hierarchy, params_dict)
        
        if result is None:
            print 'Schemas couldn\'t be created, don\'t insert data to db' 
            exit()
        new_schema, coll_descr = result
    else:
        print 'Data was not validated.'
        exit()
        
    
    conn = get_db_connect(conf_filename, 'mongodb')
    conn_host = conn['host']
    conn_port = conn['port']
    conn_db = conn['database']
    
    # connect to db
    try:
        connection = pymongo.Connection(conn_host, conn_port)
        db = connection[conn_db]
        print '...connected to the database', db
    except Exception as e:
        print 'Unable to connect to the mongodb database:\n %s\n' % e
        exit()

    try:
        data_file = open(new_data_file_name, 'rb')
    except IOError as e:
        print 'Unable to open file:\n %s\n' % e
        exit()

    csv_delim= ';'
    csv_quote= '"'
    try:
        csv_read = csv.reader(data_file, delimiter=csv_delim, quotechar=csv_quote)
    except Exception as e:
        print 'Unable to read CSV file:\n %s\n' % e
        exit()

    # create temporary dict
    obj_parsed = csv_parse(csv_read, new_schema)

    # fill it out with real data
    obj_rep = fill_docs(obj_parsed) # processing and inserting the data
    
    # prepare updated version of site navigator collection
    nav_obj = update_site_navigator(coll_descr, schema_descr)

    print 'Trying to insert data into the db'
    print db_insert_data(obj_rep, db, coll_name), 'records inserted'
    
    query = {
        "dataset": coll_descr['dataset'],
        "idef": coll_descr['idef'],
        "issue": coll_descr['issue']
    }

    nav_coll_name = consts['navigator_coll_name']
    print 'Trying to insert meta data into the db'
    
    # insert metadata about collection
    print db_insert_metadata(coll_descr, db, scheme_coll_name, query), 'collection description records inserted'
    
    # insert updated site navigator object
    db_insert_metadata(nav_obj, db, nav_coll_name, {})
    print 'Done.'


if __name__ == "__main__":
    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] source_file.csv source_schema.json") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    cmdparser.add_option("-l", "--collect", action="store", dest='collection_name', help="collection name")
    cmdparser.add_option("-m", "--metacollect", action="store", dest='metacollection_name', help="meta collection name")
    opts, args = cmdparser.parse_args()
    
    upload(args, opts.conf_filename, opts.collection_name, opts.metacollection_name)
    
