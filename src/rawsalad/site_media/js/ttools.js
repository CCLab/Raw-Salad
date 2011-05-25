    var sort = function ( table_data_object, sett ) {
        var id = "idef";
        
        var new_table_data_object = {};
        
        Utilities.prepare_sorting_setting( sett, id );
        Utilities.sort( table_data_object[ 'rows' ], sett );
    };


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

            sort( tab_data_object, settings );
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object );
            
            $(this).hide();
            
            return false;
        });


    function add_sort_key( ) {
        var i, key;
        var perspective = tab_data_object['perspective']['columns'];
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


    function create_new_sheet( data_object, filtered_sheet ) {
        var html = [];
        var new_sheet_nr = sheet_list["sheets"].length;
        var new_sheet = { };
        
        $.extend( true, new_sheet, data_object );
        new_sheet["col_nr"] = data_object["col_nr"];
        new_sheet["per_nr"] = data_object["per_nr"];
        new_sheet["name"] = "Arkusz " + new_sheet_nr.toString();
        sheet_list["sheets"].push( new_sheet );
        
        if ( sheet_list["active_sheet"] === 0 && !sheet_list["basic_pure"] ) {
            sheet_list["sheets"][0] = {};
            $.extend( true, sheet_list["sheets"][0], sheet_list["basic_sheet"] );
            sheet_list["basic_pure"] = true;
        }
        
        sheet_list["active_sheet"] = new_sheet_nr;
        
        html.push('<div id="snap-' + new_sheet_nr.toString() + '" class="snapshot active">');
        html.push(new_sheet["name"]);
        html.push('</div>');
        html.push('<div id="save-snapshot">');
        html.push('Zapisz arkusz');
        html.push('</div>');
        
        $('#save-snapshot').remove();
        $('#snapshots').append( $( html.join('') ));
        $('#snapshots')
            .find('#snap-' + new_sheet_nr.toString())
            .each( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');
            })
            .click( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');
                if ( sheet_list["active_sheet"] !== new_sheet_nr ) {
                    sheet_list["active_sheet"] = new_sheet_nr;
                    tab_data_object = sheet_list["sheets"][new_sheet_nr];
                    $('#table').empty();
                    generate_header( tab_data_object );
                    generate_table_body( tab_data_object, filtered_sheet );
                }                
            });
        $('#save-snapshot')
            .click( function () {
                create_new_sheet( tab_data_object );
            });
        
        return new_sheet_nr;
    }

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
            var new_data_object, new_sheet_nr;
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
                
                type = filter( function ( e ) {
                    return e['key'] === column;
                }, tab_data_object['perspective']['columns'] )[0]['type'];
                
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
            
            new_data_object = {};
            $.extend( true, new_data_object, tab_data_object );
            new_data_object['rows'] = Utilities.filter( tab_data_object['rows'], mask );
            new_sheet_nr = create_new_sheet( new_data_object, true );
            
            tab_data_object = sheet_list["sheets"][new_sheet_nr];
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object, true );

            $(this).hide();
                        
            return false;
       });
        



 
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
    
    $('#save-snapshot')
        .click( function () {
            create_new_sheet( tab_data_object );
        });
        
    $('#basic-snapshot')
        .click( function () {
            $('.snapshot').removeClass('active');
            $(this).addClass('active');

            if ( sheet_list["active_sheet"] !== 0 ) {
                sheet_list["active_sheet"] = 0;
                tab_data_object = sheet_list["sheets"][0];
                
                $('#table').empty();
                generate_header( tab_data_object );
                generate_table_body( tab_data_object );
            }
        });


