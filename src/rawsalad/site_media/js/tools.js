// Copyright (c) 2011, Centrum Cyfrowe
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//   * Redistributions of source code must retain the above copyright notice,
//     this list of conditions and the following disclaimer.
//   * Redistributions in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation
//     and/or other materials provided with the distribution.
//   * Neither the name of the Centrum Cyfrowe nor the names of its contributors
//     may be used to endorse or promote products derived from this software
//     without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
// GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
// OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

var _tools = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    // TODO refactor this !!!!
    that.sort = function ( data, sett ) {
        var id = "idef";
        // TODO what is it for?!
        var new_table_data_object = {};
        _algorithms.prepare_sorting_setting( sett, id );
        _algorithms.sort( data, sett );
    };

    that.prepare_tools = function () {
        prepare_sorting_interface();
        prepare_filtering_interface();
//	prepare_manage_columns_interface();
        prepare_snapshot_interface();
    };
    
    that.get_full_parents = function ( id ) {
        var par_ids = [];
        
        
    };

    return that;

//  P R I V A T E   I N T E R F A C E

    function add_sort_key() {
        var i, key;
        var html = [];
        var schema = _store.basic_schema();
        var columns = schema
                        .filter( function ( e ) {
                            return e['processable'];
                        })
                        .map( function ( e ) {
                            return {
                                name: e['key'],
                                label: e['label']
                            };
                        });

        key = $('#sort-form > div').length;

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

        $('#sort-form').append( $( html.join('') ));

        if( key === 0 ) {
            $('#add-sort-key').click( function () {
                add_sort_key();
            });
        }
    }
    
    function add_manage_checkbox()  {
	//funkcja dodająca checkboxy do PopUp-a
    }



    function add_filter_key() {
        var i, key;
        var html = [];
        var filter_part;
        var selected_column;
        var type;
        var schema = _store.basic_schema();        
        var columns = schema
                        .filter( function ( e ) {
                            return e['processable'];
                        })
                        .map( function ( e ) {
                            return {
                                name: e['key'],
                                label: e['label']
                            };
                        });

        key = $('#filter-form > div').length;
        
        columns.unshift({
            name: 'null',
            label: 'Wybierz kolumnę'
        });
        
        html.push( '<div id="filter-key-', key, '">' );
        
        html.push( '<select id="filter-', key, '-columns"' );
        html.push( ' name="columns">');
        for ( i = 0; i < columns.length; i += 1 ) {
            html.push( '<option value="', columns[i]['name']);
            html.push( '" class="filter-', key, '" >');
            html.push( columns[i]['label'], '</option>' );
        }
        html.push( '</select>' );
        
        html.push( '<select id="filter-', key, '-operations"' );
        html.push( ' name="null-operation" disabled="true">' );
        // not needed because column has not been selected yet
        
        html.push( '</select>' );
        
        if ( key === 0 ) {
            html.push( '<div id="add-filter-key">+</div>' );
            html.push( '<input type="submit" value="Filtruj" />' );
        }
        
        html.push( '</div>' );
        $('#filter-form').append( $( html.join('') ) );
        
        if( key === 0 ) {
            //TODO create CSS class for add-filter-key !!!!!!!!!!!
            $('#add-filter-key').click( function () {
                add_filter_key();
            });
        }
        
        filter_part = $('#filter-' + key + '-columns');
        filter_part.change( function() {
            selected_column = $(this).val();
            
            $('#filter-' + key + '-query').remove();
            
            for ( i = 0; i < schema.length; i += 1 ) {
                if ( schema[i]['key'] === selected_column ) {
                    type = schema[i]['type'];
                    
                    $('#filter-' + key + '-operations').remove();
                    
                    html = [ '<select id="filter-', key, '-operations"' ];
                    if ( schema[i]['type'] === 'number' ) {
                        html.push( ' name="number-operation">' );
                        html.push( '<option value="null" class="filter-', key, '" selected>Wybierz operację</option>' );
                        html.push( '<option value="gt" class="filter-', key, '">></option>' );
                        html.push( '<option value="eq" class="filter-', key, '">=</option>' );
                        html.push( '<option value="lt" class="filter-', key, '"><</option>' );
                    } else {
                        html.push( ' name="string-operation">' );
                        html.push( '<option value="null" class="filter-', key, '" selected>Wybierz operację</option>' );
                        html.push( '<option value="cnt" class="filter-', key, '">Zawiera</option>' );
                        html.push( '<option value="st" class="filter-', key, '">Zaczyna się od</option>' );
                        html.push( '<option value="ncnt" class="filter-', key, '">Nie zawiera</option>' );
                        html.push( '<option value="nst" class="filter-', key, '">Nie zaczyna się od</option>' );
                    }
                    html.push( '</select>' );
                    
                    html.push( '<input type="text" name="query" id="filter-', key, '-query" />' );
                    
                    $( html.join('') ).insertAfter( $('#filter-' + key + '-columns') );
                    
                    break;
                }
            }
        });
    }
        
    function prepare_sorting_interface() {

        $('#sort-button')
            .click( function () {
                $('#filter-form').hide();
                $('#manage-columns-form').hide();
                $('#sort-form').html('').toggle();
                add_sort_key();
            });

        $('#sort-form')
            .submit( function () {
            
//                _utils.create_preloader('Sortowanie');

                var column, order;
                var settings = [];
                var i, len = $('#sort-form select').length;

                for( i = 0; i < len; i += 1 ) {
                    column = $( '.key-'+ i +' option:selected' ).val();
                    // TODO what does this condition mean?!
                    if( column === "null" ) {
                        if( i === 1 ) {
                            $(this).hide();
                            return false;
                        }
                        else {
                            break;
                        }
                    }
                    order = parseInt( $('.key-'+ i +':radio:checked').val() );

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

                // TODO why false?!
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

    function prepare_filtering_interface() {

        $('#filter-button')
            .click( function () {
                $('#filter-form').html('').toggle();
                $('#manage-columns-form').hide();
                $('#sort-form').hide();
                add_filter_key();
            });

        $('#filter-form')
            .submit( function () {

                var column, operation, query;
                var mask = [];
                var i, len = $('#filter-form select').length / 2;
                var tmp, type;
                var new_sheet;
                for( i = 0; i < len; ++i ) {
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

                    type = _store.active_columns().filter( function ( e ) {
                        return e['key'] === column;
                    })[0]['type'];

                    operation = $('#filter-'+i+'-operations option:selected').val();;
                    query = $('#filter-'+i+'-query').val();

                    tmp = parseInt( query, 10 );
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
                //new_sheet['filtered'] = true;
                   
                _sheet.create_new_sheet( new_sheet, "Arkusz", true );

                _table.clean_table();
                _table.init_table( true );

                $(this).hide();

                return false;
           });
    };

    function 	prepare_manage_columns_interface(){

        $('#manage-columns-form')
            .click( function () {
                $('#filter-form').hide();
                $('#sort-button').hide();
                $('#sort-form').html('').toggle();
                add_manage_checkbox();
            });

        $('#manage-columns-form')
            .submit( function () {
		// Tutaj dodanie kontrolek wedle tego co mam w tabela txt

        });   
    };

    function prepare_snapshot_interface() {

        $('#save-snapshot')
            .click( function () {
                _sheet.create_new_sheet( _store.active_sheet(), "Arkusz" );
            });
    }

}) ();





