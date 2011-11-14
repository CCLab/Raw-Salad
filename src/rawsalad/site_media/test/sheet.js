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

var _sheet = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    that.create_new_sheet = function ( sheet_data, sheet_name, no_table ) {
        var new_sheet = {};

        $.extend( true, new_sheet, sheet_data );
        new_sheet["name"] = _store.next_sheet_name();

        _store.add_new_sheet( new_sheet );
        _gui.refresh_gui();
    };

    // TODO remove - not needed
    that.add_searched_group = function ( col_id, data ) {
        var basic_rows;
        var additional_rows;
        var basic_data;

        basic_rows = data.rows.filter( function ( e ) {
            return e['level'] === 'a';
        });
        additional_rows = data.rows.filter( function ( e ) {
            return e['level'] !== 'a';
        });

        basic_data = {
            rows: basic_rows,
            name: data.perspective.perspective
        };
        // create group
        _store.create_group({
           "dataset": col_id.dataset,
           "perspective": col_id.view,
           "issue": col_id.issue,
           "columns": data.perspective.columns
        });

        // create basic sheet with basic rows
        _store.init_basic_sheet( basic_data );

        // add subtrees needed to show nodes found by search
        // and change their parents' state to open
        if ( !!additional_rows ) {
            _store.add_data( additional_rows );
            _tools.open_subtrees( _store.active_rows(), additional_rows );
        }

        _gui.init_app( basic_data['name'] );
    };


    // TODO remove - not needed
    that.create_searched_sheet = function ( col_id, data ) {
        var new_sheet;
        var additional_rows;

        additional_rows = data.rows.filter( function ( e ) {
            return e['level'] !== 'a';
        });

        // set active group number to index of group with
        // the same dataset, view and issue as chosen collection
        _store.create_new_group( col_id );

        new_sheet = {
            'columns': _store.active_group()['columns'].filter( function ( e ) {
                           return e['basic'] === true;
                       }),
            'rows': data['rows'].map( function ( row ) {
                        return {
                            data: row,
                            state: { open: false, selected: false, visible: true }
                        };
                    }),
            'type': _store.FILTERED,
        };

        if( new_sheet['rows'][ new_sheet['rows'].length - 1 ]['data']['idef'].indexOf( '9999' ) !== -1 ) {
            new_sheet['rows']['total'] = new_sheet['rows'].pop();
        }

        // change subtrees nodes' parents' state to open
        if ( !!additional_rows ) {
            _tools.open_subtrees( new_sheet['rows'], additional_rows );
        }

        // create new sheet containing search data
        that.create_new_sheet( new_sheet, 'Arkusz' );

    };

    that.display_search_result = function( col_id, recived_data ) {
        var hits = {};
        var all_raws = {};
        var result_raws = [];
        
        var new_sheet;
        var idef;
        var parent_sort;
        var results;
        
        var query = col_id['query'];
        var columns = recived_data['perspective']['columns'];
        
        // create all_raws map and hits list
        recived_data['rows'].forEach( function( e ){
            idef = e['idef'];
            all_raws[ idef ] = e;
            if ( !! _algorithms.is_search_result( query, e, columns )  ) {

                parent_sort = ( e['parent_sort'] === null  ) ? '_root' : e['parent_sort'];                               
                hits[parent_sort] = hits[parent_sort] || [];
                hits[parent_sort].push( idef );
            }
        });
        
        // create hits table
        for ( results in hits ) {
            if ( hits.hasOwnProperty( results ) ) {
                result_raws.push( new_result_raw( results, hits, all_raws ) ); 
            }
        }
        
        if ( _store.group_exists( col_id ) ) {
            that.create_searched_sheet( col_id, received_data );
        }
        else {
            // create group
            _store.create_group({
                'dataset': col_id.dataset,
                'perspective': col_id.view,
                'issue': col_id.issue,
                'columns': columns
            });   
            new_sheet = {     
                'columns' : columns.filter( function( e ) {
                                return e['basic'] === true;           
                            }),
                'type': _store.SEARCHED,
                'name': recived_data['perspective']['perspective'],
                'sorted': false,
                'rows': result_raws
            };
            _sheet.create_new_sheet( new_sheet, "Arkusz", true );            
            
//                _table.clean_table();
//                _table.init_table();
            
// TODO remove - just example            
//        basic_rows = data.rows.filter( function ( e ) {
//            return e['level'] === 'a';
//        });
            
            //_sheet.add_searched_group( col_id, received_data );
        }
        
        
        
        
        
//        hits.sort();
    };

// P R I V A T E   I N T E R F A C E

    function new_result_raw( result, hits, all_raws ) {
        var hit_raw = {};
        var path = [];
        var list = [];
        var breadcrumb = [];
        var idef;
        
        var hits_table = hits[ result ];
        var parent_idef = all_raws[ hits_table [0] ] ['parent'];
        
        hits_table.forEach( function ( idef ) {            
            list.push( all_raws[ idef ] );
        });                
        while ( parent_idef !== null ){          
            parent = all_raws[ parent_idef ];
            breadcrumb.push( parent['name'] );
            path.push( parent );
            parent_idef = parent ['parent'];
        }
        breadcrumb.reverse();        
        return {
            'list': list,
            'path': path,
            'breadcrumb': breadcrumb.join(' > ')
        };     
    }
    
    return that;
}) ();


