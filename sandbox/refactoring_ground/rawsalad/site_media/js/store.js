// 
//    Public interface for storing sheets data
// 

var _store = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};

    // meta_data setter/getter
    that.meta_data = function ( value ) {
        if( arguments === 0 ) {
            return meta_data;
        }
        
        meta_data( value );    
    };
    

    that.dataset = function ( value ) { 
        if( arguments === 0 ) {
            return active_group()['dataset'];
        }
        
        active_group()['dataset'] = value;
    };
     
      
    that.perspective = function ( value ) { 
        if( arguments === 0 ) {
            return active_group()['perspecive'];
        }
        
        active_group()['perspective'] = value;
    };        


    that.issue = function ( value ) { 
        if( arguments === 0 ) {
            return active_group()['issue'];
        }
        
        return active_group()['issue'];
    };        


    that.active_group_number = function ( value ) { 
        if( arguments === 0 ) {
            return group_container['active_group_list'];
        }
        
        group_container['active_group_list'] = value;
    };        


    that.active_sheet_number = function ( value ) { 
        if( arguments === 0 ) {
            return groups['active_sheet_number'];
        }
        
        sheets_group['active_sheet_number'] = value;
    };


    that.active_sheet = function () {
        return active_group()[ 'active_sheet_number' ];
    };



    // P R I V A T E   D A T A 
    var groups_container = {
        'active_group_number': 0,
        'groups': [ sheet_list() ],
    };
    
    // data about available datasets and their perspectives
    var meta_data = [];


    var active_group = function () {
        return groups_conainer[ 'groups'][ that.active_group_number() ];
    }


    var sheet_data = function () {  
        return {
            'columns': null,
            'rows': null,  
            'pending_nodes': [],  

            'name': ''
        };
    };
    
    // list of all sheets of the table
    var sheets_group = function () {
        return {
            'dataset': null,
            'perspective': null,
            'issue': null,
        
            'active_sheet_number': 0,
            'sheets': [ sheet_data() ],
            'basic_sheet': {},
            'basic_pure_state': true
        };
    };


    return that;

}) ();













/*
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







