from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.utils import simplejson as json

import psycopg2
import psycopg2.extras

import pymongo



def main_page( request ):
    return render_to_response( "databrowser.html" )

def first_table( request ):
    data = get_data_i()
    return HttpResponse( json.dumps( data ));

def second_table( request ):
    data = get_data_ii()
    return HttpResponse( json.dumps( data ));


def get_data_i():
    mongo_collect= pymongo.Connection("localhost", 27017)['rawsdoc00']['dd_budg2011_in_tmp0']
    rows= mongo_collect.find()
    out= []
    for row in rows:
        out.append(row)
    return out

    # extract logic
    # due to the collection structure gives a totally identical result to given above
    #
    #for row in rows:
    #    dict_id= {'dysponent':row['_id']['dysponent'],'czesc':row['_id']['czesc']}
    #    dictval= {'grand_nation':row['value']['grand_nation'],'grand_eu':row['value']['grand_eu'],'grand_total':row['value']['grand_total']}
    #    dictrow= {'_id':dict_id, 'value':dictval}
    #    out.append(dictrow)



def get_data_ii():
#postgres select + group by
    mongo_collect= pymongo.Connection("localhost", 27017)['rawsdoc00']['dd_budg2011_go']
    rows= mongo_collect.find({'node': 0, 'level':'c'})
    out= []
    for row in rows:
        dict_id= {'parent':row['parent'],'idef':row['idef'],'name':row['name'],'czesc':row['czesc']}
        dictval= {'v_eu':row['v_eu'],'v_nation':row['v_nation'],'v_eu':row['v_eu']} # 3 keys here - why only 2 are shown
        dictrow= {'_id':dict_id, 'value':dictval}
        out.append(dictrow)

    return out
