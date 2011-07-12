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
        $('#data-table > thead').empty();
        $('#data-table > tbody').empty();
        $('#filtered-thead').empty();
        $('#filtered-tbody').empty();
    };

    that.init_table = function () {
        _utils.create_preloader('Wczytujê tabelê');
        if ( !_store.active_filtered() ) {
            create_thead();
            create_tbody();
            _gui.make_zebra();
        } else {
            create_filtered_thead();
            create_filtered_tbody();
        }
        _utils.clean_preloader();
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
            html.push( '<tr style="background-color: #3b3b3b">' );

            schema.forEach( function ( column ) {
                html.push( '<td class="', column['key'], ' ' );
                html.push( column['type'], '">' );
                html.push( total['data'][ column['key'] ] );
                html.push( '</td>' );
            });

            html.push( '</tr>' );
        }
        $('#data-table > thead').append( html.join('') );
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
            $('#data-table > tbody').append( generate_row({
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
            if( parent.attr( 'data-open' ) === 'false' ) {
                continue;
            }
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
            html.push( column['type'] );
            html.push( !data['leaf'] && column['key'] === 'type' ? ' click">' : '">' );
            html.push( data[column['key']] );
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

//            _gui.make_zebra();
        });

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

        $('#filtered-thead').append( html.join('') );
    }

    function create_filtered_tbody() {
        var level = 'a';
        var hashed_list = _utils.hash_list( _store.active_rows() );
        var rows_to_add = _store.active_rows().length;
        var rows_on_level;

        while( rows_to_add > 0 ) {
            rows_on_level = hashed_list[ level ];
            if ( !!rows_on_level ) {
                rows_to_add -= rows_on_level.length;
                add_filtered_rows( rows_on_level );
            }
            level = _utils.next_letter( level );
        }
    }

    function add_filtered_rows( data ) {
        var parent;
        var new_node;
        var schema = _store.active_columns();

        data.reverse().forEach( function ( row ) {
            parent = find_parent( row['data']['idef'] );
            new_node = generate_filtered_row({
                node: row,
                schema: schema
            });
            if ( !!parent ) {
                parent.after( new_node );
            } else {
                $('#filtered-tbody').prepend( new_node );
            }
        });
    }

    function generate_filtered_row( args ) {
        var html = [];
        var node = args['node'];
        var breadcrumb = node['breadcrumb'] || '';

        // breadcrumb
        html.push( '<tr class="filtered-breadcrumb">' );
        html.push( '<td colspan="', args['schema'].length, '" ' );
        html.push( 'id="breadcrumb-', node['data']['idef'], '">');
        html.push( breadcrumb );
        html.push( '</td>' );
        html.push( '</tr>');

        // filtered row
        html.push( '<tr class="filtered-data">' );
        args['schema'].forEach( function ( column ) {
            html.push( '<td class="', column['key'], ' ', column['type'], '">' );
            html.push( node['data'][ column['key'] ] );
            html.push('</td>');
        });
        html.push( '</tr>' );

        return $( html.join('') );
    }

    function find_parent( id ) {
        var parent_id = _utils.get_parent_id( id );
        var parent;

        while ( !!parent_id ) {
            parent = $('#' + parent_id);
            if ( !!parent.length ) {
                return parent;
            }
            parent_id = _utils.get_parent_id( parent_id );
        }
        // if parent not found, return []
        return '';
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

                // if children are hidden
                if( $('.'+id).length !== 0 ) {
                    _utils.with_subtree( id, $.fn.show );
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

                // mark subtree as open
                _store.set_open( id, true );
                node.attr( 'data-open', 'true' );

                // clear selected attributes and set selection to clicked tree
                _store.set_selected( a_root_id, true );
                $('tr[data-selected=true]').attr('data-selected', 'false');
                a_root.attr('data-selected', 'true');
            }
            // the node is closed
            else {
                // hide subtree
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
