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
    function kill_children( id, what ) {
        $('tr.'+id).each( function () {
            kill_children( $(this).attr('id'), what );

            if( what === 'hide' ) {
                $(this).hide();
            }
            else {
                $(this).show();
            }
        });
    }


    function next_letter( letter ) {
        var number = letter.charCodeAt( 0 );

        return String.fromCharCode( number + 1 );
    }


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
            if( $(this).attr( 'data-open' ) === 'false' ) {

                if( $('.'+node['idef']).length !== 0 ) {
                    kill_children( node['idef'], 'show' );
                }
                else {
                    var children = full_data.filter( function ( e ) {
                        return e['parent'] === node['idef'];
                    });

                    add_rows( children );
                }
                $(this).attr( 'data-open', 'true' );
            }
            else {
                kill_children( node['idef'], 'hide' );
                $(this).attr( 'data-open', 'false' );
            }
            make_zebra();
        });

        return row;
    }

})();
