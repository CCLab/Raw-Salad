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

var _store = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    // meta_data setter/getter
    that.meta_data = function ( value ) {
        // set it just once
//        _assert.is_equal( meta_data.length, 0,
//                          "meta_data already assigned" );

        meta_data = value;
    };


    // get metadata about available datasets
    that.meta_datasets = function () {
        return meta_data;
    };


    // get metadata about perspectives available in a cerain dataset
    that.meta_perspectives = function ( dataset_id ) {
        return meta_data[ dataset_id ]['perspectives'];
    };


    // check if group exists
    that.group_exists = function (data) {
        if( find_group( data ) !== -1) {
            return false;
        }
        return true;
    };


    // creates a new group and sets an activ group index
    that.create_group = function (data) {
        // create a group for new data collection
        groups.push( group( data ));
        that.active_group( groups.length - 1 );
    };


    // creates a new group or sets an active group index to apropriate group
    that.create_new_group = function ( data ) {
        var found = find_group( data );

        if( found !== -1 ) {
            that.active_group( found );
            return false;
        }

        // create a group for new data collection
        groups.push( group( data ));
        that.active_group( groups.length - 1 );

        return true;
    };


    that.dataset = function () {
        return that.active_group()['dataset'];
    };


    that.perspective = function () {
        return that.active_group()['perspective'];
    };


    that.issue = function () {
        return that.active_group()['issue'];
    };


    that.init_basic_sheet = function ( data ) {
        var active_grp = that.active_group();

        // store original version of collection
        active_grp['basic_rows'] = sheet( data, true );
        // add data to mutable list of sheets
        active_grp['sheets'].push( sheet( data ) );
    };


    that.set_active_columnes = function ( columns ) {
        that.active_sheet()['columns'] = columns;
    };


    that.get_column_from_group = function( id ) {
        var columns = that.active_group()['columns'];
        return columns.filter( function ( col ) {
            return col['key'] === id;
        })[0];
    };


    that.active_columns = function () {
        return that.active_sheet()['columns'];
    };


    that.group_columns = function () {
        return that.active_group()['columns'];
    };


    //TODO not needed
    that.basic_schema = function () {
        var full_schema = that.active_columns();

        return full_schema.filter( function ( element ) {
            return element['basic'] === true;
        });
    };


    that.set_selected = function ( id, state ) {
        var node, rows = that.active_rows();
        var i, len = rows.length;

        for( i = 0; i < len; i += 1 ) {
            node = rows[i];
            if( node['data']['idef'] === id ) {
                node['state']['selected'] = state;
                return;
            }
        }
//        that.active_rows().forEach( function ( node ) {
//            if( node['data']['idef'] === id ) {
//                node['state']['selected'] = true;
//            }
//            else {
//                node['state']['selected'] = false;
//            }
//        });
    };


    that.is_node_in_store = function ( id ) {
        var i;
        var parent;
        var rows = that.active_rows();
        for ( i= rows.length - 1; i >= 0; i-- ){
            parent = rows[i]['data']['parent']; 
            if( parent === id ){
                return true;
            }        
        }
        return false;        
    };

    that.set_open = function ( id, state ) {
        var node, rows = that.active_rows();
        var i, len = rows.length;

        for( i = 0; i < len; i += 1 ) {
            node = rows[i];
            if( node['data']['idef'] === id ) {
                node['state']['open'] = state;
                return;
            }
        }
    };


    that.active_sheet_index = function ( new_active_sheet_num ) {
        if( arguments.length === 0 ) {
            return that.active_group()['active_sheet_number'];
        }
        that.active_group()['active_sheet_number'] = new_active_sheet_num;
    };

    that.active_group_index = function () {
        return active_group_number;
    };

    that.next_sheet_number = function () {
        return that.active_group()['sheets'].length;
    };

    that.max_group_number = function () {
        return groups.length;
    };

    that.active_rows = function () {
        return that.active_sheet()['rows'];
    };


