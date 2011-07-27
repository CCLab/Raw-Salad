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
        prepare_rename_sheet_interface();
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
        var key;
        var html = [];
        var schema = _store.active_columns();
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

        columns.unshift({
                    name: 'null',
                    label: ''
                });

        key = $('#app-tb-tl-sort-form').find('tbody > tr').length;

        if( key === 2 ) {
            $('#app-tb-tl-sort-add' ).hide();
        }

        html.push( '<tr id="sort-key-', key, '">' );
        html.push( '<td>' );
        html.push( '<select name="app-tb-tl-sort-form-columns" ');
        html.push( 'class="input-text key-', key, '">' );
        // TODO don't include already selected colmuns
        columns.forEach( function ( column ) {
            html.push( '<option value="', column['name'], '" class="column-key-', key, '">' );
            html.push( column['label'], '</option>' );
        });
        html.push( '</select>' );
        html.push( '</td>' );

        html.push( '<td>' );
        html.push( '<select name="app-tb-tl-sort-order" ' );
        html.push( 'class="input-text key-', key, '">' );
        html.push( '<option class="order-key-', key, '" value="null"></option>' );
        html.push( '<option class="order-key-', key, '" value="-1">Rosnąco</option>' );
        html.push( '<option class="order-key-', key, '" value="1">Malejąco</option>' );
        html.push( '</select>' );
        html.push( '</td>' );
        html.push( '</tr>' );

        $('#app-tb-tl-sort-form')
            .find('tbody')
            .append( $( html.join('') ));
    }


    function add_filter_key() {
        var i, key;
        var html = [];
        var filter_part;
        var selected_column;
        var type;
        var schema = _store.active_columns();
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

        columns.unshift({
                    name: 'null',
                    label: ''
                });

        key = $('#app-tb-tl-filter-form').find('tbody > tr').length;

        if( key === 2 ) {
            $('#app-tb-tl-filter-add' ).remove();
        }

        html.push( '<tr>' );
        html.push( '<td>' );
        html.push( '<select name="app-tb-tl-filter-form-columns" ');
        html.push( 'class="input-text key-', key, '" ' );
        html.push( 'id="filter-', key, '-columns">' );
        // add columns as select options
        columns.forEach( function ( column ) {
            html.push( '<option value="', column['name'], '" class="filter-column-', key, '">' );
            html.push( column['label'], '</option>' );
        });
        html.push( '</select>' );
        html.push( '</td>' );

        html.push( '<td>' );
        html.push( '<select id="filter-', key, '-operations"' );
        html.push( ' name="null-operation" class="input-text" disabled>' );
        html.push( '</select>' );
        html.push( '</td>' );

        html.push( '<td>' );
        html.push( '<input type="text" name="query" id="filter-', key, '-query" class="input-text"/>' );

        $('#app-tb-tl-filter-form')
            .find('tbody')
            .append( $( html.join('') ));


        $('#filter-'+ key +'-columns')
            .change( function() {
                selected_column = $(this).val();

                for ( i = 0; i < schema.length; i += 1 ) {
                    if ( schema[i]['key'] === selected_column ) {
                        type = schema[i]['type'];

                        $('#filter-' + key + '-operations').remove();

                        html = [ '<select id="filter-', key, '-operations"' ];
                        if ( schema[i]['type'] === 'number' ) {
                            html.push( ' name="number-operation" class="input-text">' );
                            html.push( '<option value="null" class="filter-operation-', key, '" selected></option>' );
                            html.push( '<option value="gt" class="filter-operation-', key, '">&gt;</option>' );
                            html.push( '<option value="eq" class="filter-operation-', key, '">=</option>' );
                            html.push( '<option value="lt" class="filter-operation-', key, '">&lt;</option>' );
                        } else {
                            html.push( ' name="string-operation" class="input-text">' );
                            html.push( '<option value="null" class="filter-operation-', key, '" selected></option>' );
                            html.push( '<option value="cnt" class="filter-operation-', key, '">Zawiera</option>' );
                            html.push( '<option value="st" class="filter-operation-', key, '">Zaczyna się od</option>' );
                            html.push( '<option value="ncnt" class="filter-operation-', key, '">Nie zawiera</option>' );
                            html.push( '<option value="nst" class="filter-operation-', key, '">Nie zaczyna się od</option>' );
                        }
                        html.push( '</select>' );

                        $(this).parent().next().append( $( html.join('') ));//.insertAfter( $('#filter-' + key + '-columns') );
                        break;
                    }
                }
            });
    }


    function update_columns_form()  {
        var html = [];
	    var all_columns = _store.group_columns();

        all_columns.forEach( function ( e ) {
            var key = e['key'];

            html.push( '<tr><td class="columns">' );
	        html.push( '<input type="checkbox" name="app-tb-tl-columns" ' );
            html.push( 'value="', key, '" id="column-id-', key, '"' );
	        if( _store.is_column_in_active_sheet( key ) ) {
                html.push( ' checked');
            }
            html.push( '>' );
            html.push( '</td><td class="columns">' );
            html.push( '<label for="column-id-', key, '">' );
            html.push( e['label'], '</label>' );
            html.push( '</td></tr>' );
        });
        $('#app-tb-tl-columns-form')
            .find('tbody')
            .append( $( html.join('') ));
    }

