// 
//    Public interface for storing sheets data
// 

var _store = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};
    
    that.add_new_sheet = function ( new_sheet ) {
        var max_sheet_number = _store.sheets_number();
        sheet_list['sheets'][ max_sheet_number ] = new_sheet;
    };
    
    that.clean_basic_sheet = function ( ) {
        sheet_list[0] = {};
        $.extend( true, sheet_list['sheets'][0], sheet_list['basic_sheet'] );
        that.basic_pure_state( true );
    };

    // setters/getters: sheet_list
    that.colums = function ( value ) {
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


    that.dataset = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['dataset'];
        }
        
        sheet_data['dataset'] = dataset;
    };
     
      
    that.perspective = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['perspective'];
        }
        
        sheet_data['perspective'] = value;
    };        


    that.issue = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['issue'];
        }
        
        sheet_data['issue'] = value;
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


    // P R I V A T E   D A T A 
    
    // current object shown in the table
    var sheet_data = {
        'dataset': null,
        'perspective': null,
        'issue': null,

        'columns': null,
        'rows': null,  
        'pending_nodes': [],  

        'name': ''
    };
    
    // list of all sheets of the table
    var sheet_list = {
        'active_sheet_number': 0,
        'sheets': [ sheet_data ],
        'basic_sheet': {},
        'basic_pure_state': true
    };


    // data about available datasets and their perspectives
    var meta_data = [];

    return that;

}) ();





















