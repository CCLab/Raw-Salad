(function () {
    // good old store...
    var store = [];

    // execution ground
    var i;
    var data = full_data.filter( function ( e ) {
        return e['level'] === 'a';
    });
    var objects = [];
    for( i = 0; i < data.length; i += 1 ) { 
        objects.push( generate_sheet_row( data[i] ));
    }
    
    init_table( objects );
    make_zebra();

    $('#clone').click( function ( event ) {
        // TODO: _store.new_sheet();
        // TODO: _table.recreate_table();
        // TODO: _   
        var start = new Date().getTime();
        var store_copy = store.slice();

        store = [];

        $('tbody').html('');

        make_table( store_copy );
        make_zebra();
        console.log( new Date().getTime() - start );
    });


    // functions definitions
    function with_subtree( id, fun, args ) {
        $('tr.'+id).each( function () {
            with_subtree( $(this).attr('id'), fun );
            fun.apply( $(this), [ args ] );
        });
    }


    function next_letter( letter ) {
        var number = letter.charCodeAt( 0 );

        return String.fromCharCode( number + 1 );
    }


    function make_table( list ) {
        var level;
        var i;
        var hashed_data_list = Tools.all_rows( list, function ( elem ) {
                                   return elem['data'];
                               });
        var hashed_state_list = Tools.all_rows( list, function ( elem ) {
                                    return elem['state'];
                                });

        var level_data_nodes;
        var level_state_nodes;
        
        var max_level = hashed_data_list['highest_level'];
        
        for ( level = 'a'; level <= max_level; level = next_letter(level) ) {
            level_data_nodes = hashed_data_list[ level ];
            level_state_nodes = hashed_state_list[ level ];
                
            if (level === 'a' ) {
                init_table( level_data_nodes, level_state_nodes );
            }
            else {
                add_rows( level_data_nodes, level_state_nodes );
            }
        }
    }


    function make_zebra() {
        $('tr').not(':hidden').each( function ( i ) {
            if( i % 2 === 0 ) {
                $(this).removeClass( 'odd' );
                $(this).addClass( 'even' );
            }
            else {
                $(this).removeClass( 'even' );
                $(this).addClass( 'odd' );
            }
        });
    }
    
    
    function init_table( data_list ) {
        var i, len = data_list.length;
        var store_list = [];

        for( i = 0; i < len; ++i ) {
            $('tbody').append( generate_row( data_list[i] ));
        }
        make_zebra();

        // append new data into store
        store = [].concat( store, data_list );
    }
    
    
    function add_rows( data_list, state_list ) {
        var i = data_list.length - 1;
        var store_list = [];
        var data;
        var state;

        for( ; i >= 0; i -= 1 ) {
            data = data_list[i];
            if ( !!state_list ) {
                state = state_list[i];
            }
            
            store_list.push( generate_sheet_row( data, state ) );
            $('#'+data_list[i]['parent']).after( generate_row( data, state ));
        }

        // append new data into store
        // TODO _store.add_rows( store_list );
        store = [].concat( store, store_list );
    }
    
    
    function generate_sheet_row( data ) {
        return {
            data: data,
            state: { open: false, selected: false }
        };
    };
    

    function generate_row( node ) {
        var html = [];
        var row;
        var data = node['data'];
        var is_open;
        var is_selected;
        
        is_open = node['state']['open'];
        is_selected = node['state']['selected'];

        // row definition
        html.push( '<tr id="', data['idef'], '" ' );
        html.push( 'data-open="', is_open, '" ' );
        if( data['level'] === 'a' ) {
            html.push( 'data-selected="', is_selected, '" ' );
        }
        html.push( 'class="', data['level'], ' ', data['parent'],'">' );

        // cells definition
        html.push( '<td class="type', data['leaf'] ? '">' : ' click">' );
        html.push( data['type'], '</td>' );
        html.push( '<td class="name">', data['name'], '</td>' );
        html.push( '<td class="value">', Tools.money(data['v_eu']), '</td>' );
        html.push( '<td class="value">', Tools.money(data['v_nation']), '</td>' );
        html.push( '<td class="value">', Tools.money(data['v_total']), '</td>' );

        html.push( '</tr>' );

        // create & arm row
        row = $( html.join('') );
        row.click( function ( event ) {
            // a-level parent
            var a_root = a_parent( $(this) );
            // next a-level node
            var next = $('#'+(parseInt( a_root.attr('id'), 10 ) + 1));

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
                this.addClass( 'highlight' );
                this.removeClass( 'dim' );
            });

            // add the bottom border
            $('.next').removeClass('next');
            next.addClass('next');

            // open/close a subtree if it's a-level or already selected/open
            open_close_subtree( $(this), a_root );

            // clear selected attributes and set selection to clicked tree
            $('tr[data-selected=true]').attr('data-selected', 'false');
            a_root.attr('data-selected', 'true');

            make_zebra();
        });

        return row;
    }
    
    function do_node( id, fun ) {
        var i;
        var elem;
        
        for ( i = 0; i < store.length; i += 1 ) {
            elem = store[i];
            if ( elem['data']['idef'] === id ) {
                fun ( elem );
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
    
    // open/close a subtree if it's a-level or already selected/open
    function open_close_subtree( node, a_root ) {
        var a_root = a_root || a_parent( node );
        var a_level_open = a_root.attr( 'data-open' );
        var a_level_selected = a_root.attr( 'data-selected' );
        var id = node.attr('id');
        
        if ( a_level_selected === a_level_open ) {
debugger;
            // the node is closed
            if( node.attr( 'data-open' ) === 'false' ) {

                // children are hidden
                if( $('.'+id).length !== 0 ) {
                    with_subtree( id, $.fn.show );
                }
                // children not loaded yet
                else {
                    var children = full_data.filter( function ( e ) {
                        return e['parent'] === id;
                    });

                    add_rows( children );
                }

                // mark subtree as open
                node.attr( 'data-open', 'true' );
            }
            // the node is closed
            else {
                // hide subtree
                with_subtree( id, $.fn.hide );

                // mark subtree as closed
                node.attr( 'data-open', 'false' );

                // if it's a-level node - clear the css highlight/dim
                if( node.hasClass( 'a' ) ) {
                    node.removeClass( 'root' );
                    $('.dim').removeClass('dim');
                    $('.highlight').removeClass('highlight');
                    $('.next').removeClass('next');
                }
            }
        }
        
        do_node( id, function( elem ) {
            elem['state']['open'] = !elem['state']['open'];
        });
    }


})();
