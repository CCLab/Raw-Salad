# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json

import pymongo

def get_page( data ):
    template = loader.get_template( "index.html" )
    context = Context( )
    return HttpResponse( template.render( context ))

def choose_collection( data ):
    col_nr = data["col_nr"]
    # getting data from db using col_nr
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data
    
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
    # getting data from db
    return_data = {}
    json_data = json.dumps( return_data )
    return json_data

func_dict = {
              "choose_collection": choose_collection,
              "choose_perspective": choose_perspective,
              "change_collection": change_collection,
              "change_perspective": change_perspective,
              "add_columns": add_columns,
              "find_data": find_data,
              "get_node": get_node
            }
            
def app_page( request ):
    if request.method == "GET":
        return get_page( request )
    else:
        #request.method == "POST":
        function_id = request.POST( "action" )
        data = request.POST( "data" )
        return func_dict( func_dict( function_id(data) ) )

def redirect( request ):
    return HttpResponseRedirect('/app')