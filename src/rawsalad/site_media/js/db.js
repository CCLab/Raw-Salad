// 
//    Set of functions responsible for ajax communication
// 

var _db = (function () {

    var that = {};

    // gets the top-level from db
    that.get_init_data = function () {
        // ajax call data object
        var init_data_info = {
            "action": "get_init_data",
            "dataset": _store.dataset(),
            "perspective": _store.perspective(),
            "issue": _store.issue()
        };

        $.ajax({
            data: init_data_info,
            dataType: "json",
            success: function( received_data ) {
                var data = {
                    columns: received_data.perspective,
                    rows: received_data.rows,
                    name: received_data.name
                };

                debugger;                
                _store.init_basic_sheet( data );
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
                var i;            
                var data = _store.active_rows();

                for ( i = 0; i < received_data.length; i += 1 ) {
                    data.push( received_data[ i ] );
                }
                
                // add recieved data to the table and render html
                _table.add_node( parent_id );
                that.remove_pending_node( parent_id );
                               
                // if it was a basic sheet sign it changed
                if ( _store.active_sheet_number() === 0 ) {
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
    
    
    // removes a node id from the list of nodes waiting to be downloaded
    that.remove_pending_node = function ( id ) {
        var i;
        var pending_nodes = _store.active_pending_nodes();        
        
        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                pending_nodes.splice( i, 1 );
                return;
            }
        }
    };
    
    return that;
})();       
