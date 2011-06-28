# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json

import rsdbapi as rsdb
import csv, codecs, cStringIO


# to be removed soon
def choose_collection( data ):
    # getting data from db using col_nr
    return_data = get_perspectives( data["col_nr"] )
    json_data = json.dumps( return_data )
    return HttpResponse( json_data )

# get the basic, top-level view of some issue
def get_init_data( data ):
    db= rsdb.DBconnect("mongodb").dbconnect
    coll= rsdb.Collection(query= { 'level': 'a' })

    return_data = {}
    return_data["rows"]= coll.get_data(
        db, data["dataset"], data["perspective"], data["issue"]
        )
    return_data["perspective"]= coll.metadata_complete

    json_data = json.dumps( return_data )

    return HttpResponse( json_data )

# get the subtree of the next level
def get_node( data ):
    db= rsdb.DBconnect("mongodb").dbconnect
    coll= rsdb.Collection(query= { 'parent': data["parent"] })

    return_data= coll.get_data(
        db, data["dataset"], data["perspective"], data["issue"]
        )

    json_data = json.dumps( return_data )

    return HttpResponse(json_data)


# add columns - do we really need that?!
def add_columns( data ):
    pass


# search engine enter point
def find_data( data ):
    pass



# list of possible ajax calls
func_dict = {
    # get a list of perspectives after choosing a certain collection
    "choose_collection": choose_collection,

    # get data from DB when the first time a perspective is chosen
    "get_init_data": get_init_data,

    # get a sub-level data from DB
    "get_node": get_node,

    # to be implemented
    "add_columns": add_columns,
    "find_data": find_data,
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
        function_id = data["action"]
        return func_dict[function_id]( data )

def redirect( request ):
    return HttpResponseRedirect('/app')

@csrf_exempt
def download_data( request ):
    data = request.POST.get( 'sheet' ).split( '|' )
    response = HttpResponse( mimetype='text/csv' )
    response['Content-Disposition'] = 'attachment; filename=data.csv'

    writer = UnicodeWriter( response )
    for row in data:
        writer.writerow( row.split(';') )

    return response

def get_ms_nav():
    db= rsdb.DBconnect("mongodb").dbconnect
    nav_full= rsdb.Navigator().get_nav_full(db)
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