//    that.active_pending_nodes = function () {
//        return that.active_sheet()['pending_nodes'];
//    };


    that.active_basic_changed = function ( value ) {
        that.active_group()['basic_changed'] = value;
    };

    that.active_filtered = function () {
        return that.active_sheet()['filtered'];
    };


    // active sheet getter / setter
    that.active_sheet = function ( value ) {
        var active_grp = that.active_group();

        if( arguments.length === 0 ) {
            return active_grp['sheets'][active_grp['active_sheet_number']];
        }

        active_grp['active_sheet_number'] = value;
    };

    // active group getter / setter
    that.active_group = function ( value ) {
        if( arguments.length === 0 ) {
            return groups[ active_group_number ];
        }

        active_group_number = value;
    };


    that.add_data = function ( new_data ) {
        var rows = that.active_rows();

        new_data
            .map( function ( row ) {
                return {
                    data: row,
                    state: { open: false, selected: false }
                };
            })
            .forEach( function ( e ) {
                rows.push( e );
            });
    };

    that.add_new_sheet = function ( sheet ) {
        var active_grp = that.active_group();
        var next_sheet_number = that.next_sheet_number() ;

        active_grp['sheets'].push( sheet );
        that.active_sheet_index( next_sheet_number );
    };

    that.get_all_groups = function () {
        return groups;
    };

    // check if column exists in active_sheet
    that.is_column_in_active_sheet = function( key ){
        var i;
        var cols = that.active_columns();

        for( i = 0; i < cols.length; i += 1 ) {
            if( cols[i]['key'] === key ){
                    return true;
            }
        }
        return false;
    };

    that.get_group = function ( group ) {
        return groups[group];
    };

    that.get_sheet = function ( group, sheet ) {
        return groups[group]['sheets'][sheet];
    };

    that.get_sheets = function ( group_num ) {
        var sheets = groups[group_num]['sheets'] 
        return sheets;
    };
    
    that.remove_active_group = function() {
        if (groups.length === 1){
            return false;
        } 
        groups.splice ( that.active_group_index(), 1 );  
        if (that.active_group_index() !== 0){
            active_group_number = that.active_group_index()-1;   
        }
        return true;
    }

    that.remove_active_sheet = function () {
        var active_grp = that.active_group();
        var active_group_sheets = active_grp['sheets'];
        var active_sheet_num = that.active_sheet_index();
        if (groups.length === 1 && active_group_sheets.length === 1 ){
            return false; 
        }
        active_group_sheets.splice(active_sheet_num, 1 );    
        if (active_group_sheets.length === 0 ){
            that.remove_active_group();
        }else if (active_sheet_num !== 0 ) {
                active_grp['active_sheet_number'] = active_sheet_num - 1;
            }            
        return true;
    };
    
    that.next_sheet_name = function () {    
        var next_num=1;
        var sheet_name;
        that.active_group()['sheets'].forEach( function (sheet, sheet_num){
            if ( sheet['name'].indexOf('Arkusz') !== -1 ) {
                sheet_name = sheet['name'].split(' ');
                if ( sheet_name[1] >= next_num ){
                    next_num = sheet_name[1];
                    next_num++;
                   }; 
            }
        });
         return 'Arkusz ' + next_num; 
        
    };
        
    
    // TODO not needed yet    
    that.set_active_sheet_name = function (sheet_name) {
        that.active_sheet()['name'] = sheet_name;
    };

// P R I V A T E   I N T E R F A C E
    // data about available datasets and their perspectives
    var meta_data = [];

    // a store for a sheets tab in the GUI
    var groups = [];
    var active_group_number = null;



    // returns group id if it exists or -1 if there is no such a group
    function find_group( data ) {
        var i;

        for( i = 0; i < groups.length; i += 1 ) {
            if( data['dataset'] === groups[i]['dataset'] &&
                data['perspective'] === groups[i]['perspective'] &&
                data['issue'] === groups[i]['issue'] ) {

                return i;
            }
        }

        return -1;
    }



// O B J E C T   F A C T O R I E S
    // a single sheet
    function sheet( data, basic ) {
        var cols = that.active_group()['columns'].filter( function ( e ) {
                    return e['basic'] === true;
                });
        var rows = data['rows'].map( function ( row ) {
                                    return {
                                        data: row,
                                        state: { open: false, selected: false }
                                    };
                                });

        // if total present in collection move it to special position
        if( rows[ rows.length - 1 ]['data']['type'] === 'Total' ) {
            rows['total'] = rows.pop();
        }

        if( !!basic ) {
            return rows;
        }

        return {
            'columns': cols,
            'rows': rows,
            'name': data['name'],
            'filtered': false
//          'pending_nodes': []
        };
    }


    // list of all sheets of the same dataset/perspective/issue
    function group( data ) {
        return {
            'dataset': data['dataset'],
            'perspective': data['perspective'],
            'issue': data['issue'],
            'columns': data['columns'],
            'active_sheet_number': 0,
            'sheets': [],
            'basic_rows': null,
            'basic_changed': false
        };
    }

    return that;

}) ();
