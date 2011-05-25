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
        Assert.assert( meta_data.length === 0, 
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
            active_group( found );
            return false;
        }
 
        groups.push( new_group( data ));
        active_group( groups.length - 1 );
                
        return true;
    };
    
    
    that.dataset = function () {
        return active_group()['dataset'];
    };


    that.perspective = function () {
        return active_group()['perspective'];
    };

    
    that.issue = function () {
        return active_group()['issue'];
    };


    that.init_basic_sheet = function ( data ) {
        var active_grp = active_group();
        
        active_grp['basic_sheet'] = new_sheet( data );
        active_grp['sheets'].push( new_sheet( data ) );         
    };


    that.active_columns = function () {
        return active_sheet()['columns'];
    };


    that.active_sheet_index = function () {
        return active_group()['active_sheet_number'];
    };

    that.active_rows = function () {
        return active_sheet()['rows'];
    };
    

    that.active_pending_nodes = function () {
        return active_sheet()['pending_nodes'];
    };
    
    
    that.active_basic_changed = function ( value ) {
        active_group()['basic_changed'] = value;        
    };

// P R I V A T E   I N T E R F A C E
    // data about available datasets and their perspectives
    var meta_data = [];
    
    // a store for a sheets tab in the GUI
    var groups = [];
    var active_group_number = null;

    // active group getter / setter
    var active_group = function ( value ) {
        if( arguments.length === 0 ) {
            return groups[ active_group_number ];
        }
        
        active_group_number = value;
    };

    // active sheet getter / setter
    var active_sheet = function ( value ) {
        var active_grp = active_group();
        
        if( arguments.length === 0 ) {
            return active_grp['sheets'][active_grp['active_sheet_number']];
        }
        
        active_grp['active_sheet_number'] = value;
    };

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






//    that.dataset = function ( value ) { 
//        if( arguments === 0 ) {
//            return active_group()['dataset'];
//        }
//        
//        active_group()['dataset'] = value;
//    };
//     
//      
//    that.perspective = function ( value ) { 
//        if( arguments === 0 ) {
//            return active_group()['perspecive'];
//        }
//        
//        active_group()['perspective'] = value;
//    };        


//    that.issue = function ( value ) { 
//        if( arguments === 0 ) {
//            return active_group()['issue'];
//        }
//        
//        return active_group()['issue'];
//    };        


//    that.active_group_number = function ( value ) { 
//        if( arguments === 0 ) {
//            return group_container['active_group_list'];
//        }
//        
//        group_container['active_group_list'] = value;
//    };        


//    that.active_sheet_number = function ( value ) { 
//        if( arguments === 0 ) {
//            return groups['active_sheet_number'];
//        }
//        
//        sheets_group['active_sheet_number'] = value;
//    };


//    that.active_sheet = function () {
//        return active_group()[ 'active_sheet_number' ];
//    };






/*
    // setters/getters: sheet_list
    that.columns = function ( value ) {
        if( arguments === 0 ) {
            return sheet_data['columns'];
        }
        
        sheet_data['columns'] = value;
    };
    
        
    that.rows = function ( value ) {
        if( arguments === 0 ) {
            return sheet_data['rows'];
        }
        
        sheet_data['rows'] = value;
    };




    that.pending_nodes = function ( value ) {
        if( arguments === 0 ) {
            return sheet_data['pending_nodes'];
        }
        
        sheet_data['pending_nodes'] = value;
    };
    

    that.sheet_name = function ( value ) {
        if( arguments === 0 ) {
            return sheet_data['name'];
        }
        
        sheet_data['name'] = value;
    };
    
        
    // setters/getters: sheet_list
    that.active_sheet_number = function ( value ) {
        if( arguments === 0 ) {
            return sheet_list['active_sheet_number'];
        }
        
        sheet_list['active_sheet_number'] = value;
        sheet_data = sheet_list['sheets'][ value ];
    };
    
    
    that.basic_sheet = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_list['basic_sheet'];
        }
        
        sheet_list['basic_sheet'] = value;
    };

    
    that.basic_pure_state = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_list['basic_pure_state'];
        }
        
        sheet_list['basic_pure_state'] = value;
    };
     
     
    that.sheets_number = function () {
        return sheet_list['sheets'].length;
    }; 
    
    
    that.init_basic_sheet = function () {
        
        $.extend( true, that.basic_sheet(), sheet_data );
        
        that.basic_pure_state( true );
    };
    
    
    that.active_sheet = function () {
        return sheet_list['sheets'][ that.active_sheet_number ];
    };




*/







