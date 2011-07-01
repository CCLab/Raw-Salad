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
        $('thead').empty();
        $('tbody').empty();
    };

    that.init_table = function () {
        create_thead();
        create_tbody();

        _gui.make_zebra();
    };


    that.add_node = function ( parent_id ) {
        var children = _store.active_rows().filter( function ( e ) {
            return e['data']['parent'] === parent_id;
        });

        add_rows( children );
    };

    return that;

//  P R I V A T E   I N T E R F A C E

    function create_thead() {
        var schema = _store.basic_schema();
        var html = [ '<tr>' ];

        schema.forEach( function ( column ) {
            html.push( '<td class="', column['key'], ' ' );
            html.push( column['type'], '">' );
            html.push( column['label'] );
            html.push( '</td>' );
        });

        html.push( '</tr>' );
        $('thead').append( html.join('') );
    }

    function create_tbody() {
        var level = 'a';
        var hashed_list = _utils.hash_list( _store.active_rows() );

        while( !!hashed_list[ level ] ) {
            if( level === 'a' ) {
                add_top_level( hashed_list[ level ] );
            }
            else {
                add_rows( hashed_list[ level ] );
            }

            level = _utils.next_letter( level );
        }
    }


    function add_top_level( data ) {
        var i, len = data.length;
        var schema = _store.basic_schema();

        for( i = 0; i < len; ++i ) {
            $('tbody').append( generate_row({
                node: data[i],
                index: i,
                schema: schema
            }));
        }
    }


    function add_rows( data ) {
        var i = data.length - 1;
        var schema = _store.basic_schema();
	var parent;
        

        for( ; i >= 0; i -= 1 ) {
            parent = $( '#' + data[i]['data']['parent'] );
            parent.after( generate_row({
                node: data[i],
                schema: schema
            }));
        }
        _gui.make_zebra();
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
            // a-level parent
            var a_root = a_parent( $(this) );
            var a_root_id = a_root.attr('id');
            // next a-level node
            var a_root_index = parseInt( a_root.attr( 'data-index' ), 10 );
            var next = $('tr[data-index='+ (a_root_index + 1) +']');

            // dim everything outside this a-rooted subtree
            a_root
                .siblings()
                .not(':hidden')
                .addClass('dim');

            // make a-root background black
            $('tr.root').removeClass('root');
            a_root.addClass('root');

            // highlight the subtree
            with_subtree( a_root.attr('id'), function () {
                // uses 'this' instead of '$(this)' for fun.call reason
                this.removeClass( 'dim' );
            });

            // add the bottom border
            $('.next').removeClass('next');
            next.addClass('next');

            // open/close a subtree if it's a-level or already selected/open
            open_close_subtree( $(this), a_root );

            // clear selected attributes and set selection to clicked tree
            _store.set_selected( a_root_id );
            $('tr[data-selected=true]').attr('data-selected', 'false');
            a_root.attr('data-selected', 'true');

            _gui.make_zebra();
        });

        return row;
    }


    function open_close_subtree( node, root ) {
        var a_root = root || a_parent( node );
        var is_a_open     = a_root.attr( 'data-open' );
        var is_a_selected = a_root.attr( 'data-selected' );
        var id = node.attr('id');
        var children;

        if ( is_a_selected === is_a_open ) {
            // if the node is closed
            if( node.attr( 'data-open' ) === 'false' ) {

                // if children are hidden
                if( $('.'+id).length !== 0 ) {
                    with_subtree( id, $.fn.show );
                }
                // if children not loaded yet
                else {
                    _db.download_node( id );
                }

                // mark subtree as open
                _store.set_open( id, true );
                node.attr( 'data-open', 'true' );
            }
            // the node is closed
            else {
                // hide subtree
                with_subtree( id, $.fn.hide );

                // mark subtree as closed
                _store.set_open( id, false );
                node.attr( 'data-open', 'false' );

                // if it's a-level node - clear the css highlight/dim
                if( node.hasClass( 'a' ) ) {
                    node.removeClass( 'root' );
                    $('.dim').removeClass('dim');
                    $('.next').removeClass('next');
                }
            }
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


    // go through the subtree of id-node and do fun
    function with_subtree( id, fun ) {
        $('tr.'+id).each( function () {
            with_subtree( $(this).attr('id'), fun );
            fun.call( $(this) );
        });
    }

})();
