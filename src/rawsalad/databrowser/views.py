# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json

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
    data = get_choose_page_data_nodb( col_nr )
    template = loader.get_template( "choose_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))


def browse_page( request ):
    template = loader.get_template( "browse_page.html" )
    context = Context( {} )
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
    #db= pymongo.Connection("guest:guestguest@85.10.210.123/cecyf_rawsdoc00", port)[dbname]
    return db[collname]

def get_main_page_data_nodb():
    # to delete when data is in db
    budget_data = { "pos": 1, "name": "Budżet centralny", "descr": "To jest kolekcja budżetu centralnego, który stanowi\
                   zaledwie jedną trzecią finansów pulicznych.", "url": "/choose/col/1/" }
    fun_data = { "pos": 2, "name": "Fundusze celowe", "descr": "To jest kolekcja funduszy celowych, które stanowią\
                zaledwie jedną trzecią finansów pulicznych.", "url": "/choose/col/2/" }
    wl_data = { "pos": 3, "name": "Wybory lokalne", "descr": "To jest kolekcja danych z wyborów samorządowych - do rad gmin,\
                powiatów i sejmików oraz wójtów i prezydentów miast.", "url": "/choose/col/3/" }
    data_list = [budget_data, fun_data, wl_data]
    data = { "data": data_list }
    return data

def get_choose_page_data_nodb( col_nr ):
    # to delete when data is in db
    if col_nr == "1":
        task_budget = { "pos": 1, "name": "Budżet zadaniowy", "descr": "Budżet zadaniowy dzieli państwo na dwadzieścia dwie funkcje."}
        ks_budget = { "pos": 2, "name": "Budżet księgowy", "descr": "Budżet księgowy dzieli państwo na dwadzieścia dwie funkcje."}
        inst_budget = { "pos": 3, "name": "Budżet instytucjonalny", "descr": "Budżet instytucjonalny dzieli państwo na dwadzieścia dwie funkcje."}
        structures = [ task_budget, ks_budget, inst_budget ]
        wyn = { "pos": 1, "name": "Wynagrodzenia", "descr": "Przegląd środków budżetowych przeznaczonych na wynagrodzenia."}
        sr = { "pos": 1, "name": "Środki ruchome", "descr": "Przegląd środków ruchomych i stałych w budżecie państwa."}
        stories = [ wyn, sr ]
        other_collections = [ { "pos": 1, "name": "Fundusze celowe i agencje" },
                              { "pos": 2, "name": "Wybory samorządowe" } ]
        full_descr = "Budżet państwa jest najwyższej rangi planem finansowym polityki państwa oraz narzędziem polityki społecznej, uwzględniającym planowane dochody i wydatki państwa na następny rok budżetowy. Jako dochody uwzględnia się m.in.: wpływy z podatków pośrednich i bezpośrednich, dochody niepodatkowe (np. cła), dochody z prywatyzacji oraz dochody zagraniczne. Mianem wydatków określa się m.in. koszty dotacji, obsługi długu publicznego, obsługi strefy budżetowej, rozliczeń z bankami, subwencji dla gmin oraz rezerw ogólnych. Termin „budżet” pochodzi z łacińskiego bulga, oznaczającego skórzany mieszek przeznaczony do zbierania dochodów. Słowo to przyjęło się następnie w wielu językach (ang. budget, starofr. bougette, fr. la budget]. Dla historycznego rozwoju instytucji budżetu znaczenie miało kilka zdarzeń, które rozstrzygnęły o jej współczesnym kształcie, wśród których - poza oddzieleniem majątku publicznego od majątku królewskiego - wymienić należy rozwijanie stosunków towarowo-pieniężnych, parlamentaryzmu, funkcji socjalnych i gospodarczych państwa, rozwój międzynarodowych stosunków gospodarczych i finansowych oraz procesy integracyjne zachodzące we współczesnym świecie."
        data = { "name": "Budżet centralny", "full_descr": full_descr, "other_collections": other_collections,
                 "all_pers": 5, "sys_pers": 3, "zag_pers": 2, "structures": structures, "stories": stories }
        return data
    elif col_nr == "2":
        rodz_fund = { "pos": 1, "name": "Rodzaje funduszy", "descr": "Podział na fundusze w zależności od wykonywanych zadań."}
        ps_fund = { "pos": 2, "name": "Fundusze państwowe i samorządowe", "descr": "Podział na fundusze realizujące zadania na poziomie państwa i samorządów."}
        structures = [ rodz_fund, ps_fund ]
        e_r = { "pos": 1, "name": "Emerytury i renty", "descr": "Przegląd środków przeznaczanych na renty i emerytury."}
        dot = { "pos": 2, "name": "Dotacje budżetowe", "descr": "Przegląd dotacji z budżetu przeznaczanych na fundusze."}
        zk = { "pos": 3, "name": "ZUS a KRUS", "descr": "Porównanie środków wpływających do ZUS-u i KRUS-u."}
        stories = [ e_r, dot, zk ]
        other_collections = [ { "pos": 1, "name": "Budżet centralny" },
                              { "pos": 2, "name": "Wybory samorządowe" } ]
        full_descr = "Fundusze celowe – fundusze stworzone do finansowania takich zadań należących do organów publicznych (państwowych lub samorządowych), które mogłyby być finansowane z budżetu, lecz z pewnych względów uznano, iż dla ich realizacji należy stworzyć odrębne budżety. Fundusze celowe charakteryzuje celowe przeznaczenie gromadzonych w nich dochodów. Są tworzone na podstawie odrębnych ustaw (ustawa powołuje konkretny fundusz). Przychody funduszy pochodzą z dochodów publicznych. Fundusze celowe dzielą się na państwowe lub samorządowe (odpowiednio: gminne, powiatowe lub wojewódzkie). Jako ważna cechę można także podać nieokreślony czas ich funkcjonowania, który jest jednak zazwyczaj dłuższy niż rok.(źródło Wikipedia)"
        data = { "name": "Fundusze celowe", "full_descr": full_descr, "other_collections": other_collections,
                 "all_pers": 5, "sys_pers": 2, "zag_pers": 3, "structures": structures, "stories": stories }
        return data
    elif col_nr == "3":
        wbp = { "pos": 1, "name": "Wybory wójtów, burmistrzów i prezydentów miast", "descr": "W wyborach na wójtów, burmistrzów i prezydentów miast część kandydatów zwyciężyła już w pierwszej turze."}
        sw = { "pos": 2, "name": "Sejmiki wojewódzkie", "descr": "W wyborach do sejmików wojewódzkich frekwencja wyniosła 47,26% uprawnionych do głosowania. Oddano 12,06% głosów nieważnych. Ważnych głosów oddano 12 721 376."}
        structures = [ wbp, sw ]
        wp = { "pos": 1, "name": "Wyniki wyborów według płci", "descr": "Wyniki wyborów według płci."}
        ww = { "pos": 2, "name": "Wyniki wyborów według wieku", "descr": "Wyniki wyborów według wieku."}
        stories = [ wp, ww ]
        other_collections = [ { "pos": 1, "name": "Budżet centralny" },
                              { "pos": 2, "name": "Fundusze celowe" } ]
        full_descr = "W wyborach na wójtów, burmistrzów i prezydentów miast część kandydatów zwyciężyła już w pierwszej turze. Największą przewagę nad konkurentami w I turze uzyskali kandydaci w gminach: Budzyń, Puńsk i Szczytna; w każdej z nich uzyskali oni ponad 95% głosów[3]. W miastach wojewódzkich w pierwszej turze wynik został rozstrzygnięty w Białymstoku, Gdańsku, Katowicach, Kielcach, Rzeszowie, Warszawie, we Wrocławiu i w Zielonej Górze, przy czym największą przewagę nad konkurentami w spośród tych miast uzyskał Rafał Dutkiewicz we Wrocławiu, uzyskując ponad 71% głosów[3] (spośród miast niebędących siedzibami województw najwyższy wynik zanotowano w Gdyni, gdzie Wojciech Szczurek wygrał uzyskując ponad 87% głosów[4]). Druga tura wyborów na prezydentów miast wojewódzkich potrzebna była w Krakowie (Jacek Majchrowski vs Stanisław Kracik), w Łodzi (Hanna Zdanowska vs Dariusz Joński, w Poznaniu (Ryszard Grobelny vs Grzegorz Ganowicz), w Olstynie (Czesław Małkowski vs Piotr Grzymowicz), w Bydgoszczy (Rafał Bruski vs Konstanty Dombrowicz), w Opolu (Ryszard Zembaczyński vs Tomasz Garbowski), w Szczecinie (Piotr Krzystek vs Arkadiusz Litwiński) i w Lublinie (Lech Sprawka vs Krzysztof Żuk)."
        data = { "name": "Fundusze celowe", "full_descr": full_descr, "other_collections": other_collections,
                 "all_pers": 4, "sys_pers": 2, "zag_pers": 2, "structures": structures, "stories": stories }
        return data
