# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json
from django.core.mail import send_mail

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

    result= { }
    total_rec= 0

    db= rsdb.DBconnect('mongodb').dbconnect

    # 1st PASS
    tl1= time() # starting to search
    result_1= do_search(scope_list, regx, db)
    total_rec += result_1['stat']['records_found']
    tlap1= time()-tl1 # 1st pass finished
    result_1['stat'].update( { "search_time": "%0.6f" % tlap1 } )
    result['strict']= result_1

    # 2nd PASS
    second_pass_list= []
    if not strict: # second pass makes sense
        second_pass_list= usrqry.split(' ')

        result_2= { 'stat': { 'records_found': 0 }, 'result': [] } # blank dict for 2nd pass
        if len(second_pass_list) > 0:
            tl2= time() # starting to search

            for wrd in second_pass_list:
                lookup= build_regexp(wrd, True) # we look for separate words using strict
                regx= re.compile(lookup, re.IGNORECASE)
                result_2_curr= do_search(scope_list, regx, db)

                if result_2_curr['stat']['records_found'] > 0:
                    result_2['result'].append( result_2_curr['result'] )
                    result_2['stat']['records_found'] += result_2_curr['stat']['records_found']

                total_rec += result_2_curr['stat']['records_found']
                tlap2= time()-tl2 # 2nd pass finished
                result_2['stat'].update( { "search_time": "%0.6f" % tlap2 } )

            result['loose']= result_2

    tlap= time()-tl1
    result.update( {
        "search_time_total": "%0.6f" % tlap,
        'records_found_total': total_rec
        } )

    return HttpResponse( json.dumps( result ))

def string2list( in_str ):
    """ converts comma separated string to the list """
    out_list= []
    try:
        for elm in in_str.split(','):
            if '[' in elm:
                elm= elm.replace('[', '')
            if ']' in elm:
                elm= elm.replace(']', '')
            out_list.append( elm.strip().encode('utf-8') )
    except:
        pass

    return out_list

def build_idef_regexp( curr_idef ):
    """ build regexp quering collection """
    level_num= curr_idef.count('-')
    if level_num > 0: # deeper than 'a'
        idef_srch= curr_idef.rsplit('-', 1)[0]
        lookup_idef= "^%s\-\d+$" % idef_srch
        curr_idef= idef_srch
        level= 1
        while level < level_num:
            idef_srch= curr_idef.rsplit('-', 1)[0]
            lookup_idef += "|^%s\-\d+$" % idef_srch
            curr_idef= idef_srch
            level += 1
        lookup_idef += "|^([A-Z]|\d)+$"
    else: # just query the highest level
        lookup_idef= "^([A-Z]|\d)+$"

    return lookup_idef

def build_query( idef_list ):
    lookup, i= "", 0
    for idef in idef_list:
        i += 1
        lookup_idef= build_idef_regexp( idef )

        lookup += "(%s)|" % lookup_idef
        if i == len(idef_list):
            lookup= lookup[:-1] # cutting the last symbol | in case it's the end of list

    if len(idef_list) == 1: # single idef
        lookup= lookup[1:-1] # cutting ( and )

    return lookup


# get initial_data + subtrees to searched nodes
def get_searched_data( request ):
    response_dict = {
        'dataset': int( request.POST.get( 'dataset', -1 ) ),
        'view': int( request.POST.get( 'view', -1 ) ),
        'issue': request.POST.get( 'issue', '' ).encode('utf-8'),
        'idef': string2list( request.POST.get( 'idef', '' ) ),
        'regexp': True
    }

    find_query= build_query( response_dict['idef'] )
    # regexpquery= re.compile(find_query, re.IGNORECASE)

    db= rsdb.DBconnect("mongodb").dbconnect
    coll= rsdb.Collection(query= { 'idef': { '$regex': find_query} })

    return_data = {}
    return_data['rows']= coll.get_data(
        db, response_dict['dataset'], response_dict['view'], response_dict['issue']
        )
    return_data['perspective']= coll.metadata_complete

    if 'query' in return_data['perspective']: # not json serializable
        try:
            sr= json.dumps( return_data['perspective']['query'] )
        except: # not json serializable!
            if 'idef' in return_data['perspective']['query']:
                return_data['perspective']['query']['idef']= find_query # re-write it with plain regexp
        del return_data['perspective']['query']

    return HttpResponse( json.dumps(return_data) )

# store front-end state as a permalink in mongo
@csrf_exempt
def store_state( request ):
    data = request.POST.get( 'state', '' )
    #
    # store in mongo, create uniq idef and send it back to front-end
    #

    return HttpResponse( '1000' ) #replace '1000' with uniq idef

# init application prepared to handle restore data
def init_restore( request, idef ):
    template = loader.get_template( "restore.html" )
    context = Context({
        'meta': get_ms_nav(),
        'idef': idef
    })
    return HttpResponse( template.render( context ))


#restore front-end state from mongo
def restore_state( request ):
    idef = request.GET.get( 'idef', '-1' )
    data = 'get_me_from_mongo_my_name_is_' + idef

    return HttpResponse( data )


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
    template = loader.get_template( "test.html" )
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
def feedback_email( request ):
    from_email = request.POST.get( 'email', 'NO EMAIL PROVIDED' )
    message = request.POST.get( 'message', 'MESSAGE LEFT EMPTY' )

    send_mail( 'Raw Salad Feedback',
                message,
                from_email,
                ['ktrzewiczek@centrumcyfrowe.pl'] )

    return HttpResponse( 'Email sent' )


@csrf_exempt
def download_data( request ):
    response = HttpResponse()
    files = request.POST.get( 'csv_string' ).split( '--file--' )[:-1]

    # send one sheet as CSV and collection of sheets as ZIP
    if len( files ) == 1:
        f = files[0]
        response['Content-Type'] = 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=data.csv'

        if '.csv' in f:
            response.write( open( 'site_media/csv/' + f ).read() )
        else:
            data = f.split( '|' )[:-1]

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