// >>
    function prepare_sorting_interface() {

        $('#app-tb-tl-sort-button')
            .click( function () {
                var form = $('#app-tb-tl-sort-form');
                var others = $('#app-tb-tools').find('form:visible');

                if( form.is(':hidden' )) {
                    form.find('tbody').empty();
                    add_sort_key();

                    if( others.length === 0 ) {
                        form.slideDown( 200 );
                    }
                    else {
                        others.slideUp( 200, function () {
                            form.slideDown( 200 );
                        });
                    }
                }
                else {
                    form.slideUp( 200 );
                }

                $(this)
                    .toggleClass('pushed')
                    .siblings()
                    .removeClass('pushed');

                $('#app-tb-tl-sort-add').show();
            });

        $('#app-tb-tl-sort-add').click( function () {
            add_sort_key();
        });

        $('#app-tb-tl-sort-submit')
            .click( function () {
                $('#app-tb-tl-sort-form').submit();
            });

        $('#app-tb-tl-sort-form')
            .submit( function () {
                var column, order;
                var settings = [];
                var i;
                var keys_num = $('#app-tb-tl-sort-form').find('tbody > tr').length;

                for( i = 0; i < keys_num; i += 1 ) {
                    column = $( '.column-key-'+ i +':selected' ).val();
                    // if column not selected by user
                    if( column === "null" ) {
                        // if it's a first key - quit
                        if( i === 1 ) {
                            $(this).hide();
                            return false;
                        }
                        // process the previous keys
                        else {
                            break;
                        }
                    }
                    order = parseInt( $('.order-key-'+ i +':selected').val() );
                    // if order not set, set it to ascending
                    if( !order ) {
                        order = 1;
                    }
                    settings.push(
                        {
                            "pref": order,
                            "name": column
                        }
                    );
                }

                that.sort( _store.active_rows(), settings );

                _gui.refresh_gui();
                //_table.clean_table();
                //_table.init_table();
                $(this).hide();

                return false;
            });

        var i;
        for( i = 1; i <= $('#app-tb-tl-sort-form select').length; ++i ) {
            if( i > 1 ) {
                $('#key-'+i).hide();
            }

            (function (i) {
                $('#app-tb-tl-sort-form select.key-'+i).change( function () {
                    if( $('.key-'+i+' option:selected').val() !== "null" ) {
                        $('#key-'+(i+1)).show();
                    }
                });
            })(i);
        }
    };


    function prepare_filtering_interface() {

        $('#app-tb-tl-filter-button')
            .click( function () {
                var form = $('#app-tb-tl-filter-form');
                var others = $('#app-tb-tools').find('form:visible');

                if( form.is(':hidden' )) {
                    form.find('tbody').empty();
                    add_filter_key();

                    if( others.length === 0 ) {
                        form.slideDown( 200 );
                    }
                    else {
                        others.slideUp( 200, function () {
                            form.slideDown( 200 );
                        });
                    }
                }
                else {
                    form.slideUp( 200 );
                }

                $(this)
                    .toggleClass('pushed')
                    .siblings()
                    .removeClass('pushed');

                $('#app-tb-tl-filter-add' ).show();
            });

        $('#app-tb-tl-filter-add')
            .click( function () {
                add_filter_key();
            });

        $('#app-tb-tl-filter-submit')
            .click( function () {
                $('#app-tb-tl-filter-form').submit();
            });

        $('#app-tb-tl-filter-form')
            .submit( function () {

                var column, operation, query;
                var filtered_rows;
                var i;
                var keys_num = $('#app-tb-tl-filter-form').find('tbody > tr').length;
                var mask = [];
                var new_sheet;
                var tmp, type;

                for( i = 0; i < keys_num; ++i ) {
                    column = $('.filter-column-'+ i +':selected').val();
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

                    operation = $('.filter-operation-'+i+':selected').val();;
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

        $('#app-tb-tl-columns-button')
            .click( function ( event ) {
                var columns_form = $('#app-tb-tl-columns-form');

                $('#app-tb-tools')
                    .find('form:visible')
                    .slideUp( 200 );

                $('#app-tb-tl-bt-container')
                    .find('div')
                    .removeClass('selected');

                if( columns_form.is( ':hidden' ) ) {
                    // clear previous columns list
                    columns_form.find('tbody').empty();
                    // add new positions to the list
                    update_columns_form();
                    // show the form
                    columns_form.slideDown( 200 );

                    $('html')
                        .click( function () {
                            $('#app-tb-tl-columns-button')
                                .trigger( $.Event( 'click' ));
                        });

                }
                else {
                    $('html')
                        .unbind( 'click' );
                }

                event.stopPropagation();
            });


        $('#app-tb-tl-lt-select')
            .click( function () {
                $('input[name=app-tb-tl-columns]').attr( 'checked', 'true' );
            });

        $('#app-tb-tl-lt-unselect')
            .click( function () {
                $('input[name=app-tb-tl-columns]').removeAttr( 'checked' );
            });

        $('#app-tb-tl-lt-submit')
            .click( function () {
                $('#app-tb-tl-columns-form').submit();
            });

        $('#app-tb-tl-columns-form')
            .click( function ( event ) {
                event.stopPropagation();
            })
            .submit( function () {
                new_active_columns = [];
                checkboxes = $('input[name=app-tb-tl-columns]:checked');

                checkboxes.each( function () {
                    new_active_columns.
                        push( _store.get_column_from_group( $(this).val() ));
                 });

		        _store.set_active_columnes( new_active_columns );
                // TODO _gui.refresh() ?!
                _table.clean_table();
                _table.init_table();
                $(this).hide();
                $('html').unbind( 'click' );

                // to prevent form's action!!
                return false;
            });
    }

    function prepare_snapshot_interface() {

        $('#app-tb-save-sheet')
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

    function prepare_rename_sheet_interface() {
        $('#app-tb-tl-rename-form')
            .submit( function () {
                var old_sheet_name = _store.active_sheet_name();
                var new_sheet_name = $('#app-tb-tl-rename-input').val();
                if ( old_sheet_name !== new_sheet_name ){
                    alert("Set new sheet name");        
                }
                $('#app-tb-tl-rename-form').hide();
                $('#app-tb-tl-title').show();
                return false;         
            });

        $('#app-tb-tl-rename-button')
            .click( function () {
                var active_sheet_name = _store.active_sheet_name();
                $('#app-tb-tl-title').hide();
                $('#app-tb-tl-rename-input').val( active_sheet_name );
                $('#app-tb-tl-rename-form').show();
                $('#app-tb-tl-rename-button').click( function () {
                    $('#app-tb-tl-rename-form').submit();
                } );
            });
    }

    function set_new_sheet_name() {
    
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





