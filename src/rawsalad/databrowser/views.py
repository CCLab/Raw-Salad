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
        full_descr = "Budżet państwa jest najwyższej rangi planem finansowym polityki państwa oraz narzędziem polityki społecznej, uwzględniającym planowane dochody i wydatki państwa na następny rok budżetowy. Jako dochody uwzględnia się m.in.: wpływy z podatków pośrednich i bezpośrednich, dochody niepodatkowe (np. cła), dochody z prywatyzacji oraz dochody zagraniczne. Mianem wydatków określa się m.in. koszty dotacji, obsługi długu publicznego, obsługi strefy budżetowej, rozliczeń z bankami, subwencji dla gmin oraz rezerw ogólnych.<br />Termin „budżet” pochodzi z łacińskiego bulga, oznaczającego skórzany mieszek przeznaczony do zbierania dochodów. Słowo to przyjęło się następnie w wielu językach (ang. budget, starofr. bougette, fr. la budget]. Dla historycznego rozwoju instytucji budżetu znaczenie miało kilka zdarzeń, które rozstrzygnęły o jej współczesnym kształcie, wśród których - poza oddzieleniem majątku publicznego od majątku królewskiego - wymienić należy rozwijanie stosunków towarowo-pieniężnych, parlamentaryzmu, funkcji socjalnych i gospodarczych państwa, rozwój międzynarodowych stosunków gospodarczych i finansowych oraz procesy integracyjne zachodzące we współczesnym świecie."
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
        
def get_browse_page_data_nodb():
    # to delete when data is in db
    perspective = {
        "name": "Budżet zadaniowy",
        "columns": [
                    { "key": 'type', "label": "Typ", },
                    { "key": 'name', "label": "Nazwa", "processable": True, "type": 'string' },
                    { "key": 'y2010', "label": "2010", "processable": True, "type": 'number', "checkable": True },
                    { "key": 'y2011', "label": "2011", "processable": True, "type": 'number', "checkable": True }
                 ]
    }
    rows =  [
                { "id": 1, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 1", "name": "Zarządzanie państwem", "y2010": 192067, "y2011": 955848 },
                { "id": 2, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 2", "name": "Bezpieczeństwo wewnętrzne i porządek publiczny", "y2010": 837689, "y2011": 101529 },
                { "id": 3, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 3", "name": "Edukacja, wychowanie i opieka", "y2010": 925878, "y2011": 154068 },
                { "id": 4, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 4", "name": "Zarządzanie finansami państwa", "y2010": 222471, "y2011": 990150 },
                { "id": 5, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 5", "name": "Ochrona praw i interesów skarbu państwa", "y2010": 273210, "y2011": 782615 },
                { "id": 6, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 6", "name": "Polityka gospodarcza kraju", "y2010": 841071, "y2011": 380197 },
                { "id": 7, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 7", "name": "Gospodarka przestrzenna, budownictwo i mieszkalnictwo", "y2010": 643267, "y2011": 148055 },
                { "id": 8, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 8", "name": "Kultura fizyczna i sport", "y2010": 441874, "y2011": 237478 },
                { "id": 9, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 9", "name": "Kultura i dziedzictwo narodowe", "y2010": 940369, "y2011": 493538 },
                { "id": 10, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 10", "name": "Nauka polska", "y2010": 572872, "y2011": 828126 },
                { "id": 11, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 11", "name": "Bezpieczeństwo zewnętrzne i nienaruszalność granic", "y2010": 278970, "y2011": 886087 },
                { "id": 12, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 12", "name": "Środowisko", "y2010": 281331, "y2011": 561248 },
                { "id": 13, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 13", "name": "Zabezpieczenie społeczne i wspieranie rodziny", "y2010": 830991, "y2011": 806957 },    
                { "id": 14, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 14", "name": "Rynek pracy", "y2010": 270003, "y2011": 726244 },
                { "id": 15, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 15", "name": "Polityka zagraniczna", "y2010": 542305, "y2011": 854166 },
                { "id": 16, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 16", "name": "Sprawy obywatelskie", "y2010": 250917, "y2011": 740607 },    
                { "id": 17, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 17", "name": "Równomierny rozwój kraju", "y2010": 477775, "y2011": 782496 }, 
                { "id": 18, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 18", "name": "Sprawiedliwość", "y2010": 153669, "y2011": 983750 },
                { "id": 19, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 19", "name": "Infrastruktura transportowa", "y2010": 402486, "y2011": 296448 }, 
                { "id": 20, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 20", "name": "Zdrowie", "y2010": 109632, "y2011": 942002 },
                { "id": 21, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 21", "name": "Polityka rolna i rybacka", "y2010": 591247, "y2011": 430414 },
                { "id": 22, "level": 'a', "parent": None, "leaf": False, "type": "Funkcja 22", "name": "Planowanie strategiczne oraz obsługa administracyjna i techniczna", "y2010": 544098, "y2011": 718583 },
                { "id": 101, "level": 'b', "parent": 1, "leaf": False, "type": "Zadanie 1.1", "name": "Zarządzanie państwem", "y2010": 192067, "y2011": 955848 },
                { "id": 102, "level": 'b', "parent": 1, "leaf": False, "type": "Zadanie 1.2", "name": "Bezpieczeństwo wewnętrzne i porządek publiczny", "y2010": 837689, "y2011": 101529 },
                { "id": 103, "level": 'b', "parent": 1, "leaf": False, "type": "Zadanie 1.3", "name": "Edukacja, wychowanie i opieka", "y2010": 925878, "y2011": 154068 },
                { "id": 10101, "level": 'c', "parent": 101, "leaf": True, "type": "Podzadanie 1.1.1", "name": "Zarządzanie państwem", "y2010": 192067, "y2011": 955848 },
                { "id": 10102, "level": 'c', "parent": 101, "leaf": True, "type": "Podzadanie 1.1.2", "name": "Bezpieczeństwo wewnętrzne i porządek publiczny", "y2010": 837689, "y2011": 101529 },
                { "id": 10103, "level": 'c', "parent": 101, "leaf": True, "type": "Podzadanie 1.1.3", "name": "Edukacja, wychowanie i opieka", "y2010": 925878, "y2011": 154068 }        
            ]
    data = { "perspective": perspective, "rows": rows }
    return data
