# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json

# to be replaced with Denis' db interface
import pymongo 

def main_page( request ):
    #data is retrieved from db
    """
    nav_collection= get_connection("cecyf_rawsdoc00", "site_zz_nav", "guest:guestguest@85.10.210.123/cecyf_rawsdoc00", 27017)
    data = get_main_page_data(nav_collection)
    template = loader.get_template( "main_page.html" )
    context = Context( data )
    """
    data = get_main_page_data_nodb()
    template = loader.get_template( "main_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))

def choose_page( request, col_nr ):
    """
    nav_collection= get_connection("cecyf_rawsdoc00", "site_zz_nav", "guest:guestguest@85.10.210.123/cecyf_rawsdoc00", 27017)
    data = get_choose_page_data( col_nr, nav_collection )
    template = loader.get_template( "choose_page.html" )
    context = Context( data )
    """
    data = get_choose_page_data_nodb()
    template = loader.get_template( "choose_page.html" )
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
    db= pymongo.Connection("guest:guestguest@85.10.210.123/cecyf_rawsdoc00", port)[dbname]
    return db[collname]

def get_main_page_data_nodb():
    # to delete when data is in db
    budget_data = { "pos": 1, "name": "Budżet centralny", "descr": "To jest kolekcja budżetu centralnego, który stanowi\
                   zaledwie jedną trzecią finansów pulicznych.", "url": "/choose/col/1/" }
    fun_data = { "pos": 2, "name": "Fundusze celowe", "descr": "To jest kolekcja budżetu centralnego, który stanowi\
                zaledwie jedną trzecią finansów pulicznych.", "url": "/choose/fundusze_celowe/col/2/" }
    wl_data = { "pos": 3, "name": "Wybory lokalne", "descr": "To jest kolekcja budżetu centralnego, który stanowi\
               zaledwie jedną trzecią finansów pulicznych.", "url": "/choose/wybory_lokalne/col/3/" }
    data_list = [budget_data, fun_data, wl_data]
    data = { "data": data_list }
    return data

def get_choose_page_data_nodb():
    # to delete when data is in db
    task_budget = { "pos": 1, "name": "Budżet zadaniowy", "descr": "Budżet zadaniowy dzieli państwo na dwadzieścia dwie funkcje."}
    ks_budget = { "pos": 2, "name": "Budżet księgowy", "descr": "Budżet księgowy dzieli państwo na dwadzieścia dwie funkcje."}
    inst_budget = { "pos": 3, "name": "Budżet instytucjonalny", "descr": "Budżet instytucjonalny dzieli państwo na dwadzieścia dwie funkcje."}
    structures = [ task_budget, ks_budget, inst_budget ]
    wyn = { "pos": 1, "name": "Wynagrodzenia", "descr": "Przegląd środków budżetowych przeznaczonych na wynagrodzenia."}
    sr = { "pos": 1, "name": "Środki ruchome", "descr": "Przegląd środków ruchomych i stałych w budżecie państwa."}
    stories = [ wyn, sr ]
    other_collections = [ { "pos": 1, "name": "Fundusze celowe" },
                          { "pos": 2, "name": "Wybory samorządowe" },
                          { "pos": 3, "name": "Meterologia" } ]
    full_descr = "Budżet państwa jest najwyższej rangi planem finansowym polityki państwa oraz narzędziem polityki społecznej, uwzględniającym planowane dochody i wydatki państwa na następny rok budżetowy. Jako dochody uwzględnia się m.in.: wpływy z podatków pośrednich i bezpośrednich, dochody niepodatkowe (np. cła), dochody z prywatyzacji oraz dochody zagraniczne. Mianem wydatków określa się m.in. koszty dotacji, obsługi długu publicznego, obsługi strefy budżetowej, rozliczeń z bankami, subwencji dla gmin oraz rezerw ogólnych. Termin „budżet” pochodzi z łacińskiego bulga, oznaczającego skórzany mieszek przeznaczony do zbierania dochodów. Słowo to przyjęło się następnie w wielu językach (ang. budget, starofr. bougette, fr. la budget]. Dla historycznego rozwoju instytucji budżetu znaczenie miało kilka zdarzeń, które rozstrzygnęły o jej współczesnym kształcie, wśród których - poza oddzieleniem majątku publicznego od majątku królewskiego - wymienić należy rozwijanie stosunków towarowo-pieniężnych, parlamentaryzmu, funkcji socjalnych i gospodarczych państwa, rozwój międzynarodowych stosunków gospodarczych i finansowych oraz procesy integracyjne zachodzące we współczesnym świecie."
    data = { "name": "Budżet centralny", "full_descr": full_descr, "other_collections": other_collections,
             "all_pers": 5, "sys_pers": 3, "zag_pers": 2, "structures": structures, "stories": stories }
    return data