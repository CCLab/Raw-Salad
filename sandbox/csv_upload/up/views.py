# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from csv_upload.up.forms import *

from csv import DictReader
import re
import simplejson as json
import rsdbapi as rsdb
from data_validator import DataValidator
from hierarchy_inserter import HierarchyInserter
from data_wrapper import CsvFile, CsvData, Data

def home( req ):
    f = FirstStepForm()

    return render_to_response( 'home.html', { 'form': f } )


@csrf_exempt
def upload( req ):
    # treat form as a multipart one
    form = FirstStepForm( req.POST, req.FILES )
    # server-side validation (to be changed to client-side on deploy)
    if not form.is_valid():
        return render_to_response( 'home.html', { 'form': form } )

    tmp_name = 'tmp/' + req.POST['abbr'] + '.csv'
    tmp_file = open( tmp_name, 'w' )
    upl_file = req.FILES.get( 'file', '' )

    for chunk in upl_file.chunks():
        tmp_file.write( chunk );
    tmp_file.close()

    upl_file.seek( 0 )

    dataset_id, view_id = find_ids(req.POST['dataset'], req.POST['view'])

    # update nav tree
    nav_dict= define_nav_id({
        'dataset': dataset_id,
        'view': view_id,
        'issue': req.POST.get( 'issue', None ),
        'dataset_name': req.POST.get( 'dataset', '' ),
        'dataset_descr': req.POST.get( 'ds_desc', '' ),
        'view_name': req.POST.get( 'view', '' ),
        'view_descr': req.POST.get( 'vw_desc', '' )
        } )

    # temporary way to signalize that tuple (dataset_id, view_id, issue) is not unique
    if nav_dict is None:
        return home(req)

    # default settings
    nav_dict['dataset_long_descr'] = None
    nav_dict['view_long_descr'] = None

    # actual csv processing goes here
    ns_name= req.POST.get( 'abbr', 'xxxxxx' )
    ns_name= re.sub(r'[\W\s]+', '_', ns_name.lower(), re.U)
    ns_name= 'du_' + ns_name[:6] + nav_dict['issue']
    meta_data_draft= {
        'dataset': nav_dict['dataset'],
        'idef': nav_dict['view'],
        'issue': nav_dict['issue'],
        'name': req.POST.get( 'abbr', 'xxxxxx' ),
        'perspective': req.POST.get( 'view', '' ),
        'ns': ns_name,
        'explorable': None, # to define upon data upload
        'max_level': None # to define upon data upload
        }
    delim = str( req.POST.get( 'delim', ';' ) )

    columns= process_csv( upl_file, delim )
    meta_data_draft.update({ 'columns': columns })
    req.session['meta_data_draft'] = meta_data_draft
    req.session['navigator'] = nav_dict
    req.session['data_file'] = tmp_name

    return render_to_response( 'meta.html', { 'file_name': upl_file.name, 'data': columns } )


@csrf_exempt
def save_metadata( req ):
    columns_update = json.loads( req.POST.get( 'metadata', [] ) )
    req.session['meta_data_draft']['columns'] = columns_update
    req.session.modified = True

    return render_to_response( 'advanced.html', { 'data': req.session['meta_data_draft']['columns'] })


