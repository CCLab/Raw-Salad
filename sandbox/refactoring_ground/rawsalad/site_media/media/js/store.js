var _store = (function () {

    // P R I V A T E   D A T A 
    
    // current object shown in the table
    var sheet_data = {
        'dataset': null,
        'perspective': null,
        'issue': null,

        'columns': null,
        'rows': null,    

        'name': ''
    };
    
    // list of all sheets of the table
    var sheet_list = {
        'active_sheet_number': 0,
        'sheets': [{}],
        'basic_sheet': {},
        'basic_pure_state': true
    };


    //  P U B L I C   I N T E R F A C E
    var that = {};


    // setters/getters: sheet_list
    that.colums = function ( value ) {
        if( arguments === 0 ) {
            return sheet['columns'];
        }
        
        sheet['columns'] = value;
    }
    
        
    that.rows = function ( value ) {
        if( arguments === 0 ) {
            return sheet['rows'];
        }
        
        sheet['rows'] = value;
    }


    that.dataset = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['dataset'];
        }
        
        sheet_data['dataset'] = dataset;
    }
     
      
    that.perspective = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['perspective'];
        }
        
        sheet_data['perspective'] = value;
    }        


    that.issue = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_data['issue'];
        }
        
        sheet_data['issue'] = value;
    }        

    that.sheet_name = function ( value ) {
        if( arguments === 0 ) {
            return sheet_data['name'];
        }
        
        sheet_data['name'] = value;
    }
    
        
    // setters/getters: sheet_list
    that.active_sheet_number = function ( value ) {
        if( arguments === 0 ) {
            return sheet_list['active_sheet_number'];
        }
        
        sheet_list['active_sheet_number'] = value;
    }
    
    
    that.basic_sheet = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_list['basic_sheet'];
        }
        
        sheet_list['basic_sheet'] = value;
    }

    
    that.basic_pure_state = function ( value ) { 
        if( arguments === 0 ) {
            return sheet_list['basic_pure_state'];
        }
        
        sheet_list['basic_pure_state'] = value;
    }
     
     
    that.sheets_number = function () {
        return sheet_list['shhets'].length;
    } 
    
    
    that.init_basic_sheet = function () {
        
        $.extend( true, that.basic_sheet(), sheet_data );
        
        that.basic_pure_state( true );
    }

    return that;

}) ();





















