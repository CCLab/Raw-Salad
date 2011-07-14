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
        prepare_search_interface();
    };

    that.show_search_results = function( results ) {
        var search_results = generate_search_results( results );

        search_results.insertBefore( $('#show-found-button') );
        $('#show-found-button').show();

        // unbind to avoid multi event handlers on show-found-button
        $('#show-found-button')
            .unbind('click')
            .click( function () {
                var search_list = [];
                var checkboxes = $("input[name=search-checkbox]");

                checkboxes.each( function ( i ) {
                    if ( $(this).is(':checked') ) {
                        search_list.push( results[i] );
                    }
                });
                _db.add_search_data( search_list );
            });
    };

    that.open_subtrees = function( basic_rows, subtree_rows ) {
        var nodes_to_open = {};

        // remember which nodes must be opened
        subtree_rows.forEach( function ( row ) {
            nodes_to_open[ row['parent'] ] = true;
        });

        // open nodes to show downloaded subtrees
        basic_rows.forEach( function ( store_row ) {
            id = store_row['data']['idef'];
            if ( !!nodes_to_open[ id ] ) {
                store_row['state']['open'] = true;
            }
        });
    }

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

//        html.push( '<input type="button" value="Zaznacz wszystkie" id="check-all" >' );
//        html.push( '<input type="button" value="Odznacz wszystkie" id="uncheck-all" style="margin-left: 5px;">' );
        html.push( '<div class="select-all" id="manage-columns-submit" style="margin-left: 10px">Dodaj/Usuń kolumny</div>' );
        html.push( '<div class="select-all" id="uncheck-all" style="background-color: #eee; color: #333; margin-left: 5px">Odznacz wszystkie</div>' );
        html.push( '<div class="select-all" id="check-all" style="background-color: #eee; color: #333">Zaznacz wszystkie</div>' );


        for( i = 0; i < all_columns.length; i += 1 ) {
            key = all_columns[i]['key'];
            html.push( '<br />' );
	        html.push( '<input type="checkbox" name="columns"' );
            html.push( ' value="', key, '" id="column-id-', key, '"' );
	        if( _store.is_column_in_active_sheet( key ) ) {
                html.push( 'checked');
            }
            html.push('>');
            html.push('<label for="column-id-', key,'" >');
            html.push(all_columns[i]['label'],'</label>');
        }
        $('#manage-columns-form').append( $( html.join('') ));

        $('#check-all')
            .click( function () {
                for( i = 0; i < $('input[name=columns]').length; i += 1){
                    $('input[name=columns]')[i].checked=true;
                }
            });

        $('#uncheck-all')
            .click( function () {
                for (i = 0; i < $('input[name=columns]').length; i += 1){
                    $('input[name=columns]')[i].checked=false;
                }
            });

        $('#manage-columns-submit').click( function () {
            $('#manage-columns-form').submit();
        });

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
                    $('#sort-form').slideUp( 200, function () {
                        $('#sort-form').html('');
                    });
                } else {
                    if ( $('#filter-form > div').length > 0 ) {
                        visible_form = $('#filter-form');
                    } else if ( $('#manage-columns-form > input').length > 0 ) {
                        visible_form = $('#manage-columns-form');
                    }

                    if ( !!visible_form ) {
                        visible_form.slideUp( 200, function () {
                            visible_form.html('');
                            add_sort_key();
                            $('#sort-form').slideDown( 200 );
                        })
                    } else {
                        add_sort_key();
                        $('#sort-form').slideDown( 200 );
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
                    $('#filter-form').slideUp( 200, function () {
                        $('#filter-form').html('');
                    });
                } else {
                    if ( $('#sort-form > div').length > 0 ) {
                        visible_form = $('#sort-form');
                    } else if ( $('#manage-columns-form > input').length > 0 ) {
                        visible_form = $('#manage-columns-form');
                    }

                    if ( !!visible_form ) {
                        visible_form.slideUp( 200, function () {
                            visible_form.html('');
                            add_filter_key();
                            $('#filter-form').slideDown( 200 );
                        })
                    } else {
                        add_filter_key();
                        $('#filter-form').slideDown( 200 );
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

    function prepare_manage_columns_interface(){
	    var new_active_columns;
        var i = 0;
        var checkboxes_list;

        $('#manage-columns-button')
            .click( function () {
                var columns_form = $('#manage-columns-form');

                $('#filter-form').hide();
                $('#sort-form').hide();

                if( columns_form.is( ':hidden' ) ) {
                    columns_form.html('');
                    add_manage_checkbox();
                    columns_form.slideDown( 200 );
                }
                else {
                    columns_form.slideUp( 200 );
                }
            });

        $('#manage-columns-form')
            .submit( function () {
                new_active_columns = [];
                checkboxes_list = $('input[name=columns]');
                 for ( i = 0; i < checkboxes_list.length; i += 1 ) {
                    if( checkboxes_list[i].checked ) {
                        new_active_columns.
                            push( _store.get_column_from_group(checkboxes_list[i].value) );
                    }
                }
		        _store.set_active_columnes( new_active_columns );
                _table.clean_table();
                _table.init_table();
                $(this).hide();
		return false;
        });

        $('#check-all')
            .click( function () {
                for (i = 0; i < $('input[name=columns]').length; i += 1){
                    $('input[name=columns]')[i].checked=true;
                }
            });

        $('#uncheck-all')
            .click( function () {
                for (i = 0; i < $('input[name=columns]').length; i += 1){
                    $('input[name=columns]')[i].checked=false;
                }
            });



    };

    function prepare_snapshot_interface() {

        $('#save-snapshot')
            .click( function () {
                _sheet.create_new_sheet( _store.active_sheet(), "Arkusz" );
            });
    }

    function prepare_search_interface() {
        $('#search-form')
            .submit( function () {
                var query;
                var scope;
                var strict;

                $('#search-results').remove();
                $('#show-found-button').hide();

                query = $('#search-text').val();
                if ( !!query ) {
                    scope = construct_scope();
                    strict = $('#strict-match').is(':checked');
                    _db.search( query, scope, strict );
                }

                return false;
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

    function construct_scope() {
        var scope = [];
        _store.meta_datasets().forEach( function ( dataset, dset_id ) {
            dataset['perspectives'].forEach( function ( perspective, per_id ) {
                perspective['issues'].forEach( function ( issue ) {
                    scope.push( dset_id + '-' + per_id + '-' + issue );
                });
            });
        });

        return scope;
    }

    function generate_search_results( results ) {
        var meta = _store.meta_datasets();
        var collection_name;
        var dataset;
        var view;
        var issue;
        var i;
        var html = ['<div id="search-results">'];

        if ( results.length === 0 ) {
            html.push('<div id="search-title">Nic nie znaleziono</div></div>');
        } else {
            html.push('<div id="search-title">Wyniki w kolekcjach danych</div>');

            results.forEach( function( col, col_i ) {
                dataset = meta[ col['dataset'] ];
                view = dataset['perspectives'][ col['view'] ];
                collection_name = view['name'] + ' ' + col['issue'];

                issue = -1;
                for ( i = 0; i < view['issues'].length; i += 1 ) {
                    if ( parseInt( view['issues'][i] ) === col['issue'] ) {
                        issue = i;
                        break;
                    }
                }

                _assert.not_equal( issue, -1, 'Issue: ' + col['issue'] + ' not found');

                html.push('<div id="search-collection-', col_i, '">');
                html.push('<input type="checkbox" id="search-checkbox-', col_i, '"');
                html.push(' name="search-checkbox" value="', collection_name, '"/>');
                html.push( collection_name );

                col['data'].forEach( function( row, row_i ) {
                    html.push('<div id="search-result-', col_i, '-', row_i, '">');
                    html.push('<div class="search-type">', row['type'], '</div>');
                    html.push('<div class="search-name">', row['name'], '</div>');
                    html.push('</div>');
                });

                html.push('</div>');
            });

            html.push('</div>');
        }

        return $( html.join('') );
    }

}) ();