@csrf_exempt
def save_advanced( req ):
    advanced = json.loads( req.POST.get( 'advanced', {} ) )
    meta_data= req.session['meta_data_draft']
    nav_dict = req.session['navigator']
    file_name = req.session['data_file']

    print 'advanced', advanced

    meta_data['sort']= convert_sort(advanced['order'])
    meta_data['batch_size']= advanced['batch_size']

    # TODO: change type of hierarchy information passed
    advanced['hierarchy'] = [{'name': name, 'change_type': True} for name in advanced['hierarchy']]
    advanced['field_type_label'] = 'Typ'
    advanced['field_name_label'] = 'Nazwa'

    # TODO: add obligatory parameter in columns decription
    for column_descr in meta_data['columns']:
        column_descr['obligatory'] = False

    hierarchy_info = create_hierarchy_info(advanced, meta_data['columns'])

    validator = DataValidator(file_name, meta_data['columns'])
    validator.check_all()
    # TODO: pass delimiter to DataValidator, HierarchyInserter constructors
    if validator.is_all_correct():
        hierarchy_inserter = HierarchyInserter(file_name, hierarchy_info, meta_data['columns'])
        print 'old hierarchy = '
        for x in meta_data['columns']:
            print x['key']

        hierarchy_inserter.insert_hierarchy()
        
        if hierarchy_inserter.all_rows_correct():
            modified_rows = hierarchy_inserter.get_modified_rows()
            meta_data['columns'] = hierarchy_inserter.get_columns_description()
            
            print 'modified_rows = ', modified_rows
            print 'new hierarchy = '
            for x in meta_data['columns']:
                print x['key']
            print '------------------------'
            modified_data = Data(modified_rows)
            modified_data.save(file_name) # clean source file and save trasnformed data in it
            db = rsdb.DBconnect("mongodb").dbconnect

            print 'ns = ', meta_data['ns']
            upload_data_file(db, meta_data['ns'], file_name, meta_data['columns'])

            update_navigator(db, rsdb.nav_schema, nav_dict)

            coll= rsdb.Collection()
            ds_id, ps_id, iss, update_status= coll.save_complete_metadata(meta_data, db)
            print ds_id, ps_id, iss, update_status
        else:
            errors_log = hierarchy_inserter.get_errors_log()
            # TODO: return page with errors

    else:
        # TODO: remove print
        print 'DATA NOT VALIDATED'
        errors_log = validator.get_errors_log()
        # TODO: return page with errors

    return HttpResponseRedirect( '/' )


def process_csv( src_file, delim ):
    """
    process user uploaded CSV file
    and create a proposed meta-data dict
    """
    csv_delim= delim
    csv_quote= '"'

    csv_dict= DictReader(src_file, skipinitialspace= True, delimiter= csv_delim, quotechar= csv_quote)

    columns_list= fill_column_names( csv_dict.fieldnames )
    columns_list= fill_column_types( columns_list, csv_dict )

    return columns_list

def fill_column_types(columns, csvdict):
    out= columns[:]

    for row in csvdict.reader: # checking rows to guess types
        i= 0 # field index   # !!! WARNING !!! don't miss restval param of DictReader! (number of values if bigger than in the header)
        for clm in csvdict.fieldnames:
            if len(str(row[i])) > 0: # not enough for analysis
                currval= replace_locale_symbols( row[i].strip() )
                if not re.match(r'^[-+]?[0-9\,]*\.?[0-9]+([eE][-+]?[0-9]+)?$', currval): # this id NOT float or int
                    new_type= 'string'
                else: # float or int
                    # checking different formats
                    comma_sepr_whole= currval.split(',')
                    space_sepr_whole= currval.split(' ')
                    if len(comma_sepr_whole) > 1:
                        if len(comma_sepr_whole) == 2: # #####0,00
                            if '.' in comma_sepr_whole[-1]: # situation 156,150.77 -> [156, 150.77]
                                currval= currval.replace(',', '')
                            else: # situation 156,15 -> [156, 15]
                                currval= currval.replace(',', '.')
                        else: # ###,##0.00 or ###,##0
                            currval= currval.replace(',', '')
                    elif len(space_sepr_whole) > 1: # ### ##0.00 or # ### ##0
                        currval= currval.replace(' ', '')

                    new_type= check_type(currval)

                out[i]['type_tmp']= new_type
                if new_type == 'float':
                    new_prec= len(str(row[i]).split(".")[-1])
                    try:
                        cur_prec= columns[i]['type_precision']
                    except:
                        cur_prec= 0
                    out[i]['type_precision']= max( new_prec, cur_prec )
            i += 1

    # filling formats
    for out_doc in out:
        if out_doc['type_tmp'] in ['int', 'float']:

            # filling type
            out_doc['type']= 'number'
            out_doc['checkable']= True
            out_doc['format']= '# ##0'

            # filling format
            if 'type_precision' in out_doc:
                if out_doc['type_precision'] > 0:
                    out_doc['format'] += '.'
                    j= 0
                    while j < out_doc['type_precision']:
                        j += 1
                        out_doc['format'] += '0'

                    no_red_format= out_doc['format']
                    out_doc['format'] += ';[RED]-' + no_red_format

                del out_doc['type_precision']

        del out_doc['type_tmp']

    return out

