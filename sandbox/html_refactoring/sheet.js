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
        var group_nr = _store.active_group_index();
        var sheet_nr = _store.next_sheet_number();
        var new_sheet = {};

        // TODO check if it's needed, because sheet_data may be not reference, but
        // deep a copied object
        $.extend( true, new_sheet, sheet_data );
        new_sheet["name"] = sheet_name + ' ' + sheet_nr;

        _store.add_new_sheet( new_sheet );
        _gui.refresh_gui();
 //       if ( !!no_table ) {
 //           _gui.create_only_sheet_tab({
 //               'name': new_sheet['name'],
 //               'sheet_nr': sheet_nr,
 //               'group_nr': group_nr,
 //           });
 //       } else {
 //           _gui.create_sheet_tab({
 //               'name': new_sheet['name'],
 //               'sheet_nr': sheet_nr,
 //               'group_nr': group_nr,
 //           });
 //       }
    };
    
    that.add_searched_group = function ( col_id, data, sheets_left ) {
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
           "perspective": col_id.perspective,
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
        
        // if it's the last sheet, create tab and show table,
        // otherwise create only tab
        _gui.refresh_gui();
//        if ( sheets_left === 0 ) {
//            _gui.init_app( basic_data['name'] );
//        } else {
//            _gui.create_only_sheet_tab({
//                name: basic_data['name'],
//                group_nr: _store.active_group_index(),
//                sheet_nr: _store.active_sheet_index()
//            });
//        }
    };
    
    that.create_searched_sheet = function ( col_id, data, sheets_left ) {
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
                            state: { open: false, selected: false }
                        };
                    }),
            'filtered': false,
        };
        
        // change subtrees nodes' parents' state to open
        if ( !!additional_rows ) {
            _tools.open_subtrees( new_sheet['rows'], additional_rows );
        }

        // create new sheet containing search data
        // and if it is the last sheet to create, show table
        if ( sheets_left === 0 ) {
            that.create_new_sheet( new_sheet, "Arkusz" );
        } else {
            that.create_new_sheet( new_sheet, "Arkusz", true );
        }
        
    };

    return that;

// P R I V A T E  I N T E R F A C E
    var clean_basic_sheet = function () {
        var active_sheet_number;
        var basic_sheet;
        var basic_sheet_rows = [];

        active_sheet_number = _store.active_sheet_index();

        _store.active_sheet_index(0);
        _store.acitve_sheet_rows( basic_sheet_rows );
        _store.active_basic_changed( false );

        _store.active_sheet_index( active_sheet_number );
    };

}) ();
