//  B U D G E T   D A T A 
var perspective = {
    name: "Budżet zadaniowy",
    columns: [
        {
            key: 'type',
            label: "Typ",
        },
        {
            key: 'name',
            label: "Nazwa",
            processable: true,
            type: 'string',
        },
        {
            key: 'y2010',
            label: "2010",
            processable: true,
            type: 'number',
            checkable: true
        },
        {
            key: 'y2011',
            label: "2011",
            processable: true,
            type: 'number',
            checkable: true
        }
    ]
};

var rows = [
    {
        id: 1,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 1",
        name: "Zarządzanie państwem",
        y2010: 192067,
        y2011: 955848
    },
    {
        id: 2,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 2",
        name: "Bezpieczeństwo wewnętrzne i porządek publiczny",
        y2010: 837689,
        y2011: 101529
    },
    {
        id: 3,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 3",
        name: "Edukacja, wychowanie i opieka",
        y2010: 925878,
        y2011: 154068
    },    
    {
        id: 4,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 4",
        name: "Zarządzanie finansami państwa",
        y2010: 222471,
        y2011: 990150
    },    
    {
        id: 5,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 5",
        name: "Ochrona praw i interesów skarbu państwa",
        y2010: 273210,
        y2011: 782615
    },
    {
        id: 6,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 6",
        name: "Polityka gospodarcza kraju",
        y2010: 841071,
        y2011: 380197
    },    
    {
        id: 7,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 7",
        name: "Gospodarka przestrzenna, budownictwo i mieszkalnictwo",
        y2010: 643267,
        y2011: 148055
    },    
    {
        id: 8,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 8",
        name: "Kultura fizyczna i sport",
        y2010: 441874,
        y2011: 237478
    },    
    {
        id: 9,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 9",
        name: "Kultura i dziedzictwo narodowe",
        y2010: 940369,
        y2011: 493538
    },    
    {
        id: 10,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 10",
        name: "Nauka polska",
        y2010: 572872,
        y2011: 828126
    },
    {
        id: 11,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 11",
        name: "Bezpieczeństwo zewnętrzne i nienaruszalność granic",
        y2010: 278970,
        y2011: 886087
    },
    {
        id: 12,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 12",
        name: "Środowisko",
        y2010: 281331,
        y2011: 561248
    },
    {
        id: 13,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 13",
        name: "Zabezpieczenie społeczne i wspieranie rodziny",
        y2010: 830991,
        y2011: 806957
    },    
    {
        id: 14,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 14",
        name: "Rynek pracy",
        y2010: 270003,
        y2011: 726244
    },    
    {
        id: 15,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 15",
        name: "Polityka zagraniczna",
        y2010: 542305,
        y2011: 854166
    },
    {
        id: 16,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 16",
        name: "Sprawy obywatelskie",
        y2010: 250917,
        y2011: 740607
    },    
    {
        id: 17,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 17",
        name: "Równomierny rozwój kraju",
        y2010: 477775,
        y2011: 782496
    },    
    {
        id: 18,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 18",
        name: "Sprawiedliwość",
        y2010: 153669,
        y2011: 983750
    },    
    {
        id: 19,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 19",
        name: "Infrastruktura transportowa",
        y2010: 402486,
        y2011: 296448
    },    
    {
        id: 20,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 20",
        name: "Zdrowie",
        y2010: 109632,
        y2011: 942002
    },
    {
        id: 21,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 21",
        name: "Polityka rolna i rybacka",
        y2010: 591247,
        y2011: 430414
    },
    {
        id: 22,
        level: 'a',
        parent: null,
        leaf: false,
        type: "Funkcja 22",
        name: "Planowanie strategiczne oraz obsługa administracyjna i techniczna",
        y2010: 544098,
        y2011: 718583
    },
    //  Z A D A N I A
    {
        id: 101,
        level: 'b',
        parent: 1,
        leaf: false,
        type: "Zadanie 1.1",
        name: "Zarządzanie państwem",
        y2010: 192067,
        y2011: 955848
    },
    {
        id: 102,
        level: 'b',
        parent: 1,
        leaf: false,
        type: "Zadanie 1.2",
        name: "Bezpieczeństwo wewnętrzne i porządek publiczny",
        y2010: 837689,
        y2011: 101529
    },
    {
        id: 103,
        level: 'b',
        parent: 1,
        leaf: false,
        type: "Zadanie 1.3",
        name: "Edukacja, wychowanie i opieka",
        y2010: 925878,
        y2011: 154068
    },
    //  P O D Z A D A N I A
    {
        id: 10101,
        level: 'c',
        parent: 101,
        leaf: true,
        type: "Podzadanie 1.1.1",
        name: "Zarządzanie państwem",
        y2010: 192067,
        y2011: 955848
    },
    {
        id: 10102,
        level: 'c',
        parent: 101,
        leaf: true,
        type: "Podzadanie 1.1.2",
        name: "Bezpieczeństwo wewnętrzne i porządek publiczny",
        y2010: 837689,
        y2011: 101529
    },
    {
        id: 10103,
        level: 'c',
        parent: 101,
        leaf: true,
        type: "Podzadanie 1.1.3",
        name: "Edukacja, wychowanie i opieka",
        y2010: 925878,
        y2011: 154068
    },
    {
        id: 10201,
        level: 'c',
        parent: 102,
        leaf: true,
        type: "Podzadanie 1.2.1",
        name: "Zarządzanie państwem",
        y2010: 192067,
        y2011: 955848
    },
    {
        id: 10202,
        level: 'c',
        parent: 102,
        leaf: true,
        type: "Podzadanie 1.2.2",
        name: "Bezpieczeństwo wewnętrzne i porządek publiczny",
        y2010: 837689,
        y2011: 101529
    },
    {
        id: 10203,
        level: 'c',
        parent: 102,
        leaf: true,
        type: "Podzadanie 1.2.3",
        name: "Edukacja, wychowanie i opieka",
        y2010: 925878,
        y2011: 154068
    }            
];   

