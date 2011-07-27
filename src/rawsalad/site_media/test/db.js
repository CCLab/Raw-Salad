// Copyright (c) 2011, Centrum Cyfrowe
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//   * Redistributions of source code must retain the above copyright notice,
//     this list of conditions and the following disclaimer.
//   * Redistributions in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation
//     and/or other materials provided with the distribution.
//   * Neither the name of the Centrum Cyfrowe nor the names of its contributors
//     may be used to endorse or promote products derived from this software
//     without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
// GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
// OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

var _db = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};


    that.search = function ( query, scope, strict ) {
        var data = {
            query: query,
            scope: scope.toString(),
            strict: strict.toString()
        };

        $.ajax({
            url: 'search/',
            data: data,
            dataType: 'json',
            success: function ( received_data ) {
                var tbody = $('#pl-sr-results').find('tbody');
                tbody.empty();

                received_data['strict']['result'].forEach( function ( collection ) {
                    var html = [];
                    var single_row;
                    var idefs = [];

                    html.push( '<tr style="background-color: #e3e3e3">' );
                    html.push( '<td class="pl-sr-results-number right">', collection['data'].length, '</td>' );
                    html.push( '<td class="pl-sr-results-name">' );
                    html.push( '<div class="pl-sr-results-name-text left">', collection['perspective'], '</div>' );
                    html.push( '<div class="pl-sr-results-button left">&gt;</div>' );
                    html.push( '</td>' );
                    html.push( '</tr>' );

                    single_row = $( html.join('') );
                    collection['data'].forEach( function ( result ) {
                        idefs.push( result['idef'] );
                    });

                    single_row
                        .click( function () {
                            that.add_search_data({
                                dataset: collection['dataset'],
                                view: collection['view'],
                                issue: collection['issue'],
                                idef: idefs
                            });
                        })
                        .find( '.pl-sr-results-name' )
                            .hover(
                                function () {
                                    $(this)
                                        .css( 'cursor', 'pointer' )
                                        .find( '.pl-sr-results-name-text' )
                                        .css( 'color', '#1ea3e8' )
                                        .end()
                                        .find( '.pl-sr-results-button' )
                                        .css( 'background-color', '#1ea3e8' );
                                },
                                function () {
                                    $(this)
                                        .find( '.pl-sr-results-name-text' )
                                        .css( 'color', '#000' )
                                        .end()
                                        .find( '.pl-sr-results-button' )
                                        .css( 'background-color', '#c1c1c1' );
                                }
                            );

                    tbody.append( single_row );
                });

                _utils.clear_preloader();

                $('#pl-sr-full')
                    .slideUp( 200 );

                $('#pl-sr-results')
                    .slideDown( 200 );

                $('#pl-sr-show').show();
            }
        });
    };

    that.add_search_data = function ( search_list ) {
        var col_id = {
            dataset: search_list['dataset'],
            view: search_list['view'],
            issue: search_list['issue'],
        };

        $.ajax({
            url: 'get_searched/',
            data: search_list,
            dataType: 'json',
            success: function ( received_data ) {
                // TODO: shouldnt value returned by group_exists be changed?
                if ( !_store.group_exists( col_id ) ) {
                    _sheet.create_searched_sheet( col_id, received_data );
                }
                else {
                    _sheet.add_searched_group( col_id, received_data );
                }
                _gui.show_table_tab();
            }
        }); // $.ajax
    };

    // gets the top-level from db
    that.get_init_data = function (col_id) {
        // ajax call data object
        var init_data_info = {
            "action": "get_init_data",
            "dataset": col_id.dataset,
            "perspective": col_id.perspective,
            "issue": col_id.issue
        };

        $.ajax({
            data: init_data_info,
            dataType: "json",
            success: function( received_data ) {
                var data = {
			// TODO get rid of colkumns here
			// TODO move it to create sheet function
//                    columns: received_data.perspective.columns,
                    rows: received_data.rows,
                    name: received_data.perspective.perspective
                };

                // create group
                _store.create_group({
                   "dataset": col_id.dataset,
                   "perspective": col_id.perspective,
                   "issue": col_id.issue,
                   "columns": received_data.perspective.columns,
                });
                _store.init_basic_sheet( data );
                // create a table
                _table.init_table();
                // initialize an application
                _gui.init_app( data['name'] );
            }
        });
    };


    // downloads requested nodes, appends them to object with other nodes
    // and adds html code for new nodes
    that.download_node = function ( parent_id ) {
        // ajax call data object
        var download_data = {
            action: 'get_node',
            dataset: _store.dataset(),
            perspective: _store.perspective(),
            issue: _store.issue(),
            parent: parent_id,
        };

        $.ajax({
            data: download_data,
            dataType: 'json',
            success: function( received_data ) {

                // store new data in model
                _store.add_data( received_data );
                // render new data in table
                // TODO is parent_id really necessary?!
                _table.add_node( parent_id );
//                remove_pending_node( parent_id );

                // if it was a basic sheet sign it changed
                if ( _store.active_sheet_index() === 0 ) {
                    _store.active_basic_changed( true );
                }
            }
        });
    };


    // adds a node id to list of nodes waiting to be downloaded
    // and inserted in the table
