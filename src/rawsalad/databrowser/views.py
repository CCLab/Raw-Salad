# -*- coding: utf-8 -*-

#from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json

import rawsdbapi as rawdb
import csv, codecs, cStringIO


# to be removed soon
def choose_collection( data ):
    col_nr = data["col_nr"]
    # getting data from db using col_nr
    return_data = get_perspectives( col_nr )
    json_data = json.dumps( return_data )
    return HttpResponse( json_data )


# get the basic, top-level view of some issue
def get_init_data( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]

    return_data = {}
    return_data['perspective']= rawdb.get_metadata(col_nr, per_nr)
    initial_data_query= { 'level': 'a' }
    return_data["rows"]= rawdb.extract_docs(col_nr, per_nr, initial_data_query)

    json_data = json.dumps( return_data )

    return HttpResponse( json_data )


# get the subtree of the next level
def get_node( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    par_id = data["par_id"]
    add_columns = data["add_columns"]

    # getting data from db
    return_data = []
    parent_data_query= { 'parent': par_id }
    return_data= rawdb.extract_docs(col_nr, per_nr, parent_data_query)

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
    context = Context( tmp_solution_for_metadata() )
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


# is that ever used?!
def get_meta_data():
    # DK
    datasets= {'collections':None}
    # return only the highest level
    datasets['collections']= rawdb.extract_nav(keys_aux={'perspectives':0})

    return datasets

# to be replaced with a single meta-data call!!
def get_perspectives( col_nr ):
    # DK
    dataset_coll= {}
    # dataset
    keys_dict={ 'name':1, 'idef':1 }
    query_dict={ 'idef':int(col_nr) }
    dataset_coll['collection']= rawdb.extract_nav(keys_dict, query_dict)[0]
    dataset_coll['collection']['number']= dataset_coll['collection'].pop('idef')
    # its perspectives
    keys_dict={ 'perspectives':1 }
    query_dict={ 'idef':int(col_nr) }
    persp_dict= rawdb.extract_nav(keys_dict, query_dict)[0]
    dataset_coll.update(persp_dict)

    return dataset_coll




def tmp_solution_for_metadata():
    return { meta_data: [
        {
            "idef": 0, 
            "long_description": None, 
            "name": "Budżet centralny", 
            "description": "Ustawa budżetowa w kilku odsłonach"
        }, 
        {
            "idef": 1, 
            "long_description": None, 
            "name": "Środki europejskie", 
            "description": "Udział środków europejskich w budżecie centralnym Polski"
        }, 
        {
            "idef": 2, 
            "long_description": None, 
            "name": "Fundusze celowe i agencje narodowe", 
            "description": "Części kosztowe budżetów wszystkich funduszy celowych i agencji narodowych"
        }, 
        {
            "idef": 3, 
            "long_description": None, 
            "name": "Narodowy Fundusz Zdrowia", 
            "description": "Budżet Narodowego Funduszu Zdrowia z rozbiciem na ośrodki wojewódzkie"
        }, 
        {
            "idef": 4, 
            "long_description": None, 
            "name": "Krajowy Fundusz Drogowy", 
            "description": "Dane finansowe Krajowego Funduszu Drogowego"
        }
    ]}


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
