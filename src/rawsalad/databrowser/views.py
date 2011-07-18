# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json

import rsdbapi as rsdb
import csv, codecs, cStringIO
import re
from time import time

from StringIO import StringIO
from zipfile import ZipFile


# to be removed soon
def choose_collection( data ):
    # getting data from db using col_nr
    return_data = get_perspectives( data['col_nr'] )
    json_data = json.dumps( return_data )
    return HttpResponse( json_data )

# get the basic, top-level view of some issue
def get_init_data( data ):
    db= rsdb.DBconnect("mongodb").dbconnect
    coll= rsdb.Collection(query= { 'level': 'a' })

    return_data = {}
    return_data['rows']= coll.get_data(
        db, data['dataset'], data['perspective'], data['issue']
        )
    return_data['perspective']= coll.metadata_complete

    json_data = json.dumps( return_data )

    return HttpResponse( json_data )

# get the subtree of the next level
def get_node( data ):
    db= rsdb.DBconnect("mongodb").dbconnect
    coll= rsdb.Collection(query= { 'parent': data['parent'] })

    return_data= coll.get_data(
        db, data['dataset'], data['perspective'], data['issue']
        )

    json_data = json.dumps( return_data )

    return HttpResponse(json_data)

def build_regexp(searchline, strictsearch):
    """ construct regexp for search """
    # building regexp for search
    if strictsearch:
        # ver 0.0
        # searchline= "^%(lookupstr)s\s|\s%(lookupstr)s\s|\s%(lookupstr)s$" % { "lookupstr": searchline }
        # ver 0.1
        searchline= "^%(lookupstr)s([^a-z][^A-Z][^0-9]|\s)|([^a-z][^A-Z][^0-9]|\s)%(lookupstr)s([^a-z][^A-Z][^0-9]|\s)|([^a-z][^A-Z][^0-9]|\s)%(lookupstr)s$" % { "lookupstr": searchline }
        
    return searchline

def do_search(scope_list, regx, dbconn):
    """
    TO-DO:
    - search with automatic substitution of specific polish letters
      (lowercase & uppercase): user can enter 'lodz', but the search
      should find 'Łódż'
    - search with flexible processing of prefixes and suffixes
      (see str.endswith and startswith)
    - search in 'info' keys
    """
    ns_list= [] # list of results
    stat_dict= { "errors": [] }
    found_num= 0 # number of records found
    exclude_fields= ['idef', 'idef_sort', 'parent', 'parent_sort', 'level'] # not all fields are searchable
    
    for sc in scope_list: # fill the list of collections
        sc_list= sc.split('-')
        dataset, idef, issue= int(sc_list[0]), int(sc_list[1]), str(sc_list[2])
        coll= rsdb.Collection(fields=["perspective", "ns", "columns"])
        metadata= coll.get_complete_metadata(dataset, idef, issue, dbconn)
        if metadata is None:
            stat_dict['errors'].append('collection not found %s' % sc)
        else:
            curr_coll_dict= {
                'perspective': metadata['perspective'],
                'dataset': dataset,
                'view': idef,
                'issue': issue,
                'data': []
                }


            coll.set_fields(None) # for search we need all fields, except for exclude_fields
            for fld in metadata['columns']:
                if 'processable' in fld:
                    check_str= fld['type'] == 'string'
                    check_excl= fld['key'] not in exclude_fields
                    if fld['processable'] and check_str and check_excl:
                        search_query= { fld['key']: regx }
                        coll.set_query(search_query)
                        found= coll.get_data(dbconn, dataset, idef, issue)
                        if len(found) > 0:
                            for found_elt in found:
                                curr_coll_dict['data'].append({
                                    'key': fld['key'],
                                    'text': found_elt[str(fld['key'])],
                                    'idef': found_elt['idef'],
                                    'parent': found_elt['parent']
                                    })
                                found_num += 1
            if len(curr_coll_dict['data']) > 0:
                ns_list.append(curr_coll_dict)

    stat_dict.update( { 'records_found': found_num } )

    return { 'stat': stat_dict, 'result': ns_list }