//    that.add_pending_node = function ( id ) {
//        var i;
//        var pending_nodes = _store.active_pending_nodes();
//
//        for ( i = 0; i < pending_nodes.length; i += 1 ) {
//            if ( pending_nodes[ i ] === id ) {
//                return false;
//            }
//        }
//        pending_nodes.push( id );
//
//        return true;
//    };

    return that;


//  P R I V A T E   I N T E R F A C E

    // removes a node id from the list of nodes waiting to be downloaded
//    function remove_pending_node( id ) {
//        var i;
//        var pending_nodes = _store.active_pending_nodes();
//
//        for ( i = 0; i < pending_nodes.length; i += 1 ) {
//            if ( pending_nodes[ i ] === id ) {
//                pending_nodes.splice( i, 1 );
//                return;
//            }
//        }
//    };

})();
/*
                    // to test it
                    if ( received_data['dataset'] === '0' && received_data['view'] === '0' ) {
                        received_data = {"rows": [{"wspolfin_eu": 0, "leaf": false, "name": "KANCELARIA PREZYDENTA RP", "parent": null, "level": "a", "numer": 1, "idef": "01", "swiad_fiz": 953, "wyd_majatk": 6850, "v_total": 171524, "czesc": "1", "wyd_jednostek": 121721, "dot_sub": 42000, "pozycja": 1, "type": "Cz\u0119\u015b\u0107 1", "sw_eu": 0, "wyd_dlug": 0}, {"wspolfin_eu": 0, "leaf": false, "name": "KANCELARIA SEJMU", "parent": null, "level": "a", "numer": 2, "idef": "02", "swiad_fiz": 80741, "wyd_majatk": 21276, "v_total": 430780, "czesc": "2", "wyd_jednostek": 328763, "dot_sub": 0, "pozycja": 1, "type": "Cz\u0119\u015b\u0107 2", "sw_eu": 0, "wyd_dlug": 0}, {"wspolfin_eu": 0, "leaf": false, "name": "Urz\u0119dy naczelnych organ\u00f3w w\u0142adzy pa\u0144stwowej, kontroli i ochrony prawa oraz s\u0105downictwa", "parent": "01", "level": "b", "numer": 751, "idef": "01-751", "swiad_fiz": 953, "wyd_majatk": 6850, "v_total": 129524, "czesc": "1", "wyd_jednostek": 121721, "dot_sub": 0, "pozycja": 2, "type": "Dzia\u0142 751", "sw_eu": 0, "wyd_dlug": 0}, {"wspolfin_eu": 0, "leaf": false, "name": "Kultura i ochrona dziedzictwa narodowego", "parent": "01", "level": "b", "numer": 921, "idef": "01-921", "swiad_fiz": 0, "wyd_majatk": 0, "v_total": 42000, "czesc": "1", "wyd_jednostek": 0, "dot_sub": 42000, "pozycja": 7, "type": "Dzia\u0142 921", "sw_eu": 0, "wyd_dlug": 0}], "perspective": {"sort": {"1": {"level": 1}, "0": {"idef": 1}}, "name": "budzet_ksiegowy_2011", "idef": 0, "dataset": 0, "explorable": "type", "perspective": "Bud\u017cet ksi\u0119gowy 2011", "aux": {"leaf": 1, "parent": 1, "level": 1}, "query": {"level": "a"}, "ns": "dd_budg2011_tr", "issue": "2011", "columns": [{"type": "string", "key": "idef", "label": "ID"}, {"type": "string", "processable": true, "key": "numer", "label": "Numer"}, {"type": "number", "processable": true, "key": "czesc", "label": "Cz\u0119\u015b\u0107"}, {"type": "string", "label": "Typ", "processable": true, "key": "type", "basic": true}, {"type": "string", "label": "Tre\u015b\u0107", "processable": true, "key": "name", "basic": true}, {"type": "string", "processable": true, "key": "pozycja", "label": "Pozycja"}, {"label": "Dotacje i subwencje", "processable": true, "key": "dot_sub", "basic": false, "checkable": true, "type": "number"}, {"label": "\u015awiadczenia na rzecz os\u00f3b fizycznych", "processable": true, "key": "swiad_fiz", "basic": false, "checkable": true, "type": "number"}, {"label": "Wydatki bie\u017c\u0105ce jednostek bud\u017cetowych", "processable": true, "key": "wyd_jednostek", "basic": false, "checkable": true, "type": "number"}, {"label": "Wydatki maj\u0105tkowe", "processable": true, "key": "wyd_majatk", "basic": false, "checkable": true, "type": "number"}, {"label": "Wydatki na obs\u0142ug\u0119 d\u0142ugu Skarbu Pa\u0144stwa", "processable": true, "key": "wyd_dlug", "basic": false, "checkable": true, "type": "number"}, {"label": "\u015arodki w\u0142asne Unii Europejskiej", "processable": true, "key": "sw_eu", "basic": false, "checkable": true, "type": "number"}, {"label": "Wsp\u00f3\u0142finansowanie projekt\u00f3w z udzia\u0142em \u015brodk\u00f3w Unii Europejskiej", "processable": true, "key": "wspolfin_eu", "basic": false, "checkable": true, "type": "number"}, {"label": "OG\u00d3\u0141EM", "processable": true, "key": "v_total", "basic": true, "checkable": true, "type": "number"}]}}
                    }
                    else if ( received_data['dataset'] === '0' && received_data['view'] === '1' ) {
                        received_data = {"rows": [{"info": null, "leaf": false, "name": "ZARZ\u0104DZANIE PA\u0143STWEM", "parent": null, "level": "a", "idef": "1", "czesc": null, "czesc_name": null, "v_nation": 1343628, "type": "FUNKCJA 1"}, {"info": null, "leaf": false, "name": "BEZPIECZE\u0143STWO WEWN\u0118TRZNE I PORZ\u0104DEK PUBLICZNY", "parent": null, "level": "a", "idef": "2", "czesc": null, "czesc_name": null, "v_nation": 15764059, "type": "FUNKCJA 2"}, {"info": null, "leaf": false, "name": "EDUKACJA, WYCHOWANIE I OPIEKA", "parent": null, "level": "a", "idef": "3", "czesc": null, "czesc_name": null, "v_nation": 52368661, "type": "FUNKCJA 3"}, {"info": null, "leaf": false, "name": "Ochrona obywateli, utrzymanie porz\u0105dku publicznego oraz dzia\u0142ania na rzecz poprawy bezpiecze\u0144stwa", "parent": "2", "level": "b", "idef": "2-1", "czesc": null, "czesc_name": null, "v_nation": 5829003, "type": "Zadanie 2.1"}, {"info": null, "leaf": false, "name": "Redukowanie przest\u0119pczo\u015bci", "parent": "2", "level": "b", "idef": "2-2", "czesc": null, "czesc_name": null, "v_nation": 3015132, "type": "Zadanie 2.2"}, {"info": null, "leaf": false, "name": "Strze\u017cenie praworz\u0105dno\u015bci i czuwanie nad \u015bciganiem przest\u0119pstw przez prokuratur\u0119", "parent": "2", "level": "b", "idef": "2-3", "czesc": null, "czesc_name": null, "v_nation": 1066093, "type": "Zadanie 2.3"}, {"info": null, "leaf": false, "name": "Ochrona przeciwpo\u017carowa, dzia\u0142alno\u015b\u0107 zapobiegawcza, ratownicza i ga\u015bnicza", "parent": "2", "level": "b", "idef": "2-4", "czesc": null, "czesc_name": null, "v_nation": 2225298, "type": "Zadanie 2.4"}, {"info": null, "leaf": false, "name": "Zarz\u0105dzanie kryzysowe i obrona cywilna", "parent": "2", "level": "b", "idef": "2-5", "czesc": null, "czesc_name": null, "v_nation": 2131002, "type": "Zadanie 2.5"}, {"info": null, "leaf": false, "name": "Ochrona granicy pa\u0144stwowej, kontrola ruchu granicznego i przeciwdzia\u0142anie nielegalnej migracji", "parent": "2", "level": "b", "idef": "2-6", "czesc": null, "czesc_name": null, "v_nation": 1497531, "type": "Zadanie 2.6"}, {"idef_sort": "0003-0001", "name": "O\u015bwiata i wychowanie", "parent": "3", "level": "b", "parent_sort": "0003", "idef": "3-1", "czesc": null, "czesc_name": null, "v_nation": 40384231, "leaf": false, "type": "Zadanie 3.1"}, {"idef_sort": "0003-0002", "name": "Szkolnictwo wy\u017csze", "parent": "3", "level": "b", "parent_sort": "0003", "idef": "3-2", "czesc": null, "czesc_name": null, "v_nation": 11984430, "leaf": false, "type": "Zadanie 3.2"}, {"idef_sort": "0003-0002-0001", "name": "Zarz\u0105dzanie systemem szkolnictwa wy\u017cszego", "parent": "3-2", "level": "c", "parent_sort": "0003-0002", "idef": "3-2-1", "czesc": null, "czesc_name": null, "v_nation": 35793, "leaf": false, "type": "Podzadanie 3.2.1"}, {"idef_sort": "0003-0002-0002", "name": "Kszta\u0142cenie w szkolnictwie wy\u017cszym", "parent": "3-2", "level": "c", "parent_sort": "0003-0002", "idef": "3-2-2", "czesc": null, "czesc_name": null, "v_nation": 9620851, "leaf": false, "type": "Podzadanie 3.2.2"}, {"idef_sort": "0003-0002-0003", "name": "Wsparcie procesu studiowania", "parent": "3-2", "level": "c", "parent_sort": "0003-0002", "idef": "3-2-3", "czesc": null, "czesc_name": null, "v_nation": 1795244, "leaf": false, "type": "Podzadanie 3.2.3"}, {"idef_sort": "0003-0002-0004", "name": "Utrzymanie i rozbudowa infrastruktury szkolnictwa wy\u017cszego", "parent": "3-2", "level": "c", "parent_sort": "0003-0002", "idef": "3-2-4", "czesc": null, "czesc_name": null, "v_nation": 532542, "leaf": false, "type": "Podzadanie 3.2.4"}], "perspective": {"sort": {"1": {"parent_sort": 1}, "0": {"idef_sort": 1}, "2": {"level": 1}}, "name": "budzet_zadaniowy_podzadania_2012", "max_level": "d", "idef": 1, "dataset": 0, "explorable": "type", "perspective": "Bud\u017cet zadaniowy 2012 - Podzadanie", "aux": {"idef": 1, "leaf": 1, "parent": 1, "level": 1}, "query": {"node": {"$in": [null, 1]}, "level": "a"}, "ns": "dd_budg2012_go", "issue": "2012", "columns": [{"type": "string", "label": "Typ", "processable": false, "key": "type", "basic": true}, {"type": "string", "label": "Nazwa", "processable": true, "key": "name", "basic": true}, {"type": "string", "processable": true, "key": "czesc", "label": "Cz\u0119\u015b\u0107"}, {"type": "string", "processable": true, "key": "czesc_name", "label": "Cz\u0119\u015b\u0107 w bud\u017aecie ksi\u0119gowym"}, {"type": "string", "label": "Cel & Miernik", "processable": false, "key": "info", "basic": false}, {"label": "Bud\u017cet Pa\u0144stwa", "processable": true, "key": "v_nation", "basic": true, "checkable": true, "type": "number"}]}};
                    }
*/
