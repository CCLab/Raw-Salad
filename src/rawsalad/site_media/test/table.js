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

var _table = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    that.clean_table = function () {
        $('#app-tb-datatable > thead').empty();
        $('#app-tb-datatable > tbody').empty();
        $('#app-tb-filteredtable > thead').empty();
        $('#app-tb-filteredtable > tbody').empty();
    };

    that.init_table = function () {
        if ( !_store.active_filtered() ) {
            create_thead();
            create_tbody();
            _gui.make_zebra();
            $('#app-tb-tl-columns-button').show();
            $('#app-tb-tl-clear-button').show();
            $('#app-tb-tl-filter-button').show();
            $('#app-tb-tl-sort-button').show();
            $('#app-tb-tl-sort-button').css({
                'border-radius': '5px 0px 0px 5px',
                '-moz-border-radius': '5px 0px 0px 5px',
                '-webkit-border-radius': '5px 0px 0px 5px',
                '-o-border-radius': '5px 0px 0px 5px'
            });
        } else {
            create_filtered_thead();
            create_filtered_tbody( _store.active_sorted() );
            $('#app-tb-tl-columns-button').hide();
            $('#app-tb-tl-clear-button').hide();
            $('#app-tb-tl-filter-button').hide();
            $('#app-tb-tl-sort-button').css({
                'border-radius': '5px',
                '-moz-border-radius': '5px',
                '-webkit-border-radius': '5px',
                '-o-border-radius': '5px'
            });
        }
    };

    that.add_node = function ( parent_id ) {
        var children = _store.active_rows().filter( function ( e ) {
            return e['data']['parent'] === parent_id;
        });

        add_rows( children );
        _gui.make_zebra();
    };

    return that;