def search_data( request ):
    """
    search engine enter point
    """
    usrqry = request.GET.get( 'query', '' )
    scope = request.GET.get( 'scope', '' )
    strict = request.GET.get( 'strict', 'false' )
    # converting scope and strict to objects
    scope_list= scope.split(',')
    if strict == 'false':
        strict= False
    else:
        strict= True
    # cleaning user query
    usrqry= usrqry.strip()
    usrqry= re.sub('\s+', ' ', usrqry) # cleaning multiple spaces

    lookup= build_regexp(usrqry, strict)
    regx= re.compile(lookup, re.IGNORECASE)

    db= rsdb.DBconnect('mongodb').dbconnect

    # 1st PASS
    tl= time() # starting to search
    result= do_search(scope_list, regx, db)
    tlap= time()-tl # 1st pass finished

    # 2nd PASS
    second_pass_list= []
    if result['stat']['records_found'] == 0:
        if not strict: # second pass makes sense
            second_pass_list= usrqry.split(' ')
    if len(second_pass_list) > 0:
        for wrd in second_pass_list:
            lookup= build_regexp(wrd, True) # we look for separate words using strict
            regx= re.compile(lookup, re.IGNORECASE)
            result_second_pass= do_search(scope_list, regx, db)

            if result_second_pass['stat']['records_found'] > 0:
                result['result'].append( result_second_pass['result'] )
                result['stat']['records_found'] += result_second_pass['stat']['records_found']

            tlap= time()-tl # 2nd pass finished

    result['stat'].update( { "search_time": "%0.6f" % tlap } )

    print result

    return HttpResponse( json.dumps( result ))
    
# get initial_data + subtrees to searched nodes
def get_searched_data( request ):
    response_dict = {
        'dataset': request.GET.get( 'dataset', -1 ),
        'view': request.GET.get( 'view', -1 ),
        'issue': request.GET.get( 'issue', -1 )
    }
    return HttpResponse( json.dumps(response_dict) )
    

# list of possible ajax calls
func_dict = {
    # get a list of perspectives after choosing a certain collection
    "choose_collection": choose_collection,

    # get data from DB when the first time a perspective is chosen
    "get_init_data": get_init_data,

    # get a sub-level data from DB
    "get_node": get_node,

    # to be implemented
    }



def get_page( data ):
    template = loader.get_template( "app.html" )
#     context = Context( tmp_solution_for_metadata() )
    context = Context( get_ms_nav() )
    return HttpResponse( template.render( context ))


def app_page( request ):
    data = request.GET
    if data == {}:
        return get_page( request )
    else:
        function_id = data['action']
        return func_dict[function_id]( data )

def redirect( request ):
    return HttpResponseRedirect('/app')

@csrf_exempt
def download_data( request ):
    response = HttpResponse()
    files = request.POST.get( 'sheets' ).split( '--file--' )[:-1]

    # send one sheet as CSV and collection of sheets as ZIP
    if len( files ) == 1:
        data = files[0].split( '|' )[:-1]
        response['Content-Type'] = 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=data.csv'

        writer = UnicodeWriter( response )
        for row in data:
            writer.writerow( row.split(';') )
    else:
        in_memory = StringIO()
        zip = ZipFile( in_memory, 'a' )

        for i, f in enumerate( files ):
            if '.csv' in f:
                csv_string = open( 'site_media/csv/' + f ).read()
            else:
                csv_string = f.replace( '|', '\n' ).encode( 'utf-8' )

            zip.writestr( 'data-'+str(i)+'.csv', csv_string )

        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0

        zip.close()

        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = "attachment; filename=collected_data.zip"

        in_memory.seek( 0 )
        response.write( in_memory.read() )

    return response

def get_ms_nav():
    db= rsdb.DBconnect("mongodb").dbconnect
    nav_full= rsdb.Navtree().get_nav_full(db)
    out= { 'meta_data': json.dumps( nav_full ) }
    return out

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter=';', **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
