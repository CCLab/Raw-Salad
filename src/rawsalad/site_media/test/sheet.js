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
        new_sheet["name"] =  ( sheet_name === 'Arkusz' ) ? _store.next_sheet_name() : sheet_name;
        _store.add_new_sheet( new_sheet );
        _gui.refresh_gui();
    };

    that.display_search_result = function( col_id, recived_data ) {
        var hits = {};
        var all_raws = {};
        var result_raws = [];
        var group_num;
        var new_sheet;
        var idef;
        var parent_sort;
        var results;
        var sheet_num;
        
        var query = col_id['query'];
        var perspective = recived_data['perspective'];        
        var columns = recived_data['perspective']['columns'];
        var new_group = {
                'dataset': col_id['dataset'],
                'issue': perspective['issue'],
                'perspective': col_id['view'],
                'issue': col_id['issue'],
                'columns': columns
        };
        
        // create all_raws map and hits list
        recived_data['rows'].forEach( function( e ) {
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
            if ( !! hits.hasOwnProperty( results ) ) {
                result_raws.push( new_result_raw( results, hits, all_raws ) ); 
            }
        }

        new_sheet = {     
            'columns': columns.filter( function( e ) {
                            return e['basic'] === true;           
                       }),
            'type': _store.SEARCHED,
            'query': query,
            'name': recived_data['perspective']['perspective'],
            'sorted': false,
            'rows': result_raws
            };

        
        group_num = _store.group_exists( col_id );
        if ( group_num !== null ) {
            _store.active_group( group_num );
            sheet_num = _store.search_result_exists( query );
            if ( sheet_num  !== null ){
                _store.active_sheet( sheet_num );
                _gui.refresh_gui();
            }
            else {
                // add new sheet
                add_new_result( new_sheet, "Znalezione" );
            }
        }
        else {
            // create group
            _store.create_new_group( new_group ); 
            _store.active_group_name( perspective['perspective'] );              
            add_new_result( new_sheet, "Znalezione" );
        }
        _gui.show_table_tab();   
        if( $('#application').is(':hidden') ) {                                
            $('#application').show();
        }        
    };

// P R I V A T E   I N T E R F A C E

    function add_new_result( sheet, name ){
        that.create_new_sheet( sheet, name, true );                        
    } 


    function new_result_raw( result, hits, all_raws ) {
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
            breadcrumb.push( parent['type'].concat( ': ', parent['name'] ) );
            path.push( parent );
            parent_idef = parent ['parent'];
        }
        breadcrumb.reverse();        
        return {
            'list': list,
            'data': path,
            'breadcrumb': breadcrumb.join(' > ')
        };     
    }

    return that;

}) ();
