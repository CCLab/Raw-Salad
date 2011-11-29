#!/usr/bin/python
# -*- coding: utf-8 -*-

import getpass
import os
import optparse
import rsdbapi as rsdb
from ConfigParser import ConfigParser

if __name__ == "__main__":    
    updates= {
        'dataset': '0',
        'view': '1',
        'issue': '2011',
        'data': [
            {
                'idef': '10-1-1',
                'v_nation': 3000000
                },
            {
                'idef': '15-4',
                'name': 'Kształtowanie międzynarodowego wizerunku RP updatiki'
                },
            {
                'idef': '17-3-2-1',
                'v_nation': 800000,
                'info': [
                    {
                        'wartosc_rok_obec': None,
                        'leaf': False,
                        'elem_type': 'Cel',
                        'parent': '17-3-2-1',
                        'parent_sort': '0017-0003-0002-0001',
                        'idef': '17-3-2-1-1',
                        'elem_level': 'e',
                        'idef_sort': '0017-0003-0002-0001-0001',
                        'elem_name': 'Sprawna realizacja PO IG w latach 2007-2015 updatiki',
                        'wartosc_bazowa': None
                        },
                    {
                        'wartosc_rok_obec': '44,63%',
                        'leaf': True,
                        'elem_type': 'Miernik',
                        'parent': '17-3-2-1-1',
                        'parent_sort': '0017-0003-0002-0001-0001',
                        'idef': '17-3-2-1-1-1',
                        'elem_level': 'f',
                        'idef_sort': '0017-0003-0002-0001-0001-0001',
                        'elem_name': 'Wartość środków certyfikowanych do KE do wartości alokacji',
                        'wartosc_bazowa': '13,62%'
                        }                    
                    ]
                }
            ]
        }

    usrkey= '987654321123456789'

    db= rsdb.DBconnect("mongodb").dbconnect

    is_usrkey= rsdb.Usrkey()
    if is_usrkey.get_key(usrkey, db):

        coll= rsdb.Collection()

        for currdoc in updates['data']:
            coll.set_query( {'idef': currdoc['idef'].strip() } )
            res= coll.get_data(db, updates['dataset'], updates['view'], updates['issue'])
            for curr_res in res:
                new_doc= curr_res
                new_doc.update( currdoc )
                try:
                    coll.save_doc(new_doc, updates['dataset'], updates['view'], updates['issue'], currdoc['idef'].strip(), db)
                except:
                    print coll.response
    else:
        print is_usrkey.response
