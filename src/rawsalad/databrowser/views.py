# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json
# DK
import rawsdbapi

#import pymongo

def get_page( data ):
    template = loader.get_template( "app.html" )
    context = Context( get_meta_data() )
    return HttpResponse( template.render( context ))

def choose_collection( data ):
    col_nr = data["col_nr"]
    # getting data from db using col_nr
    return_data = get_perspectives( col_nr )
    json_data = json.dumps( return_data )
    return HttpResponse( json_data )
    
def choose_perspective( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    # getting data from db using col_nr and per_nr
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
def change_collection( data ):
    col_nr = data["col_nr"]
    # getting data from db using col_nr
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
def change_perspective( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    # getting data from db using col_nr and per_nr
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
def add_columns( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    columns_names = data["columns_names"]
    nodes = data["nodes"]
    # getting data from db
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
def find_data( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    search_type = data["type"]
    search_phrase = data["phrase"]
    # getting data from db
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
def get_node( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    par_id = data["par_id"]
    add_columns = data["add_columns"]

    # DK
    # getting data from db
    return_data = []
    parent_data_query= { 'parent': par_id }
    return_data= rawsdbapi.extract_docs(col_nr, per_nr, parent_data_query)

    json_data = json.dumps( return_data )

    return HttpResponse(json_data)
    
def get_init_data( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    
    # DK
    return_data = {}            
    return_data['perspective']= rawsdbapi.get_metadata(col_nr, per_nr)
    initial_data_query= { 'level': 'a' }
    return_data["rows"]= rawsdbapi.extract_docs(col_nr, per_nr, initial_data_query)

    json_data = json.dumps( return_data )
    
    return HttpResponse( json_data )

func_dict = {
              # get a list of perspectives after choosing a certain collection
              "choose_collection": choose_collection,

              # get data from DB when the first time a perspective is chosen
              "get_init_data": get_init_data,

              # get a sub-level data from DB
              "get_node": get_node,
              
              "add_columns": add_columns,
              "find_data": find_data,
            }
            
def app_page( request ):
    data = request.GET
    if data == {}:
        return get_page( request )
    else:
        function_id = data["action"]
        return func_dict[function_id]( data )

def redirect( request ):
    return HttpResponseRedirect('/app')
    
    
    
def get_meta_data():
    # DK
    datasets= {'collections':None}
    # return only the highest level
    datasets['collections']= rawsdbapi.extract_nav(keys_aux={'perspectives':0})

    return datasets
            
            
def get_perspectives( col_nr ):
    # DK
    dataset_coll= {}
    # dataset
    keys_dict={ 'name':1, 'idef':1 }
    query_dict={ 'idef':int(col_nr) }
    dataset_coll['collection']= rawsdbapi.extract_nav(keys_dict, query_dict)[0]
    dataset_coll['collection']['number']= dataset_coll['collection'].pop('idef')
    # its perspectives
    keys_dict={ 'perspectives':1 }
    query_dict={ 'idef':int(col_nr) }
    persp_dict= rawsdbapi.extract_nav(keys_dict, query_dict)[0]
    dataset_coll.update(persp_dict)

    return dataset_coll
