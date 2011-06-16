(function () {
    var i, f;
    var html = [];

    make_table();
    make_zebra();

    function kill_children( id ) {
        $('.'+id).each( function () {
            kill_children( $(this).attr('id') );
            $(this).remove();
        });
    }

    function make_table( level ) {
        var level = level || 'a';
        var next_letter = function( letter ) {
            var number = letter.charCodeAt( 0 );
            return String.fromCharCode( number + 1 );
        };

        var nodes = full_data.filter( function ( e ) {
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

        make_table( next_letter( level ));
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
        var i;
        var html = [];
        var node;
        var row;

        for( i = 0; i < list.length; ++i ) {
            node = list[i];
            html =[];

            html.push( '<tr id="', node['idef'], '" class="a">' );
            html.push( '<td class="type click">', node['type'], '</td>' );
            html.push( '<td class="name">', node['name'], '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_eu']), '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_nation']), '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_total']), '</td>' );
            html.push( '</tr>' );

            (function ( id ) {
                row = $(html.join('')).click( function ( event ) {
                    kill_children( id );
                    make_zebra();
                });
            })( node['idef'] );

            $('tbody').append( row );
        }
    }


    function add_rows( list ) {
        var i;
        var html;
        var node;
        var row;

        for( i = list.length-1; i >= 0; i -= 1 ) {
            node = list[i];
            html = [];

            html.push( '<tr id="', node['idef'], '" ' );
            html.push( 'class="', node['level'], ' ', node['parent'], '">' );
            html.push( '<td class="type', node['leaf'] ? '">' : ' click">' );
            html.push( node['type'], '</td>' );
            html.push( '<td class="name">', node['name'], '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_eu']), '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_nation']), '</td>' );
            html.push( '<td class="value">', Tools.money(node['v_total']), '</td>' );
            html.push( '</tr>' );

            (function ( id ) {
                row = $(html.join('')).click( function ( event ) {
                    kill_children( id );
                    make_zebra();
                });
            })( node['idef'] );

            $('#'+node['parent']).after( row );
        }
    }
})();
