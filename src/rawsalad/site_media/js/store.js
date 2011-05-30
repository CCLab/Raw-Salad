// 
//    Public interface for storing sheets data
// 

var _store = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    // meta_data setter/getter
    that.meta_data = function ( value ) {
        if( arguments.length === 0 ) {
            return meta_data;
        }
        
        // set it just once
        _assert.assert( meta_data.length === 0, 
                       "meta_data already assigned!!!" );

        // TODO >> it should come from db as a simple list 
        meta_data = value;    
    };
    
    
    // get metadata about available datasets 
    that.meta_datasets = function () {
        return meta_data;
    }
    
    
    // get metadata about perspectives available in a cerain dataset
    that.meta_perspectives = function ( dataset_id ) {
        return meta_data[ dataset_id ]['perspectives'];
    }    


    // creates a new group or sets an active group index to apropriate group
    that.create_new_group = function ( data ) {

        var found = find_group( data );

        if( found !== -1 ) {
            that.active_group( found );
            return false;
        }
 
        groups.push( new_group( data ));
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

        active_grp['basic_sheet'] = new_sheet( data );
        active_grp['sheets'].push( new_sheet( data ) );  
    };


    that.active_columns = function () {
        return that.active_sheet()['columns'];
    };


    that.active_sheet_index = function () {
        return that.active_group()['active_sheet_number'];
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
    

    that.active_pending_nodes = function () {
        return that.active_sheet()['pending_nodes'];
    };
    
    
    that.active_basic_changed = function ( value ) {
        that.active_group()['basic_changed'] = value;        
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


    that.add_new_sheet = function ( data ) {
        var active_grp = that.active_group();
        var next_sheet_number = that.next_sheet_number() ;
        
        active_grp['sheets'].push( new_sheet( data ) );
        that.active_sheet_index( next_sheet_number );
    };

// P R I V A T E   I N T E R F A C E
    // data about available datasets and their perspectives
    var meta_data = [];
    
    // a store for a sheets tab in the GUI
    var groups = [];
    var active_group_number = null;

    
    var find_group = function ( data ) {
        var i;
        
        for( i = 0; i < groups.length; i += 1 ) {
            if( data['dataset'] === groups[i]['dataset'] && 
                data['perspective'] === groups[i]['perspective'] && 
                data['issue'] === groups[i]['issue'] ) {
                
                return i;
            }
        }
        
        return -1;
    };
    

// O B J E C T   F A C T O R I E S
    // a single sheet
    var new_sheet = function ( data ) {  
        return {
            'columns': data['columns'],
            'rows': data['rows'],  
            'pending_nodes': [],  

            'name': data['name']
        };
    };
    
    // list of all sheets of the same dataset/perspective/issue
    var new_group = function ( data ) {
        return {
            'dataset': data['dataset'],
            'perspective': data['perspective'],
            'issue': data['issue'],
        
            'active_sheet_number': 0,
            'sheets': [],
            'basic_sheet': null,
            'basic_changed': false
        };
    };


    return that;

}) ();



