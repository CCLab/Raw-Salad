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
	prepare_manage_columns_interface();
        prepare_sorting_interface();
        prepare_filtering_interface();
        prepare_snapshot_interface();
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
        var i;
        var key;
        var html = [];
	var active_columns = _store.active_columns();
	var all_columns = _store.group_columns();
	
        
        for( i=0; i<all_columns.length; i+=1) {
            key = all_columns[i]['key'];
	    html.push ( '<input type="checkbox" name="colum-', key,'" ' );
            html.push ( ' value="column-',key,'" id="column-id-', key,'" ' );
	    if (_store.is_column_in_active_sheet(key)){
                html.push('checked ');
            }
            html.push('>');
            html.push('<label for="column-id-', key,'" >');
            html.push(all_columns[i]['label'],'</label>');
        }
        $('#manage-columns-form').append( $( html.join('') ));
	//TODO add checkboxes to manage columns popup
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
        
        if ( key === 2 ) {
            $('#add-sort-key' ).remove();
        }
        
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
        
        html.push( '</select>' );
        
        if ( key === 0 ) {
            html.push( '<div id="add-filter-key">+</div>' );
            html.push( '<input type="submit" value="Filtruj" />' );
        }
        
        html.push( '</div>' );
        $('#filter-form').append( $( html.join('') ) );
        
        if( key === 0 ) {
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
                var visible_form;
                if ( $('#sort-form > div').length > 0 ) {
                    $('#sort-form').slideUp( 400, function () {
                        $('#sort-form').html('').toggle();
                    });
                } else {
                    if ( $('#filter-form > div').length > 0 ) {
                        visible_form = $('#filter-form');
                    } else if ( $('#manage-columns-form > input').length > 0 ) {
                        visible_form = $('#manage-columns-form');
                    }
                    
                    if ( !!visible_form ) {
                        visible_form.slideUp( 400, function () {
                            visible_form.html('').toggle();
                            $('#sort-form').html('').toggle();
                            add_sort_key();
                            $('#sort-form').slideDown( 400 );
                        })
                    } else {
                        $('#sort-form').html('');
                        add_sort_key();
                        $('#sort-form').slideDown( 400 );
                    }
                }
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
                var visible_form;
                if ( $('#filter-form > div').length > 0 ) {
                    $('#filter-form').slideUp( 400, function () {
                        $('#filter-form').html('').toggle();
                    });
                } else {
                    if ( $('#sort-form > div').length > 0 ) {
                        visible_form = $('#sort-form');
                    } else if ( $('#manage-columns-form > input').length > 0 ) {
                        visible_form = $('#manage-columns-form');
                    }
                    
                    if ( !!visible_form ) {
                        visible_form.slideUp( 400, function () {
                            visible_form.html('');
                            $('#filter-form').html('');
                            add_sort_key();
                            $('#filter-form').slideDown( 400 );
                        })
                    } else {
                        $('#filter-form').html('');
                        add_sort_key();
                        $('#filter-form').slideDown( 400 );
                    }
                }
            });

        $('#filter-form')
            .submit( function () {

                var column, operation, query;
                var mask = [];
                var i, len = $('#filter-form select').length / 2;
                var tmp, type;
                var new_sheet;
                var filtered_rows;
                
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

                filtered_rows = _algorithms.filter( _store.active_rows(), mask );
                new_sheet = {};
                $.extend( true, new_sheet, _store.active_sheet() );
                new_sheet['rows'] = create_filter_result( filtered_rows );
                new_sheet['filtered'] = true;

                _sheet.create_new_sheet( new_sheet, "Arkusz", true );

                _table.clean_table();
                _table.init_table();

                $(this).hide();

                return false;
           });
    };

    function 	prepare_manage_columns_interface(){
        $('#manage-columns-button')
            .click( function () {
                $('#filter-form').hide();
                $('#sort-form').hide();
                $('#manage-columns-form').html('').toggle();
                add_manage_checkbox();
            });

        $('#manage-columns-form')
            .submit( function () {
		//TODO changes in _store
                $(this).hide();
		return false;
        });   
    };

    function prepare_snapshot_interface() {

        $('#save-snapshot')
            .click( function () {
                _sheet.create_new_sheet( _store.active_sheet(), "Arkusz" );
            });
    }
    
    function create_filter_result( filtered_list ) {        
        return filtered_list.filter( function ( e ) {                   
                                 var id = e['data']['idef'];
                                 return ! $('#'+id).is(':hidden');
                             })
                             .map( function (e) {
                                 var id = e['data']['idef'];
                                 e['breadcrumb'] = create_breadcrumb( id );
                                 return e;
                             });
    }
    
    function get_filtered_data( visual_list ) {
        visual_data_object = {};
        
        var i;
        var id;
        for ( i = 0; i < visual_list.length; i += 1 ) {
            id = visual_list[i]['data']['idef'];
            visual_data_object[ id ] = visual_list[i];
        }
        
        return visual_data_object;
    }
    
    function create_breadcrumb( id ) {
        var tmp_id = id;
        var node;
        var type;
        var full_type;
        var name;
        var breadcrumb = [];
        var breadcrumb_list = [];
        
        tmp_id = _utils.get_parent_id( id );
        
        while ( !!tmp_id ) {
            node = $('#'+ tmp_id);
            full_type = node.children('.type').html();
            type = get_type_representation( full_type );
            name = node.children('.name').html();
            
            tmp_id = _utils.get_parent_id( tmp_id );
            breadcrumb_list.push({
                type: type,
                name: name
            });
        }
        
        breadcrumb_list = breadcrumb_list.reverse();
        
        breadcrumb_list.forEach( function ( el, i ) {
            breadcrumb.push( el['type'] + ' ' );
            if ( i < breadcrumb_list.length - 1 ) {
                if ( el['name'].length > 35 ) {
                    el['name'] = el['name']
                                           .slice(0, 32)
                                           .concat('...');
                }
            } else {
                if ( el['name'].length > 45 ) {
                    el['name'] = el['name']
                                           .slice(0, 42)
                                           .concat('...');
                }
            }
            breadcrumb.push( el['name'] );
            if ( i < breadcrumb_list.length - 1 ) {
                breadcrumb.push(' > ');
            }
        });
        
        return breadcrumb.join('');
    }
    
    function get_type_representation( full_type ) {
        var type_list;
        type_list = full_type.split(' ');
        return type_list.pop();
    }
    
}) ();





