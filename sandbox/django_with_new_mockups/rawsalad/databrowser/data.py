# -*- coding: utf-8 -*-

perspective = {
    "name": "budzet_zadaniowy", 
    "idef": 1, 
    "collection": "dd_budg2011_go", 
    "perspective": "Budżet zadaniowy", 
    "columns": [
        {
            "type": "string", 
            "processable": True, 
            "key": "idef", 
            "label": "Numer"
        }, 
        {
            "type": "string", 
            "label": "Typ", 
            "processable": True, 
            "key": "type", 
            "basic": True
        }, 
        {
            "type": "string", 
            "label": "Nazwa", 
            "processable": True, 
            "key": "name", 
            "basic": True
        }, 
        {
            "type": "string", 
            "processable": True, 
            "key": "czesc", 
            "label": "Część"
        }, 
        {
            "type": "string", 
            "processable": True, 
            "key": "cel", 
            "label": "Cel"
        }, 
        {
            "type": "string", 
            "processable": True, 
            "key": "miernik_nazwa", 
            "label": "Miernik"
        }, 
        {
            "type": "string", 
            "processable": True, 
            "key": "miernik_wartosc_bazowa", 
            "label": "Wartość bazowa"
        }, 
        {
            "type": "string", 
            "processable": True, 
            "key": "miernik_wartosc_rb", 
            "label": "Wartość br."
        }, 
        {
            "label": "OGÓŁEM", 
            "processable": True, 
            "key": "v_total", 
            "basic": True, 
            "checkable": True, 
            "type": "number"
        }, 
        {
            "label": "Budżet Państwa", 
            "processable": True, 
            "key": "v_nation", 
            "basic": True, 
            "checkable": True, 
            "type": "number"
        }, 
        {
            "label": "Środki Europejskie", 
            "processable": True, 
            "key": "v_eu", 
            "basic": True, 
            "checkable": True, 
            "type": "number"
        }
    ]
}