def check_type(val):
    try:
        val= float(val)
        tp= 'float'
        if val.is_integer():
            tp= 'int'
    except:
        tp= 'string'

    return tp


def fill_column_names(field_names):
    """
    cleaning the header:
    - everything to lowercase
    - empty column name -> column_N (N is a number)
    - delete dots (.) in the end of a name
    - \n, /, \, +, -, *, ' ', etc. -> _
    - [ą, ć, ę, ł, ń, ó, ś, ź, ż, Ą, Ć, Ę, Ł, Ń, Ó, Ś, Ź, Ż] ->
      [a, c, e, l, n, o, s, z, z, A, C, E, L, N, O, S, Z, Z]
    """

    basic_keywords= ['id', 'idef', 'numer', 'number', 'typ', 'type', 'name', 'nazwa', 'total', 'ogolem']

    out= []
    i= 0

    for field in field_names:
        i += 1
        label= field.strip().replace('\n', ' ')
        if len(label) == 0: # field with no name
            label= 'Pole %s' % i
        key= re.sub(r'[\W\s]+', '_', replace_locale_symbols(label.lower()), re.U)
        key= re.sub(r'_$', '', key)

        basic, processable= False, True
        for kw in basic_keywords:
            if kw in key:
                basic= True
                break

        out.append({
            'label': label,
            'key': key,
            'type': 'string', # will be updated later
            'format': r'@', # text as default, but will be updated later
            'basic': basic,
            'processable': processable,
            'checkable': False # will turn True, if it is a number
            })

    return out

def convert_sort(sort_list):
    out= {}
    if len(sort_list) > 0:
        cnt= 0
        for elm in sort_list:
            kv= [(k,v) for k,v in elm.iteritems()][0]
            if kv[1] == 'Ascending':
                dr= 1
            else:
                dr= -1
            out[str(cnt)]= { kv[0]: dr }
            cnt += 1

    return out

def define_nav_id(navig_dict):
    """
    check if there are such dataset and view in the navigation tree,
    if there are none, code them and save to the tree
    """
    db= rsdb.DBconnect("mongodb").dbconnect
    navtree= rsdb.Navtree()

    if navig_dict['dataset'] is None: # no such dataset in the db
        dataset= navtree.get_max_dataset(db)
        navig_dict['dataset']= dataset+1
        navig_dict['view']= 0 # the new dataset, so, the view is 0
    else:
        if navig_dict['view'] is None: # no such view of the dataset
            view= navtree.get_max_view(db, int(navig_dict['dataset'])) # check if there's such view
            navig_dict['view']= view+1
            need_insert= True
        else: # there's already such dataset and view - check if given issue is unique
            if navig_dict['issue'] in navtree.get_issue( db, navig_dict['dataset'], navig_dict['view'] ):
                return None # error - issue already exist!

    return navig_dict

def replace_locale_symbols(src): # find smarter way to do it!
    return src.replace(r'ą', 'a').replace(r'ć', 'c').replace(r'ę', 'e').replace(r'ł', 'l')\
           .replace(r'ń', 'n').replace(r'ó', 'o').replace(r'ś', 's').replace(r'ź', 'z')\
           .replace(r'ż', 'z').replace(r'Ą', 'A').replace(r'Ć', 'C').replace(r'Ę', 'E')\
           .replace(r'Ł', 'L').replace(r'Ń', 'N').replace(r'Ó', 'O').replace(r'Ś', 'S')\
           .replace(r'Ź', 'Z').replace(r'Ż', 'Z')


