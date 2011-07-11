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
                var tmp_data = [
                    {
                        dataset: 0,
                        view: 0,
                        issue: 2011,
                        name: 'gospodarka',
                        data: [
                            {
                                czesc: "1",
                                dot_sub: 42000,
                                idef: "01-921",
                                leaf: false,
                                level: "b",
                                name: "Kultura i ochrona dziedzictwa narodowego",
                                numer: 921,
                                parent: "01",
                                pozycja: 7,
                                sw_eu: 0,
                                swiad_fiz: 0,
                                type: "Dzia³ 921",
                                v_total: 42000,
                                wspolfin_eu: 0,
                                wyd_dlug: 0,
                                wyd_jednostek: 0,
                                wyd_majatk: 0
                            }
                        ]
                    },
                    {
                        dataset: 0,
                        view: 1,
                        issue: 2012,
                        name: 'gospodarka',
                        data: [
                            {
                                czesc: null,
                                czesc_name: null,
                                idef: "2-2",
                                info: null,
                                leaf: false,
                                level: "b",
                                name: "Redukowanie przestêpczoœci",
                                parent: "2",
                                type: "Zadanie 2.2",
                                v_nation: 3015132
                            }
                        ]
                    }
                ];
                _tools.show_search_results( tmp_data );
                console.log( tmp_data );
            }
        });
    };
    
    that.add_search_data = function ( search_list ) {
        var data;
        search_list.forEach( function ( e ) {
            data = {
                dataset: e['dataset'],
                view: e['view'],
                issue: e['issue'],
                data: e['data'].map( function ( elem ) {
                          return elem['idef'];
                      })
            };
            
            $.ajax({
                url: 'get_searched/',
                data: data,
                dataType: 'json',
                success: function ( received_data ) {
                    var col_id = {
                        'dataset': data['dataset'],
                        'perspective': data['view'],
                        'issue': data['issue']
                    };
                    var basic_data;
                    var basic_rows;
                    var additional_rows;
                    var i;
                    var groups;
                    var group_nr;
                    var new_sheet;
                    
                    if ( _store.group_exists(col_id) ) {
                        groups = _store.get_all_groups;
                        for ( i = 0; i < groups.length; i += 1 ) {
                            if ( col_id['dataset'] === groups[i]['dataset'] &&
                                 col_id['perspective'] === groups[i]['perspective'] &&
                                 col_id['issue'] === groups[i]['issue'] ) {
                                group_nr = i;
                                break;
                            }
                        }
                            
                        _assert.assert( (group_nr === 0 || !!group_nr),
                                        'Collection not found');
                        
                        // set active group number to index of group with
                        // the same dataset, view and issue as chosen collection
                        _store.active_group( group_nr );
                        
                        new_sheet = {
                            'rows': received_data['rows'],
                            'name': 'Arkusz ' + _store.next_sheet_number()
                        };
                        
                        // create new sheet containing search data
                        _sheet.create_new_sheet( new_sheet, "Arkusz" );                        
                    } else {
                        basic_rows = received_data.rows.filter( function ( e ) {
                            return e['level'] === 'a';
                        });
                        additional_rows = received_data.rows.filter( function ( e ) {
                            return e['level'] !== 'a';
                        });
                        
                        basic_data = {
                            rows: basic_rows,
                            name: received_data.perspective.perspective
                        };

                        // create group
                        _store.create_group({
                           "dataset": col_id.dataset,
                           "perspective": col_id.perspective,
                           "issue": col_id.issue,
                           "columns": received_data.perspective.columns
                        });
                        
                        // create basic sheet with basic rows
                        _store.init_basic_sheet( basic_data );
                        
                        // add subtrees needed to show nodes found by search
                        if ( !!additional_rows ) {
                            _store.add_data( additional_rows );
                        }
                        
                        // initialize an application
                        _gui.init_app( basic_data['name'] );
                    }
                } // function( received_data )
            }); // $.ajax
        }); // forEach
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
