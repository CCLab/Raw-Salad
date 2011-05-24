# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json
# DK
import rawsdbapi as rawdb


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
    context = Context( get_meta_data() )
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


def download_data( request ):
    json = request.POST['sheet']
    print json
    return HttpResponse( json, mimetype='text/csv' )


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
