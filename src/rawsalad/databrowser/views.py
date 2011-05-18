# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson as json

# should be removed after data is imported from db
from data import new_rows
from data import perspective
#import rawsdbapi

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
    # getting data from db
    return_data = []
    for row in new_rows:
        if row["parent"] == par_id:
            return_data.append(row)
#    parent_data_query= { 'parent': par_id }
#    return_data= rawsdbapi.extract_docs(col_nr, per_nr, parent_data_query)

    json_data = json.dumps( return_data )

    return HttpResponse(json_data)
    
def get_init_data( data ):
    col_nr = data["col_nr"]
    per_nr = data["per_nr"]
    
    return_data = {}
    return_data["perspective"] = perspective
    return_data["rows"] = []
    for row in new_rows:
        if row["level"] == "a":
            return_data["rows"].append(row)
            
#    return_data["perspective"]= rawsdbapi.get_metadata(col_nr, per_nr)
#    initial_data_query= { 'level': 'a' }
#    return_data["rows"]= rawsdbapi.extract_docs(col_nr, per_nr, initial_data_query)

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
    return { 
              'collections': [
                    {
                        'name': 'Budżet centralny',
                        'description': 'Ustawa budżetowa w kilku odsłonach'
                    },
                    {
                        'name': 'Budżet środków europejskich',
                        'description': 'Udział środków europejskich w budżecie centralnym Polski'
                    },
                    {
                        'name': 'Fundusze celowe i agencje narodowe',
                        'description': 'Części kosztowe budżetów wszystkich funduszy celowych i agencji narodowych'
                    },
                    {
                        'name': 'Narodowy Fundusz Zdrowia',
                        'description': 'Budżet Narodowego Funduszu Zdrowia z rozbiciem na ośrodki wojewódzkie'
                    },
                    {
                        'name': 'Krajowy Fundusz Drogowy',
                        'description': 'Dane finansowe Krajowego Funduszu Drogowego'
                    }                                        
                ]
            }
            
            
def get_perspectives( col_nr ):

    if col_nr == '0':
        return {
            'collection': {
                'name': 'Budżet centralny',
                'number': 1
                },
            'perspectives': [
                {
                    'name': 'Budżet tradycyjny',
                    'description': 'Ustawa budżetowa as such',
                    'issue': [ 2011 ]
                    },
                {
                    'name': 'Budżet zadaniowy',
                    'description': 'Dwadzieścia dwie funkcje państwa',
                    'issue': [ 2011, 2012 ]
                    },
                {
                    'name': 'Budżet instytucjonalny',
                    'description': 'Wszyscy dysponenci ustawy budżetowej',
                    'issue': [ 2011, 2012 ]
                    }
                ]
            }
    elif col_nr == '1':
        return {
            'collection': {
                'name': 'Środki europejskie',
                'number': 2
                },
            'perspectives': [
                {
                    'name': 'Budżet środków europejskich',
                    'description': 'Dane dotyczące środków europejskich na szczeblu centralnym',
                    'issue': [ 2011 ]
                    },
                {
                    'name': 'Środki europejskie a ustawa budżetowa ',
                    'description': 'Przegląd relacji między środkami europejskimi a ustawą budżetową',
                    'issue': [ 2011 ]
                    }
                ]
            }    
    elif col_nr == '2':
        return {
            'collection': {
                'name': 'Fundusze celowe i agencje',
                'number': 3
                },
            'perspectives': [
                {
                    'name': 'Dane budżetowe w układzie zadaniowym',
                    'description': 'Z podziałem na funkcje, zadania i podzadania',
                    'issue': [ 2011 ]
                    },
                {
                    'name': 'Dane budżetowe w układzie tradycyjnym',
                    'description': 'Odpowiadające klasycznemu układowi budżetu państwa',
                    'issue': [ 2011 ]
                    }
                ]
            }
    elif col_nr == '3':
        return {
            'collection': {
                'name': 'Narodowy Fundusz Zdrowia',
                'number': 4
                },
            'perspectives': [
                {
                    'name': 'Dane zagregowane',
                    'description': 'Dane szczebla centralnego',
                    'issue': [ 2011 ]
                    },
                {
                    'name': 'Dane ośrodków regionalnych',
                    'description': 'Dane budżetowe ośrodków regionalnych NFZ',
                    'issue': [ 2011 ]
                    }
                ]
            }
    else:
        return {
            'collection': {
                'name': 'Krajowy Fundusz Drogowy',
                'number': 5
                },
            'perspectives': [
                {
                    'name': 'Dane zagregowane',
                    'description': 'Ogólne dane o wydatkach KFD',
                    'issue': [ 2011 ]
                    }
                ]
            }
        
    
    
    
    
    
    
    
    
    
