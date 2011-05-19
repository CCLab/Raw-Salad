// 
//    Set of functions responsible for ajax communication
// 

var _db = (function () {

    var that = {};

    // downloads requested nodes, appends them to object with other nodes
    // and adds html code for new nodes
    that.download_node = function ( table_data, parent_id ) {
        // ajax call data object
        var download_data = {
            action: 'get_node',
            dataset: table_data['col_nr'], 
            perspective: table_data['per_nr'],
            issue: table_data['issue'],
            parent: parent_id,
            // >> what is it for?!
            add_columns: []
        };
        
        $.ajax({
            data: download_data,
            dataType: 'json',
            success: function( received_data ) {                        
                var i;            
                var data = table_data.rows;
                
                for ( i = 0; i < received_data.length; i += 1 ) {
                    data.push( received_data[ i ] );
                }
                
                // add recieved data to the table and render html
                _table.add_node( table_data, parent_id );
                that.remove_pending_node( table_data, parent_id );
                
                // if it was a basic sheet sign it changed
                if ( _store.active_sheet_number() === 0 ) {
                    _store.basic_pure_state( false );
                }
            }
        });
    };
    
    
    // adds a node id to list of nodes waiting to be downloaded
    // and inserted in the table
    that.add_pending_node = function ( table_data, id ) {
        var i;
        var pending_nodes = table_data[ 'pending_nodes' ];
        
        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                return false;
            }
        }
        pending_nodes.push( id );

        return true;
    };
    
    
    // removes a node id from the list of nodes waiting to be downloaded
    that.remove_pending_node = function ( table_data, id ) {
        var i;
        var pending_nodes = table_data[ 'pending_nodes' ];
        
        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                pending_nodes.splice( i, 1 );
                return;
            }
        }
    };


    // arms the perspectives buttons
    that.arm_perspective = function ( object ) {
        // ajax call data object
        var init_data_info
    
        // store chosen perspective and issue
        _store.perspective( object.attr( 'data-perspective' ));
        _store.issue( object.attr( 'data-issue' ));                
        
        init_data_info = {
            "action": "get_init_data",
            "dataset": _store.dataset(),
            "perspective": _store.perspective(),
            "issue": _store.issue()
        };

        $.ajax({
            data: init_data_info,
            dataType: "json",
            success: function( received_data ) {
            
                // store received data
                _store.columns( received_data.perspective );
                _store.rows( received_data.rows );
                _store.sheet_name( "Arkusz " + _store.sheets_number() );
                
                _store.init_basic_sheet();

                _table.init_table()
                _gui.close_choose_panel();
            }
        });
    });

    return that;
})();       
