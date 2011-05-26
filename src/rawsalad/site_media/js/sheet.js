// 
//    Public interface for creating and handling sheet
// 

var _sheet = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};

    that.create_new_sheet = function ( sheet_data, sheet_name, filtered_sheet ) {
        var new_sheet_nr = _store.active_sheet_index();
        var new_sheet = { };
        
        $.extend( true, new_sheet, sheet_data );
        new_sheet["name"] = sheet_name;
        
        add_new_sheet( new_sheet );
        
        if ( _store.active_sheet_index() === 0 && _store.active_basic_changed() ) {
            clean_basic_sheet();
        }
        
        _store.active_sheet_index(new_sheet_nr);
        
        _gui.create_sheet_tab( sheet_name, new_sheet_nr, filtered_sheet );
        
        return new_sheet_nr;
    }
    
    
    that.change_active_sheet = function ( sheet_nr ) {
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
        
        active_sheet_number = _store.active_sheet_index();
        ////TODO : can't get max number of sheets in the group
        // temporary solution
        max_sheet_number = _store.active_sheet_index();
        
        _store.active_sheet_index( max_sheet_number );
        
        _store.dataset( new_sheet['dataset'] );
        _store.perspective( new_sheet['perspective'] );
        _store.issue( new_sheet['issue'] );
        _store.active_columns( new_sheet['columns'] );
        _store.active_rows( new_sheet['rows'] );
        _store.active_pending_nodes( [] );
        ////TODO : should sheet have a name? can't set
        //_store.name( new_sheet['name'] );
        
        _store.active_sheet_index( active_sheet_number );
    };


    var clean_basic_sheet = function () {
        var active_sheet_number;
        var basic_sheet;
        var basic_sheet_rows = [];
        
        active_sheet_number = _store.active_sheet_index();
        
        ////TODO : can't get basic_sheet
        //basic_sheet = _store.basic_sheet();
        //$.extend( true, basic_sheet_rows, basic_sheet['rows'] );
        
        _store.active_sheet_index(0);
        _store.acitve_sheet_rows( basic_sheet_rows );
        _store.active_basic_changed( false );
        
        _store.active_sheet_index( active_sheet_number );
    };

    return that;

}) ();
