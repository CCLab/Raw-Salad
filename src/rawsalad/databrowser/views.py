# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json

# to be replaced with Denis' db interface
import pymongo 

def main_page( request ):
    #data will be retrieved from db
    data = get_main_page_data()
    template = loader.get_template( "main_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))

def choose_page( request, col_nr ):
    data = get_choose_page_data( col_nr )
    template = loader.get_template( "dataset_info_page.html" )
    context = Context( data )
    return HttpResponse( template.render( context ))

def other_page( request ):
    # shows chosen url for sites not ready yet,
    # only temporary solution to avoid getting 500 error
    path = request.path
    return HttpResponse( "<html><body>Wybrano adres:   " + path +
                         "</body></html>")

def get_main_page_data():
    budget_data = { "pos": 1, "name": "Budżet centralny", "url": "choose/col/1/", "descr": "Budżet centralny to kolekcja przedstawiająca budżet panstwa z kilku kluczowych perspektyw" }
    polls_data = { "pos": 2, "name": "Wybory lokalne", "url": "choose/col/2/", "descr": "Kolekcja danych z wyborów samorządowych - do rad gmin, powiatów i sejmików oraz wójtów i prezydentów miast." }
    data_list = [ budget_data, polls_data ]
    data = { "data": data_list }
    return data

# Warning: hell
def get_choose_page_data( col_nr ):
    print 'col_nr', col_nr
    data_list = []
    long_descr = ""
    
    if col_nr == "1":
        task_budget = { "pos": 1, "func": "structure", "name": "Budżet zadaniowy", "url": "browser/col/1/view/1", "descr": "Budżet zadaniowy dzieli państwo na dwadzieścia dwie funkcje, w ramach których środki przydzielane są konkretnym instytucjom." }
        inst_budget = { "pos": 2, "func": "structure", "name": "Budżet instytucjonalny", "url": "browser/col/1/view/2", "descr": "To perspektywa na budżet pozwalająca na szybki przegląd instytucji odpowiedzialnych za realizację postanowień ustawy budżetowej." }
        trad_budget = { "pos": 3, "func": "structure", "name": "Budżet księgowy", "url": "browser/col/1/view/3", "descr": "Budżet księgowy to tradycyjna struktura budżetowa realizowana w chwili obecnej w ramach ustawy budżetowej." }
        wyn = { "pos": 4, "func": "story", "name": "Wynagrodzenia", "url": "snapshots/a1b1c1_d1b3c2_d1", "descr": "Wynagrodzenia" }
        sr_ruch = { "pos": 5, "func": "story", "name": "Środki ruchome", "url": "snapshots/a1b1c1_d1b3c4_d2", "descr": "Środki ruchome" }
        war_nm_p = { "pos": 6, "func": "story", "name": "Wartości niematerialne i prawne", "url": "snapshots/a1b3c1_d1b3c2_d1", "descr": "Wartości niematerialne i prawne" }
        sr_nr = { "pos": 7, "func": "story", "name": "Środki nieruchome", "url": "snapshots/a1b3c2_d1b3c4_d2", "descr": "Środki nieruchome" }

        long_descr = "<p><b>Budżet zadaniowy</b> (ang. <i>performance budget</i>) to metoda zarządzania finansami publicznymi, ukierunkowana na osiąganie większej skuteczności oraz efektywności i przejrzystości wydatkowania środków publicznych, polegająca na:</p><ol><li>opracowywaniu budżetu państwa w oparciu o cele budżetu zadaniowego, zgodne ze wskazaniami zawartymi w dokumentach strategicznych i programowych rządu, w ramach których to celów, umieszczane są - właściwe przedmiotowo tym celom - zadania, wraz z adekwatnymi miernikami informującymi o rezultatach/wynikach realizacji tych zadań - a także o rezultatach/wynikach realizacji ich części składowych (a zarazem - o stopniu osiągania celów budżetowych zadań w aspekcie skuteczności oraz efektywności),</li><li>monitorowaniu oraz ewaluacji poszczególnych zadań budżetu zadaniowego za pomocą mierników, dzięki czemu wytwarzane są informacje efektywnościowe (ang. <i>performance information</i>) służące podnoszeniu jakości alokacji w planowaniu budżetu w kolejnych latach/okresach planowania budżetowego,</li><li>praktycznym stosowaniu informacji efektywnościowych w procesie planowania budżetu przez rząd, a także wykorzystaniu ich podczas prac parlamentarnych nad uchwalaniem ustawy budżetowej (najczęściej jako tzw.: <i>performance-informed budgeting</i>)</li></ol>"
        
        data_list = [ task_budget, inst_budget, trad_budget, wyn, sr_ruch, war_nm_p, sr_nr]
        print "JESTEM"

        
    elif col_nr == "2":
        ww_b_pm = { "pos": 1, "func": "structure", "name": "Wybory wójtów, burmistrzów i prezydentów miast", "url": "browser/col/2/view/1", "descr": "W wyborach na wójtów, burmistrzów i prezydentów miast część kandydatów zwyciężyła już w pierwszej turze.", "long_descr": "<p>W wyborach na wójtów, burmistrzów i prezydentów miast część kandydatów zwyciężyła już w pierwszej turze. Największą przewagę nad konkurentami w I turze uzyskali kandydaci w gminach: Budzyń, Puńsk i Szczytna; w każdej z nich uzyskali oni ponad 95% głosów[3]. W miastach wojewódzkich w pierwszej turze wynik został rozstrzygnięty w Białymstoku, Gdańsku, Katowicach, Kielcach, Rzeszowie, Warszawie, we Wrocławiu i w Zielonej Górze, przy czym największą przewagę nad konkurentami w spośród tych miast uzyskał Rafał Dutkiewicz we Wrocławiu, uzyskując ponad 71% głosów[3] (spośród miast niebędących siedzibami województw najwyższy wynik zanotowano w Gdyni, gdzie Wojciech Szczurek wygrał uzyskując ponad 87% głosów[4]). Druga tura wyborów na prezydentów miast wojewódzkich potrzebna była w Krakowie (Jacek Majchrowski vs Stanisław Kracik), w Łodzi (Hanna Zdanowska vs Dariusz Joński, w Poznaniu (Ryszard Grobelny vs Grzegorz Ganowicz), w Olstynie (Czesław Małkowski vs Piotr Grzymowicz), w Bydgoszczy (Rafał Bruski vs Konstanty Dombrowicz), w Opolu (Ryszard Zembaczyński vs Tomasz Garbowski), w Szczecinie (Piotr Krzystek vs Arkadiusz Litwiński) i w Lublinie (Lech Sprawka vs Krzysztof Żuk).</p>" }
        sej_woj = { "pos": 2, "func": "structure", "name": "Sejmiki wojewódzkie", "url": "browser/col/2/view/2", "descr": "W wyborach do sejmików wojewódzkich frekwencja wyniosła 47,26% uprawnionych do głosowania. Oddano 12,06% głosów nieważnych. Ważnych głosów oddano 12 721 376", "long_descr": "<p>Sejmik województwa (potocznie: sejmik wojewódzki) jest organem stanowiącym i kontrolnym samorządu województwa, który tworzą radni, wybierani w wyborach bezpośrednich. Jego kadencja trwa cztery lata, licząc od dnia wyborów.</p><p>Sejmik jest przede wszystkim odpowiedzialny za rozwój cywilizacyjny w skali regionu, a więc za politykę regionalną.</p>" }
        wyn_wg_pc = { "pos": 3, "func": "story", "name": "Wyniki wyborów według płci", "descr": "Wyniki wyborów według płci", "url": "snapshots/a2b1c1_d1b3c2_d1", "src": "db.snapshot_a2b1c1_d1b3c2_d1" }
        wyn_wg_wk = { "pos": 4, "func": "story", "name": "Wyniki wyborów według wieku", "descr": "Wyniki wyborów według wieku", "url": "snapshots/a2b1c2_d1b3c4_d2", "src": "db.snapshot_a2b1c2_d1b3c4_d2" }

        long_descr = "<p>Wybory lokalne to bla, bla, bla, bla, bla, bla, ..., bla, z całym szcunkiem</p>"
        
        data_list = [ ww_b_pm, sej_woj, wyn_wg_pc, wyn_wg_wk ]

    data = { "data": data_list, "long_descr": long_descr }
    return data
