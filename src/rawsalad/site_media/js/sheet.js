// 
//    Public interface for creating and handling sheet
// 

var _sheet = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};

    that.create_new_sheet = function ( sheet_data, sheet_name, filtered_sheet ) {
        var new_sheet_nr = _store.next_sheet_number();
        var group_nr = _store.active_group_index();
        var new_sheet = {};
        
        $.extend( true, new_sheet, sheet_data );
        new_sheet["name"] = sheet_name + new_sheet_nr;

        _store.add_new_sheet( new_sheet );

        _gui.create_sheet_tab({ 
            'name': new_sheet['name'], 
            'sheet_nr': new_sheet_nr,
            'group_nr': group_nr, 
            'filtered_sheet': filtered_sheet 
        });
        
        return new_sheet_nr;
    }
    
    
    that.change_active_sheet = function ( args ) {
        var sheet_nr = args.sheet_nr;
        var group_changed = args.group_changed;
        var filtered_sheet = args.filtered_sheet; // TODO: add filtered property
        
        if ( _store.active_sheet_index() !== sheet_nr || !!group_changed ) {
            _store.active_sheet( sheet_nr );
            _table.clean_table();
            _table.init_table( filtered_sheet );
        }
    }
    
    that.show_basic_sheet = function ( args )
    {
        var group_nr = args.group_nr;
        var group_changed = false;
        
        if ( !!group_nr || group_nr === 0 ) {
            if (_store.active_group_index() !== group_nr) {
                _store.active_group( group_nr );
                group_changed = true;
            }
        }
        
        that.change_active_sheet( {'sheet_nr': 0, 'group_changed': group_changed} );
    }
    
    // P R I V A T E  I N T E R F A C E



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
