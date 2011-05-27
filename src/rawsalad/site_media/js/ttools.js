//
//    Public interface for table tools
//

var _ttools = (function () {

//  P U B L I C   I N T E R F A C E

    var that = {};
    
    that.sort = function ( data, sett ) {
        var id = "idef";
        
        var new_table_data_object = {};
        
        _algorithms.prepare_sorting_setting( sett, id );
        _algorithms.sort( data, sett );
    };
    
    that.prepare_table_interface = function () {
        prepare_sorting_interface();
        prepare_filtering_interface();
        prepare_snapshot_interface();
    };
    
//  P R I V A T E   I N T E R F A C E
    
    var add_sort_key = function() {
        var i, key;
        var perspective = _store.active_columns();
        var columns = [];
        var html = [];

        key = $('#sort-form > div').length;

        for( i = 0; i < perspective.length; ++i ) {
            if( perspective[i]['basic'] === true && 
                perspective[i]['processable'] === true ) {
                columns.push( 
                    {
                        name: perspective[i]['key'],
                        label: perspective[i]['label']
                    }
                );
            }
        }

        if( key === 2 ) {
            $('#add-sort-key' ).remove();
        }

        html.push( '<div id="key-', key, '">' );
        // columns select list
        html.push( '<select name="columns" class="key-', key, '">' );
        html.push( '<option value="null" class="key-', key, '" selected>' );
        html.push( 'Wybierz kolumnę</option>' );
        
        // TODO don't include already selected colmuns
        for( i = 0; i < columns.length; ++i ) {
            html.push( '<option value="', columns[i]['name'], '" class="key-', key, '">' );
            html.push( columns[i]['label'], '</option>' );
        }
        
        html.push( '</select>' );
        // ascending/descending radio buttons
        html.push( 'Rosnąco <input class="radio key-', key, '" type="radio" ' );
        html.push( 'name="key-', key, '-order" value="-1" checked />' );
        html.push( 'Malejąco <input class="radio key-', key, '" type="radio" ' );
        html.push( 'name="key-', key, '-order" value="1" />' );

        if( key === 0 ) {
            html.push( '<div id="add-sort-key">+</div>' );
            html.push( '<input type="submit" value="Sortuj" />' );
        }
        html.push( '</div>' );

        $('#sort-form').append( $(html.join('')) );

        if( key === 0 ) {
            $('#add-sort-key').click( function () {
                add_sort_key();   
            });
        }
    }
    
    var prepare_sorting_interface = function() {
    
        $('#sort-button')
            .click( function () {
                $('#filter-form').hide();
                $('#sort-form').html('').toggle();
                add_sort_key();
            });
        
        $('#sort-form')
            .submit( function () {

                var column, order;
                var settings = [];
                var i, len = $('#sort-form select').length;
                
                for( i = 0; i < len; ++i ) {
                    column = $('.key-'+i+' option:selected').val();
                    if( column === "null" ) {
                        if( i === 1 ) {
                            $(this).hide();
                            return false;
                        }
                        else {
                            break;
                        }
                    }
                    order = parseInt($('.key-'+i+':radio:checked').val());                 

                    settings.push(
                        {
                            "pref": order,
                            "name": column
                        }
                    );
                }

                that.sort( _store.active_rows(), settings );
                
                _table.clean_table();
                _table.init_table();
                
                $(this).hide();
                
                return false;
            });
            
        var i;
        for( i = 1; i <= $('#sort-form select').length; ++i ) {
            if( i > 1 ) {
                $('#key-'+i).hide();
            }

            (function (i) {
                $('#sort-form select.key-'+i).change( function () {    
                    if( $('.key-'+i+' option:selected').val() !== "null" ) {
                        $('#key-'+(i+1)).show();
                    }
                });
            })(i);
        }
    };
    
    var prepare_filtering_interface = function() {
    
        $('#filter-button')
            .click( function () {
                $('#filter-form').toggle(); 
                $('#sort-form').hide();               
            });

        $('#filter-form')
            .submit( function () {

                var column, operation, query;
                var mask = [];
                var i, len = $('#filter-form select').length / 2;
                var tmp, type;
                var new_sheet;
                for( i = 1; i < len; ++i ) {
                    column = $('#filter-'+i+'-columns option:selected').val();
                    if( column === "null" ) {
                        if( i === 1 ) {
                            $(this).hide();
                            return false;
                        }
                        else {
                            break;
                        }
                    }                

                    type = _utils.filter( function ( e ) {
                        return e['key'] === column;
                    }, _store.active_columns() )[0]['type'];
                    
                    operation = $('#filter-'+i+'-operations option:selected').val();;
                    query = $('#filter-'+i+'-query').val();

                    tmp = parseInt( query, 10 ) / 1000;
                    // if the column if numeric - check if the query is so
                    if( type === 'number' ) {
                        // crazy way to check if tmp is a number!
                        if( !!tmp === true || tmp === 0 ) {
                            query = tmp;
                        }
                        else {
                            // characters for numeric column -- do nothing & quit
                            $(this).hide();            
                            return false;
                        }
                    }
                    
                    mask.push(
                        {
                           name: column, 
                           pref: operation, 
                           value: query
                        }
                    );
                }
                
                new_sheet = {};
                $.extend( true, new_sheet, _store.active_sheet() );
                new_sheet['rows'] = _algorithms.filter( new_sheet['rows'], mask );
                
                _sheet.create_new_sheet( new_sheet, "arkusz", true );
                
                _table.clean_table();
                _table.init_table( true );

                $(this).hide();
                            
                return false;
           });
    };
    
    var prepare_snapshot_interface = function() {
        
        $('#save-snapshot')
            .click( function () {
                _sheet.create_new_sheet( _store.active_sheet(), "arkusz" );
            });
            
        $('#basic-snapshot')
            .click( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');

                if ( _store.active_sheet_index() !== 0 ) {
                    _store.active_sheet(0);                    
                    _table.clean_table();
                    _table.generate_header();
                    _table.generate_table_body();
                }
            });
    }
    
    that.prepare_table_interface();
    
    return that;
    
}) ();

    
    


