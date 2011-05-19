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
        new_sheet["col_nr"] = sheet_data["col_nr"];
        new_sheet["per_nr"] = sheet_data["per_nr"];
        new_sheet["name"] = sheet_name;
        
        _store.add_new_sheet( new_sheet );
        
        if ( _store.active_sheet_number() === 0 && !_store.basic_sheet_pure() ) {
            _store.clean_basic_sheet();
        }
        
        _store.active_sheet_number = new_sheet_nr;
        
        gui.create_sheet_tab( sheet_name, new_sheet_nr, filtered_sheet );
        
        return new_sheet_nr;
    }
    
    that.change_active_sheet( sheet_nr ) {
        if ( _store.active_sheet_nr() !== sheet_nr ) {
            _store.active_sheet_nr( sheet_nr );
            _table.clean_table();
            _table.init_table( filtered_sheet );
        }
    }
    
    

    return that;

}) ();
