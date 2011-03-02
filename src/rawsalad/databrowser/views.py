# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json

# to be replaced with Denis' db interface
import pymongo 

def main_page( request ):
    #data is retrieved from db
    nav_collection= get_connection("rawsdoc00", "site_zz_nav", "localhost", 27017)
    data = get_main_page_data(nav_collection)
    template = loader.get_template( "main_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))

def choose_page( request, col_nr ):
    nav_collection= get_connection("rawsdoc00", "site_zz_nav", "localhost", 27017)
    data = get_choose_page_data( col_nr, nav_collection )
    template = loader.get_template( "dataset_info_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))

def other_page( request ):
    # shows chosen url for sites not ready yet,
    # only temporary solution to avoid getting 500 error
    path = request.path
    return HttpResponse( "<html><body>Wybrano adres:   " + path +
                         "</body></html>")

def get_main_page_data(collection):
    data_list= []
    for ffkey in collection.find({}, {
            "_id":0, 'pos':1, 'name':1, 'url':1, 'descr':1
            }).sort("pos"):
        ffval= dict(zip(
                ('pos', 'name', 'url', 'descr'),
                (ffkey['pos'], ffkey['name'], ffkey['url'], ffkey['descr'])
            ))
        data_list.append(ffval)

    data = { "data": data_list }
    return data

# Warning: hell
def get_choose_page_data( col_nr, collection ):
    print 'col_nr', col_nr

    long_descr_curr= collection.find_one({'pos':int(col_nr)}, {"_id":0, 'long_descr':1})
    long_descr= long_descr_curr['long_descr']

    data_list = []
    data_curr= collection.find({'pos':int(col_nr)}, {
            "_id":0, 'perspectives.pos':1, 'perspectives.func':1,
            'perspectives.name':1, 'perspectives.url':1, 'perspectives.descr':1
            }).sort('perspectives.pos')
    
    for ffkey in data_curr:
        for ffitem in ffkey['perspectives']:
            data_list.append(ffitem)

    data = { "data": data_list, "long_descr": long_descr }
    return data

def get_connection( dbname, collname, host, port ):
    db= pymongo.Connection(host, port)[dbname]
    return db[collname]