//  P R I V A T E   I N T E R F A C E

    function create_thead() {
        var schema = _store.active_columns();
        var total = _store.active_rows()['total'];
        var html = [ '<tr>' ];

        // create header
        schema.forEach( function ( column ) {
            html.push( '<td class="', column['key'], ' ' );
            html.push( column['type'], '">' );
            html.push( column['label'] );
            html.push( '</td>' );
        });

        html.push( '</tr>' );

        // create total row
        if( !!total ) {
            html.push( '<tr style="background-color: #8b8b8b">' );

            schema.forEach( function ( column ) {
                html.push( '<td class="', column['key'], ' ' );
                if( column['format'] !== '@' ) {
                    html.push( 'number">' );
                    html.push( _utils.money( total['data'][ column['key'] ], column['format'] ));
                }
                else {
                    html.push( 'string">' );
                    html.push( total['data'][ column['key'] ] );
                }
                html.push( '</td>' );
            });

            html.push( '</tr>' );
        }
        $('#app-tb-datatable > thead').append( html.join('') );
    }

    function create_tbody() {
        var level = 'a';
        var hashed_list = _utils.hash_list( _store.active_rows() );
        var selected_node;

        while( !!hashed_list[ level ] ) {
            if( level === 'a' ) {
                add_top_level( hashed_list[ level ] );
            }
            else {
                add_rows( hashed_list[ level ] );
            }

            level = _utils.next_letter( level );
        }

        // apply node selection(if there is selected node) to css classes
        selected_node = _store.active_rows().filter( function ( e ) {
            return e['state']['selected'];
        });
        if ( selected_node.length > 0 ) {
            apply_selection( selected_node[0]['data']['idef'] );
        }
    }

    function add_top_level( data ) {
        var i, len = data.length;
        var schema = _store.active_columns();

        for( i = 0; i < len; ++i ) {
            $('#app-tb-datatable > tbody').append( generate_row({
                node: data[i],
                index: i,
                schema: schema
            }));
        }
    }


    function add_rows( data ) {
        var i = data.length - 1;
        var schema = _store.active_columns();
        var parent;

        for( ; i >= 0; i -= 1 ) {
            parent = $( '#' + data[i]['data']['parent'] );
//            if( parent.attr( 'data-open' ) === 'false' ) {
//                continue;
//            }
            parent.after( generate_row({
                node: data[i],
                schema: schema
            }));
        }
//        _gui.make_zebra();
    }


    // generate a single table row
    function generate_row( args ) {
        var node = args['node'];
        var data = node['data'];
        var schema = args['schema'];
        var is_open = node['state']['open'];
        var is_selected = node['state']['selected'];
        var is_visible = node['state']['visible'];
        var html = [];
        var row;

        // row definition
        html.push( '<tr id="', data['idef'], '" ' );
        html.push( 'data-open="', is_open, '" ' );
        if( data['level'] === 'a' ) {
            html.push( 'data-selected="', is_selected, '" ' );
            html.push( 'data-index="', args['index'], '" ' );
        }
        html.push( 'class="', data['level'], ' ', data['parent'],'">' );

        // cells definition
        // TODO >> it can be sligthly slower than for loop - test it
        schema.forEach( function ( column ) {
            html.push( '<td class="', column['key'], ' ' );
            html.push( !data['leaf'] && column['key'] === 'type' ? ' click ' : '' );
            if( column['format'] !== '@' ) {
                html.push( 'number">' );
                html.push( _utils.money( data[column['key']], column['format'] ) );
            }
            else {
                html.push( 'string">' );
                html.push( data[column['key']] );
            }
            if( !!data['info'] && column['key'] === 'type' ) {
                //html.push( '<img src="/site_media/img/info_small.png" border="0" i' );
                //html.push( 'data-id="', data['idef'], '" style="margin-left: 5px;"/>' );
                html.push( generate_info_panel_button( data ) );
            }
            html.push( '</td>' );
        });

        html.push( '</tr>' );

        // create & arm row
        row = $( html.join('') );
        row.click( function ( event ) {
                // update css classes connected with node selection
                apply_selection( $(this).attr('id') );

                // open/close a subtree if it's a-level or already selected/open
                open_close_subtree( $(this), a_parent( $(this) ) );

            })
            .hover(
                function () {
                    $(this).find('.click').css('color', '#1a7aad' );
                },
                function () {
                    $(this).find('.click').css('color', '#11a8f7' );
                }
            );

        row.find('img')
           .click( function ( event ) {
           //     console.log( _store.get_info( $(this).attr('data-id') ).toString() );
                var info_panel_close_button = $('#app-tb-in-con-button-x');
                if ( info_panel_close_button.length === 1 ){
                   info_panel_close_button.trigger( $.Event( 'click' ));
                }
                else{
                generate_info_panel_content( _store.get_info( $(this).attr('data-id') ));
                $('#app-tb-info')
                    .click( function ( event ){
                        event.stopPropagation();
                    });
                $('#app-tb-in-con-button-x').click( function() {
                    $('#app-tb-in-content').slideUp( 200, function () {
                    	$('#app-tb-info').remove();
                    	$('html').unbind( 'click' );
            	    });
                });
                $('html')
                    .click( function () {
                        $('#app-tb-in-con-button-x')
                            .trigger( $.Event( 'click' ));
                });
                }
                event.stopPropagation();
           });

        if ( !is_visible ) {
            row.hide();
        }

        return row;
    }

    function create_filtered_thead() {
        var schema = _store.active_columns();
        var html = [];

        html.push( '<tr>' );
        schema.forEach( function ( column ) {
            html.push( '<th class="', column['key'], ' ', column['type'], '" ' );
            html.push( 'class="filtered-data">' );
            html.push( column['label'], '</th>' );
        });
        html.push( '</tr>' );

        $('#app-tb-filteredtable > thead').append( html.join('') );
    }

    function create_filtered_tbody( is_sorted ) {
        var schema = _store.active_columns();
        // deep copy is made to ensure that _store is not changed by sort
        var rows_copy = [];
        $.extend( true, rows_copy, _store.active_rows() );

        if ( !is_sorted ) {
            rows_copy.sort( function ( a, b ) {
                if ( a['data']['idef_sort'] < b['data']['idef_sort'] ) {
                    return -1;
                } else if ( a['data']['idef_sort'] > b['data']['idef_sort'] ) {
                    return 1;
                } else {
                    return 0;
                }
            });
        }
        rows_copy.forEach( function ( row ) {
                     var new_node = generate_filtered_row({
                                         node: row,
                                         schema: schema
                                     });
                     $('#app-tb-filteredtable > tbody').append( new_node );
                 });
    }

    function generate_filtered_row( args ) {
        var node = args['node'];
        var breadcrumb = node['breadcrumb'] || node['data']['breadcrumb'] || '';
        var html = [];

        // breadcrumb
        html.push( '<tr class="filtered-breadcrumb">' );
        html.push( '<td colspan="', args['schema'].length, '" ' );
        html.push( 'id="breadcrumb-', node['data']['idef'], '">');
        html.push( breadcrumb );
        html.push( '</td>' );
        html.push( '</tr>');

        // filtered row
        html.push( '<tr id="', node['data']['idef'], '" ' );
        html.push( 'class="filtered-data">' );
        args['schema'].forEach( function ( column ) {
            html.push( '<td class="', column['key'], ' ' );
            if( column['format'] !== '@' ) {
                html.push( 'number">' );
                html.push( _utils.money( node['data'][ column['key']], column['format'] ));
            }
            else {
                html.push( 'string">' );
                html.push( node['data'][ column['key'] ] );
            }
            html.push('</td>');
        });
        html.push( '</tr>' );

        return $( html.join('') );
    }

    function generate_info_panel_button( data ) {
        var html = [ '<div class="app-tb-info-button">' ];
        html.push( '<img src="/site_media/img/info_small.png" border="0" ' );
        html.push( 'data-id="', data['idef'], '" style="margin-left: 5px;"/>' );
        html.push( '</div>' );
        return html.join('');
    }


    function generate_info_panel_content( info ) {
        var html = [];
        var parent_id = info['0']['parent'];
        var info_button = $( '#' + parent_id ).find( '.app-tb-info-button' );

        html.push( '<div id="app-tb-info">' );
        html.push( '<div id="app-tb-in-content">' );
        html.push( '<h3 style="float: left;">Ten panel zawiera informacje dodatkowe nie mieszczące się w podstawowej strukturze danych.</h3>' );
        html.push( '<div id="app-tb-in-con-button-x"  style="margin-top: 3px; float: right;"> x </div> ' );
        html.push( '<br style="clear: both;" />' );
        html.push( '<br style="clear: both;" />' );
        html.push( '<div id="app-tb-in-header">' );
        html.push( _tools.create_info_breadcrumb( parent_id ) );
        html.push( '</div>' );
        html.push( '<div id="app-tb-in-title">' );
        html.push( _store.get_node_name(parent_id) );
        html.push( '</div>' );
        html.push( generate_info_panel_text( info ) );
        html.push( '</div>' );
        html.push( '</div>' );

        info_button.parent().append( html.join('') );
        $('#app-tb-in-content').slideDown( 200 );

    }

    function generate_info_panel_text( info ) {
        var html = [];
        var functions_map = {
            '0': generate_text_for_budzet,
            '2': generate_text_for_fundusze_zad,
            '3': generate_text_for_nfz
        };
        var text_generator = functions_map[ _store.dataset() ];
        var visible_attrs = prepare_visible_attributes();

        html.push( text_generator( info, visible_attrs ) );
        html.push( '</table>' );

        return html.join('');
    }


    function generate_text_for_budzet( info, visible_attrs ) {
        var html;
        var budzet_function_map = {
            '0': generate_text_for_budzet_ksiegowy,
            '1': generate_text_for_budzet_zadaniowy
        }
        var text_generator = budzet_function_map[ _store.view() ];
        html = text_generator( info, visible_attrs );
        return html;
    }

    function generate_text_for_budzet_ksiegowy( info, visible_attrs ) {
        var html = [];
        var list = info.slice();
        // sort list by 'dzial' value
        list.sort( function( a, b ) {
                var a_idef_list = a['idef'].split( '-' );
                var b_idef_list = b['idef'].split( '-' );
                return a_idef_list[1] - b_idef_list[1];
            });

        html.push( '<table id="app-tb-in-con-table1" >' );
        html.push( '<tbody>' );
        list.forEach( function ( e ) {
            html.push( '<tr><td class="app-tb-in-con-type" >', e['type'], ':');
            html.push('</td><td class="app-tb-in-con-name" >', e['name'], '</td></tr>' );
        });
        html.push( '</tbody>' );
        html.push( '</table>' );
        return html.join('');
    }


    function generate_text_for_budzet_zadaniowy( info, visible_attrs ) {
        var attr;
        var html = [];
        var cont = null;

        html.push( '<table id="app-tb-in-con-table1" >' );
        html.push( '<tbody>' );
        info.forEach( function ( e ) {
            html.push( '<tr><td class="app-tb-in-con-type" >', e['type'], ':');
            html.push('</td><td class="app-tb-in-con-name" >', e['name'], '</td></tr>' );
            if ( e['type'] === 'Miernik' ) {
                cont = e;
            }
        });
        html.push( '</tbody>' );
        html.push( '</table>' );

        html.push( '<table id="app-tb-in-con-table2" >' );
        html.push( '<tbody>' );
        if ( cont !== null ){

            for ( attr in visible_attrs ) {
                if ( visible_attrs.hasOwnProperty(attr) ) {
                    html.push( '<tr><td class="app-tb-in-con-attr" >', visible_attrs[attr],':' );
                    html.push( '</td><td class="app-tb-in-con-num" >', cont[attr], '</td></tr>' );
                }
            }
        }
        html.push('</tbody>');
        html.push( '</table>' );

        return html.join('');
    }

    function generate_text_for_fundusze_zad( info, visible_attrs ) {
        var attr;
        var html = [];
        var cont = null;

        html.push( '<table id="app-tb-in-con-table1" >' );
        html.push( '<tbody>' );
        info.forEach( function ( e ) {
            html.push( '<tr><td class="app-tb-in-con-type" >', e['type'], ':' );
            html.push( '</td><td class="app-tb-in-con-name" >', e['name'], '</td></tr>');

            if ( e['type'] === 'Miernik' ) {
                cont = e;
            }

        });
        html.push( '</tbody>' );
        html.push( '</table>' );

        html.push( '<table id="app-tb-in-con-table2" >' );
        html.push( '<tbody>' );
        if ( cont !== null ){
            for ( attr in visible_attrs ) {
                if ( visible_attrs.hasOwnProperty(attr) ) {
                    html.push( '<tr><td class="app-tb-in-con-attr" >', visible_attrs[attr], ':' );
                    html.push( '</td><td class="app-tb-in-con-num" >', cont[attr], '</td></tr>' );
                }
            }
        }
        html.push('</tbody>');
        html.push( '</table>' );
        return html.join('');
    }

    function generate_text_for_nfz( info, visible_attrs ) {
        var html = [];
        var attr;

        html.push( '<table id="app-tb-in-con-table1" >' );
        html.push( '<tbody>' );
        html.push( '<tr><td class="app-tb-in-con-type" >');
        html.push('</td> <td class="app-tb-in-con-name" >', info[0]['name'], '</td>' );
        html.push( '</tr>' );

        html.push( '</tbody>' );
        html.push( '</table>' );

        html.push( '<table id="app-tb-in-con-table2" >' );
        html.push( '<tbody>' );
        for ( attr in visible_attrs ) {
            if ( visible_attrs.hasOwnProperty(attr) ) {
                    html.push( '<tr><td class="app-tb-in-con-attr" >', visible_attrs[attr], ':' );
                    html.push ( '</td><td class="app-tb-in-con-num">' );
                    html.push( info[0][attr], '</td></tr>' );
            }
        }

        html.push( '</tbody>' );
        html.push( '</table>' );
        return html.join('');
    }

    function prepare_visible_attributes() {
        var visible_attrs = {};
        var dataset = _store.dataset();
        var year;

        if ( dataset === '0' ) {
            visible_attrs = {
                'wartosc_bazowa': 'Wartosc bazowa',
                'wartosc_rok_obec': 'Wartosc rok obecny'
            };
        }
        else if ( dataset === '2' ) {
            visible_attrs[ 'miernik_wartosc_bazowa' ] = 'Wartosc bazowa';
            _store.active_columns().forEach( function ( col ) {
                if ( /val_(\d+)/.test(col['key']) ) {
                    year = /val_(\d+)/.exec( col['key'] )[1];
                    visible_attrs[ 'miernik_wartosc_' + year ] =
                        'Miernik wartosc ' + year + 'r.';
                }
            });
        }
        else if ( dataset === '3' ) {
            _store.active_columns().filter ( function ( col ) {
                    return col['key'] !== 'type';
                })
                .forEach( function( col ) {
                    if ( col['key'] !== 'type' && col['key'] !== 'name' ) {
                        visible_attrs[ col['key'] ] = col['label'];
                    }
                });
        }

        return visible_attrs;
    }

    function find_parent( id ) {
        var parent_id = _utils.get_parent_id( id );
        var parent;

        while ( !!parent_id ) {
            parent = $( '#' + parent_id );
            if ( !!parent.length ) {
                return parent;
            }
            parent_id = _utils.get_parent_id( parent_id );
        }
        // if parent not found, return ''
        return null;
    }

    function apply_selection( id ) {
        var node = $('#' + id);

        // a-level parent
        var a_root = a_parent( node );
        var a_root_id = a_root.attr('id');
        // next a-level node
        var a_root_index = parseInt( a_root.attr( 'data-index' ), 10 );
        var next = $('tr[data-index='+ (a_root_index + 1) +']');

        // dim everything outside this a-rooted subtree
        a_root
            .siblings()
            .addClass('dim')
            .end()
            .removeClass('dim');

        // make a-root background black
        $('tr.root').removeClass('root');
        a_root.addClass('root');

        // highlight the subtree
        _utils.with_subtree( a_root.attr('id'), function () {
            // uses 'this' instead of '$(this)' for fun.call reason
            this.removeClass( 'dim' );
        });

        // add the bottom border
        $('.next').removeClass('next');
        next.addClass('next');
    }


    function show_selected_subtree( id ) {
        var list = $('tr.'+id);
        list.each( function () {
            var node = $(this);
            var new_id = node.attr('id');
            var data_open = node.attr( 'data-open' );
            if ( data_open === 'true' ) {
                show_selected_subtree( new_id );
            }
            node.show();
           _store.set_visible( new_id, true );
        });
        _store.set_visible( id, true );
    }


    function set_invisible_subtree( id ) {
        var list = $('tr.'+id);
        list.each( function () {
            var node = $(this);
            var new_id = node.attr('id');
            var data_open = node.attr( 'data-open' );
            if ( data_open === 'true' ) {
                set_invisible_subtree( new_id );
            }
            _store.set_visible( new_id, false );
        });
    }


    function open_close_subtree( node, root ) {
        var a_root = root || a_parent( node );
        var a_root_id = a_root.attr('id');
        var is_a_open     = a_root.attr( 'data-open' );
        var is_a_selected = a_root.attr( 'data-selected' );
        var id = node.attr('id');
        var children;
        var previously_selected_id;

        if ( is_a_selected === is_a_open ) {
            // if the node is closed
            if( node.attr( 'data-open' ) === 'false' ) {

                // mark subtree as open
                _store.set_open( id, true );
                node.attr( 'data-open', 'true' );

                // if children are hidden
                var test = $('.'+id);
                if( $('.'+id).length !== 0 ) {
                   // _utils.with_subtree( id, $.fn.show );
                   show_selected_subtree( id );
                   _gui.make_zebra();
                }
                // if children not loaded yet
                else {
                    _db.download_node( id );
                }

                // if there is previously selected node, unselect it in _store
                previously_selected_id = $('tr[data-selected=true]').attr('id');
                if ( !!previously_selected_id ) {
                    _store.set_selected( previously_selected_id, false );
                }


                // clear selected attributes and set selection to clicked tree
                _store.set_selected( a_root_id, true );
                $('tr[data-selected=true]').attr('data-selected', 'false');
                a_root.attr('data-selected', 'true');
            }
            // the node is closed
            else {
                // hide subtree
                set_invisible_subtree( id );
                _utils.with_subtree( id, $.fn.hide );

                // mark subtree as closed
                _store.set_open( id, false );
                node.attr( 'data-open', 'false' );


                // if it's a-level node - clear the css highlight/dim
                if( node.hasClass( 'a' ) ) {
                    node.removeClass( 'root' );
                    $('.dim').removeClass('dim');
                    $('.next').removeClass('next');

                    // clear selected attributes and set selection to clicked tree
                    _store.set_selected( a_root_id, false );
                    $('tr[data-selected=true]').attr('data-selected', 'false');
                }
            }
        }
        else if( a_root.attr( 'data-selected' ) === 'false' ) {
            // unselect previously selected node in _store
            previously_selected_id = $('tr[data-selected=true]').attr('id');
            _store.set_selected( previously_selected_id, false );

            _store.set_selected( a_root_id, true );
            $('tr[data-selected=true]').attr('data-selected', 'false');
            a_root.attr('data-selected', 'true');
        }
    }


    // return a-level parent of a given node
    function a_parent( node ) {
        if( node.hasClass( 'a' ) ) {
            return node;
        }
        var prev = node.prev();

        return prev.hasClass('a') ? prev : a_parent( prev );
    }

})();