def find_ids(dataset_name, view_name):
    """ Finds id of dataset [and optionally view] which name is dataset_name
        [and optional view's name is view name]
        Returns tuple containing seeked ids, if id is not found, then it becomes None
    """
    dataset_id = view_id = None
    db= rsdb.DBconnect("mongodb").dbconnect
    
    navtree = rsdb.Navtree()
    datasets = navtree.get_dataset(db)
    for dataset in datasets:
        if dataset['name'] == dataset_name:
            dataset_id = dataset['idef']
            break
    
    if dataset_id:
        views = navtree.get_view(db, dataset_id)
        for view in views:
            if view['name'] == view_name:
                view_id = view['idef']
                break

    return dataset_id, view_id


def update_navigator(db, nav_coll, nav_dict):
    """ Updates site navigator collection with nav_dict containing information
        about changed part, db and nav_coll specify database and collection.
    """
    navtree = rsdb.Navtree()
    coll = db[nav_coll]
    if nav_dict['dataset'] == navtree.get_max_dataset(db) + 1: # no such dataset in the db
        dataset_obj = {
            'idef': nav_dict['dataset'],
            'name': nav_dict['dataset_name'],
            'description': nav_dict['dataset_descr'],
            'long_description': nav_dict['dataset_long_descr'],
            'perspectives': [
                {
                    'idef': nav_dict['view'],
                    'name': nav_dict['view_name'],
                    'description': nav_dict['view_descr'],
                    'long_description': nav_dict['view_long_descr'],
                    'issues': [ nav_dict['issue'] ]
                }
            ]
        }
    
    elif nav_dict['view'] == navtree.get_max_view(db, int(nav_dict['dataset'])) + 1:
        dataset_obj = coll.find_one({'idef': nav_dict['dataset']})
        view_obj = {
            'idef': nav_dict['view'],
            'name': nav_dict['view_name'],
            'description': nav_dict['view_descr'],
            'long_description': nav_dict['view_long_descr'],
            'issues': [ nav_dict['issue'] ]
        }
        dataset_obj['perspectives'].append(view_obj)
    else:
        dataset_obj = coll.find_one({'idef': nav_dict['dataset']})
        try:
            view_obj = dataset_obj['perspectives'][ nav_dict['view'] ]
            view_obj['issues'].append(nav_dict['issue'])
        except Exception as e:
            return False

    coll.save(dataset_obj)
    
    return True


def create_hierarchy_info(info, columns):
    """ Creates information about hierarchy in csv file, info is information passed by user with
        names of columns creating hierarchy, columns is list with description of each column.
    """

    print 'columns = ', columns
    columns_idx = {}
    for i, column_descr in enumerate(columns):
        name = column_descr['key']
        columns_idx[name] = i
    
    #hierarchy_columns = [{'index': columns_idx[column_descr['name']], 'change_type': columns_idx[column_descr['change_type']} for column_descr in info['hierarchy']]
    hierarchy_columns = info['hierarchy'][:]
    for column_descr in hierarchy_columns:
        column_descr['index'] = columns_idx[column_descr['name']]
        del column_descr['name']
    summable_fields = [columns_idx[column['key']] for column in columns if column['type'] == 'number']
    
    hierarchy_info = {
        'columns': hierarchy_columns,
        'field_type_label': info['field_type_label'],
        'field_name_label': info['field_name_label'],
        'summable': summable_fields
    }

    print 'create_hierarchy_info --> ', hierarchy_info

    return hierarchy_info

def upload_data_file(db, coll_name, file_name, columns):
    """Uploads file file_name to database db to collection coll_name,
    columns describe columns inside that file
    
    Arguments:
    db -- database where data will be uploaded
    collection -- collection that will contain uploaded data
    file_name -- name of file containing data to upload
    columns -- description of columns in the file
    """
    coll = db[coll_name]
    coll.remove()

    keys_list = [column_descr['key'] for column_descr in columns]
    print 'keys_list = ', keys_list
    
    # TODO: parameterize delim
    csv_file = CsvFile(file_name, delim=';', quote='"')
    csv_data = CsvData(csv_file)
    row = csv_data.get_next_row(row_type='list')
    while row:
        print 'row = ', row
        db_row = {}
        for i, value in enumerate(row):
            db_row[ keys_list[i] ] = value
        print 'db_row = ', db_row
        coll.insert(db_row)

        row = csv_data.get_next_row(row_type='list')

    return False
