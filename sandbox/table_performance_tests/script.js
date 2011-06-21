(function () {
    // good old store...
    var store = [];

    // execution ground
    init_table( full_data.filter( function ( e ) {
        return e['level'] === 'a';
    }));

    make_zebra();

    $('#clone').click( function ( event ) {
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


    // TODO reimplement it with hash-table instead of filter
    function make_table( list, level ) {
        var level = level || 'a';

        var nodes = list.filter( function ( e ) {
            return e['level'] === level;
        });

        if( nodes.length === 0 ) {
            return;
        }

        if( level === 'a' ) {
            init_table( nodes );
        }
        else {
            add_rows( nodes );
        }

        make_table( list, next_letter( level ));
    }


    function make_zebra() {
        $('tr').each( function ( i ) {
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


    function init_table( list ) {
        var i = 0;

        for( ; i < list.length; ++i ) {
            $('tbody').append( generate_row( list[i] ));
        }
        make_zebra();

        // append new data into store
        store = [].concat( store, list );
    }


    function add_rows( list ) {
        var i = list.length - 1;

        for( ; i >= 0; i -= 1 ) {
            $('#'+list[i]['parent']).after( generate_row( list[i] ));
        }

        // append new data into store
        store = [].concat( store, list );
    }

    function generate_row( node ) {
        var html = [];
        var row;

        // row definition
        html.push( '<tr id="', node['idef'], '" ' );
        html.push( 'data-open="false" ' );
        if( node['level'] === 'a' ) {
            html.push( 'data-selected="false" ' );
        }
        html.push( 'class="', node['level'], ' ', node['parent'],'">' );

        // cells definition
        html.push( '<td class="type', node['leaf'] ? '">' : ' click">' );
        html.push( node['type'], '</td>' );
        html.push( '<td class="name">', node['name'], '</td>' );
        html.push( '<td class="value">', Tools.money(node['v_eu']), '</td>' );
        html.push( '<td class="value">', Tools.money(node['v_nation']), '</td>' );
        html.push( '<td class="value">', Tools.money(node['v_total']), '</td>' );

        html.push( '</tr>' );

        // create & arm row
        row = $( html.join('') );
        row.click( function ( event ) {
            // a-level parent
            var a_root = a_parent( $(this) );
            var open = a_root.attr( 'data-open' );
            var selected = a_root.attr( 'data-selected' );
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
            if( (selected === 'false' && open === 'false') ||
                (selected === 'true'  && open === 'true') ) {

                // the node is closed
                if( $(this).attr( 'data-open' ) === 'false' ) {

                    // children are hidden
                    if( $('.'+node['idef']).length !== 0 ) {
                        with_subtree( node['idef'], $.fn.show );
                    }
                    // children not loaded yet
                    else {
                        var children = full_data.filter( function ( e ) {
                            return e['parent'] === node['idef'];
                        });

                        add_rows( children );
                    }

                    // mark subtree as open
                    $(this).attr( 'data-open', 'true' );
                }
                // the node is closed
                else {
                    // hide subtree
                    with_subtree( node['idef'], $.fn.hide );

                    // mark subtree as closed
                    $(this).attr( 'data-open', 'false' );

                    // if it's a-level node - clear the css highlight/dim
                    if( $(this).hasClass( 'a' ) ) {
                        $(this).removeClass( 'root' );
                        $('.dim').removeClass('dim');
                        $('.highlight').removeClass('highlight');
                        $('.next').removeClass('next');
                    }
                }
            }

            // clear selected attributes and set selection to clicked tree
            $('tr[data-selected=true]').attr('data-selected', 'false');
            a_root.attr('data-selected', 'true');

            make_zebra();
        });

        return row;
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