new_rows = [
        {
            "leaf": False, 
            "name": "ZARZĄDZANIE PAŃSTWEM", 
            "parent": None, 
            "level": "a", 
            "idef": "1", 
            "v_eu": 25140, 
            "v_total": 1561521, 
            "v_nation": 1536381, 
            "type": "FUNKCJA 1"
        },
        {
            "leaf": False, 
            "name": "BEZPIECZEŃSTWO WEWNĘTRZNE I PORZĄDEK PUBLICZNY", 
            "parent": None, 
            "level": "a", 
            "idef": "2", 
            "v_eu": 58779, 
            "v_total": 14170616, 
            "v_nation": 14111837, 
            "type": "FUNKCJA 2"
        }, 
        {
            "leaf": False, 
            "name": "EDUKACJA, WYCHOWANIE I OPIEKA", 
            "parent": None, 
            "level": "a", 
            "idef": "3", 
            "v_eu": 1016384, 
            "v_total": 14379196, 
            "v_nation": 13362812, 
            "type": "FUNKCJA 3"
        },
    {
        "leaf": False, 
        "name": "Obsługa merytoryczna i kancelaryjno-biurowa Prezydenta Rzeczypospolitej Polskiej", 
        "parent": "1", 
        "v_eu": 0, 
        "idef": "1-1", 
        "level": "b", 
        "v_total": 151833, 
        "v_nation": 151833, 
        "type": "Zadanie 1.1"
    }, 
    {
        "leaf": False, 
        "name": "Obsługa Parlamentu i jego organów w zakresie merytorycznym i organizacyjnym", 
        "parent": "1", 
        "v_eu": 0, 
        "idef": "1-2", 
        "level": "b", 
        "v_total": 445085, 
        "v_nation": 445085, 
        "type": "Zadanie 1.2"
    },
    {
        "leaf": False, 
        "name": "Ochrona obywateli i utrzymanie porządku publicznego", 
        "parent": "2", 
        "v_eu": 37059, 
        "idef": "2-1", 
        "level": "b", 
        "v_total": 5795284, 
        "v_nation": 5758225, 
        "type": "Zadanie 2.1"
    }, 
    {
        "leaf": False, 
        "name": "Redukowanie przestępczości i działania na rzecz poprawy społecznego poczucia bezpieczeństwa", 
        "parent": "2", 
        "v_eu": 21650, 
        "idef": "2-2", 
        "level": "b", 
        "v_total": 3084993, 
        "v_nation": 3063343, 
        "type": "Zadanie 2.2"
    },
    {
        "leaf": False, 
        "name": "Edukacja i wychowanie", 
        "parent": "3", 
        "v_eu": 395308, 
        "idef": "3-1", 
        "level": "b", 
        "v_total": 1929627, 
        "v_nation": 1534319, 
        "type": "Zadanie 3.1"
    }, 
    {
        "leaf": False, 
        "name": "Szkolnictwo wyższe", 
        "parent": "3", 
        "v_eu": 619691, 
        "idef": "3-2", 
        "level": "b", 
        "v_total": 12442732, 
        "v_nation": 11823041, 
        "type": "Zadanie 3.2"
    },
    {
        "leaf": False, 
        "name": "Obsługa i koordynacja urzędu Prezydenta RP", 
        "parent": "1-1", 
        "v_eu": 0, 
        "idef": "1-1-1", 
        "level": "c", 
        "v_total": 130148, 
        "v_nation": 130148, 
        "type": "Podzadanie 1.1.1"
    }, 
    {
        "leaf": False, 
        "name": "Obsługa prawna urzędu Prezydenta RP", 
        "parent": "1-1", 
        "v_eu": 0, 
        "idef": "1-1-2", 
        "level": "c", 
        "v_total": 4960, 
        "v_nation": 4960, 
        "type": "Podzadanie 1.1.2"
    },
    {
        "leaf": False, 
        "name": "Wsparcie merytoryczne parlamentarzystów", 
        "parent": "1-2", 
        "v_eu": 0, 
        "idef": "1-2-1", 
        "level": "c", 
        "v_total": 62815, 
        "v_nation": 62815, 
        "type": "Podzadanie 1.2.1"
    }, 
    {
        "leaf": False, 
        "name": "Zapewnianie warunków wykonywania mandatu posła i senatora", 
        "parent": "1-2", 
        "v_eu": 0, 
        "idef": "1-2-2", 
        "level": "c", 
        "v_total": 382270, 
        "v_nation": 382270, 
        "type": "Podzadanie 1.2.2"
    },
    {
        "leaf": False, 
        "name": "Zapewnienie bezpieczeństwa wewnęrznego państwa", 
        "parent": "2-1", 
        "v_eu": 0, 
        "idef": "2-1-1", 
        "level": "c", 
        "v_total": 529669, 
        "v_nation": 529669, 
        "type": "Podzadanie 2.1.1"
    }, 
    {
        "leaf": False, 
        "name": "Zapewnienie bezpieczeństwa najważniejszym osobom, obiektom i urządzeniom w państwie", 
        "parent": "2-1", 
        "v_eu": 0, 
        "idef": "2-1-2", 
        "level": "c", 
        "v_total": 177382, 
        "v_nation": 177382, 
        "type": "Podzadanie 2.1.2"
    },
    {
        "leaf": False, 
        "name": "Zapewnienie działania służby śledczej i kryminalnej", 
        "parent": "2-2", 
        "v_eu": 21650, 
        "idef": "2-2-1", 
        "level": "c", 
        "v_total": 2946403, 
        "v_nation": 2924753, 
        "type": "Podzadanie 2.2.1"
    }, 
    {
        "leaf": False, 
        "name": "Zwalczanie korupcji", 
        "parent": "2-2", 
        "v_eu": 0, 
        "idef": "2-2-2", 
        "level": "c", 
        "v_total": 106971, 
        "v_nation": 106971, 
        "type": "Podzadanie 2.2.2"
    },
    {
        "leaf": False, 
        "name": "Zarządzanie i nadzór nad systemem edukacji i wychowania", 
        "parent": "3-1", 
        "v_eu": 52454, 
        "idef": "3-1-1", 
        "level": "c", 
        "v_total": 145435, 
        "v_nation": 92981, 
        "type": "Podzadanie 3.1.1"
    }, 
    {
        "leaf": False, 
        "name": "Kształcenie ogólne, zawodowe i ustawiczne", 
        "parent": "3-1", 
        "v_eu": 66980, 
        "idef": "3-1-2", 
        "level": "c", 
        "v_total": 1045109, 
        "v_nation": 978129, 
        "type": "Podzadanie 3.1.2"
    },
    {
        "leaf": False, 
        "name": "Zarządzanie systemem szkolnictwa wyższego", 
        "parent": "3-2", 
        "v_eu": 0, 
        "idef": "3-2-1", 
        "level": "c", 
        "v_total": 28892, 
        "v_nation": 28892, 
        "type": "Podzadanie 3.2.1"
    }, 
    {
        "leaf": False, 
        "name": "Kształcenie w szkolnictwie wyższym akademickim", 
        "parent": "3-2", 
        "v_eu": 355685, 
        "idef": "3-2-2", 
        "level": "c", 
        "v_total": 9848166, 
        "v_nation": 9492481, 
        "type": "Podzadanie 3.2.2"
    },
    {
        "leaf": True, 
        "name": "Kancelaria Prezydenta RP", 
        "parent": "1-1-1", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-1-dt1", 
        "cel": "Zapewnienie realizacji zadań konstytucyjnych i ustawowych Prezydenta Rzeczypospolitej Polskiej", 
        "miernik_nazwa": "Racjonalne wykorzystanie środków budżetowych", 
        "v_eu": 0, 
        "v_total": 130148, 
        "czesc": "01", 
        "v_nation": 130148, 
        "miernik_wartosc_bazowa": "98,4%", 
        "miernik_wartosc_rb": "99,9%"
    },
    {
        "leaf": True, 
        "name": "Kancelaria Prezydenta RP", 
        "parent": "1-1-2", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-1-dt1", 
        "cel": "Zapewnienie realizacji obsługi prawnej Prezydenta Rzeczypospolitej Polskiej", 
        "miernik_nazwa": "Racjonalne wykorzystanie środków budżetowych", 
        "v_eu": 0, 
        "v_total": 4960, 
        "czesc": "01", 
        "v_nation": 4960, 
        "miernik_wartosc_bazowa": "98,4%", 
        "miernik_wartosc_rb": "99,9%"
    },
    {
        "leaf": True, 
        "name": "Kancelaria Sejmu", 
        "parent": "1-2-1", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-2-dt1", 
        "cel": "Zapewnienie dostępu do wiedzy, analiz i ekspertyz niezbędnych w pracy parlamentarzystów", 
        "miernik_nazwa": "Ankieta badająca poziom zadowolenia posłów z działań podejmowanych przez Kancelarię Sejmu", 
        "v_eu": 0, 
        "v_total": 50426, 
        "czesc": "02", 
        "v_nation": 50426, 
        "miernik_wartosc_bazowa": "4,2", 
        "miernik_wartosc_rb": "4,2"
    }, 
    {
        "leaf": True, 
        "name": "Kancelaria Senatu", 
        "parent": "1-2-1", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-2-dt2", 
        "cel": "Zapewnianie dostępu do wiedzy, analiz i ekspertyz niezbędnych w pracy parlamentarzystów", 
        "miernik_nazwa": "Ocena wsparcia merytorycznego ze strony  Kancelarii Senatu dokonana przez senatorów (skala 1-4, gdzie 1 - ocena zła, 4 - ocena bardzo dobra)", 
        "v_eu": 0, 
        "v_total": 12389, 
        "czesc": "03", 
        "v_nation": 12389, 
        "miernik_wartosc_bazowa": "3,76", 
        "miernik_wartosc_rb": "> 3,77"
    },
    {
        "leaf": True, 
        "name": "Kancelaria Sejmu", 
        "parent": "1-2-2", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-2-dt1", 
        "cel": "Zapewnienie sprawnej obsługi parlamentarzystów, warunków niezbędnych do skutecznej realizacji obowiązków oraz ochrony praw wynikających ze sprawowania mandatu", 
        "miernik_nazwa": "Ankieta badająca poziom zadowolenia posłów z działań podejmowanych przez Kancelarię Sejmu ", 
        "v_eu": 0, 
        "v_total": 329750, 
        "czesc": "02", 
        "v_nation": 329750, 
        "miernik_wartosc_bazowa": "4,2", 
        "miernik_wartosc_rb": "4,2"
    }, 
    {
        "leaf": True, 
        "name": "Kancelaria Senatu", 
        "parent": "1-2-2", 
        "level": "d", 
        "type": "Dysponent", 
        "idef": "1-2-dt2", 
        "cel": "Zapewnianie sprawnej obsługi parlamentarzystów, warunków niezbędnych do skutecznej realizacji obowiązków oraz ochrony praw wynikających ze sprawowania mandatu", 
        "miernik_nazwa": "Ocena sprawności i efektywności obsługi Kancelarii Senatu dokonana przez senatorów (skala 1-4, gdzie 1 - ocena zła, 4 - ocena bardzo dobra)", 
        "v_eu": 0, 
        "v_total": 52520, 
        "czesc": "03", 
        "v_nation": 52520, 
        "miernik_wartosc_bazowa": "3,73", 
        "miernik_wartosc_rb": "> 3,77"
    }
]