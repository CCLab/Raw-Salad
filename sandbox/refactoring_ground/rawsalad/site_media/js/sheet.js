// 
//    Public interface for creating and handling sheet
// 

var _sheet = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};

    that.create_new_sheet( sheet_data, sheet_name, filtered_sheet ) {
        var new_sheet_nr = _store.sheets_number();
        var new_sheet = { };
        
        $.extend( true, new_sheet, sheet_data );
        new_sheet["dataset"] = sheet_data["dataset"];
        new_sheet["perspective"] = sheet_data["perspective"];
        new_sheet["name"] = sheet_name;
        
        add_new_sheet( new_sheet );
        
        if ( _store.active_sheet_number() === 0 && !_store.basic_sheet_pure() ) {
            clean_basic_sheet();
        }
        
        _store.active_sheet_number = new_sheet_nr;
        
        _gui.create_sheet_tab( sheet_name, new_sheet_nr, filtered_sheet );
        
        return new_sheet_nr;
    }
    
    
    that.change_active_sheet( sheet_nr ) {
        if ( _store.active_sheet_nr() !== sheet_nr ) {
            _store.active_sheet_nr( sheet_nr );
            _table.clean_table();
            _table.init_table( filtered_sheet );
        }
    }
    
    // P R I V A T E  I N T E R F A C E
    
    var add_new_sheet = function ( new_sheet ) {
        var active_sheet_number;
        var max_sheet_number;
        
        active_sheet_number = _store.active_sheet_number();
        max_sheet_number = _store.sheets_number();
        
        _store.active_sheet_number( max_sheet_number );
        
        _store.dataset( new_sheet['dataset'] );
        _store.perspective( new_sheet['perspective'] );
        _store.issue( new_sheet['issue'] );
        _store.columns( new_sheet['columns'] );
        _store.rows( new_sheet['rows'] );
        _store.pending_nodes( [] );
        _store.name( new_sheet['name'] );
        
        _store.active_sheet_number( active_sheet_number );
    };


    var clean_basic_sheet = function ( ) {
        var active_sheet_number;
        var basic_sheet;
        var basic_sheet_rows = [];
        
        active_sheet_number = _store.active_sheet_number();
        basic_sheet = _store.basic_sheet();
        $.extend( true, basic_sheet_rows, basic_sheet['rows'] );
        
        _store.active_sheet_number(0);
        _store.rows( basic_sheet_rows );
        _store.basic_pure_state( true );
        
        _store.active_sheet_number( active_sheet_number );
    };

    return that;

}) ();
