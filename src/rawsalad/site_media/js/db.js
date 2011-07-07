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
                remove_pending_node( parent_id );

                // if it was a basic sheet sign it changed
                if ( _store.active_sheet_index() === 0 ) {
                    _store.active_basic_changed( true );
                }
            }
        });
    };


    // adds a node id to list of nodes waiting to be downloaded
    // and inserted in the table
    that.add_pending_node = function ( id ) {
        var i;
        var pending_nodes = _store.active_pending_nodes();

        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                return false;
            }
        }
        pending_nodes.push( id );

        return true;
    };

    return that;


//  P R I V A T E   I N T E R F A C E

    // removes a node id from the list of nodes waiting to be downloaded
    function remove_pending_node( id ) {
        var i;
        var pending_nodes = _store.active_pending_nodes();

        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                pending_nodes.splice( i, 1 );
                return;
            }
        }
    };

})();
