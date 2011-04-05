(function () {

    // creates a table with header and a-level data
    var create_table = function() {
    var columns = perspective['columns'];
    var html = [ '<div id="thead"><div class="data">' ];
    var col, col_type;
    var i;
    
    // iterate through columns definitions
    for ( i = 0; i < columns.length; i += 1 ) {
        col = columns[i];
        
        if ( col['key'] === 'type' || col['key'] === 'name' ) {
        col_type = col['key'] + ' cell';
        } else {
        col_type = 'value cell';
        }	
        
        html.push( '<div class="', col_type, '">' );
        html.push( col['label'] );
        html.push( '</div>' );
    }
    html.push( '</div></div>' );
    html.push( '<div id="tbody"></div>' );
        html.push( '<div style="overflow: hidden; height: 1px;">.</div>')

    $('#table').append( $( html.join('') ));
    add_node();
        make_zebra();
    };
    

    // add action listener to newly created nodes
    var arm_nodes = function( id ) {
        var node;
        
        if( id === undefined ) {      
            node = $('.a');
        } else {
            node = $('#'+id+'> .nodes');
        }
        
        node.find('.data').find('.type').click( function () {
            var nodes = $(this).parent().next();
            var id = $(this).parent().parent().attr('id');
            var len = nodes.find('div').length;
            var this_node;
            var children;
            var style;
            
            if( nodes.find('div').length === 0 ) {
                add_node( id );
                highlight( $(this).parent().parent() );
            } else {
                nodes.toggle();
                highlight( $(this).parent().parent() );                
            }
            make_zebra();
        });	                             

        node.find('.checkbox').click( function () {
            var nav_plain = '/site_media/media/img/navigation/02_03.png';
            var nav_active = '/site_media/media/img/navigation/02_03_active.png';
            var nav_over = '/site_media/media/img/navigation/02_03_over.png';

            var nav_img = $('#nav-03');                    
            var nav_current = nav_img.attr('src');

            if( nav_current === nav_plain )
            {
                nav_img.attr('src', nav_active )
                       .hover( 
                           function () {
                               nav_img.attr('src', nav_over ); 
                               nav_img.css('cursor', 'pointer');
                           },                     
                           function () {
                               nav_img.attr('src', nav_active );                            
                           });
            }
            $(this).toggleClass( 'selected' );
        });
    }

    var make_zebra = function () {
        // makes zebra in table
    }
    
    var highlight = function( node ) {        
        // highlight previously clicked group
        
        var node_marked_earlier = $('.marked');
        var i;
        var par;
        
        if ( node.hasClass('a') ) { // a-node clicked
            if ( node.children( 'div.data' ).children().eq(0).hasClass( 'marked' ) ) { // marked a-node clicked
                unmark_a_node( node );
            } else { // not marked a-node clicked
                if ( node_marked_earlier.length > 0 ) { // there is another marked node
                    unmark_a_node( node_marked_earlier.parent().parent() );
                }
                mark_a_node( node );
                add_side_border( node );
                add_bottom_border( node );
            }
        } else { // not a-node clicked
            par = node.parent().parent();
            while ( !par.hasClass( 'a' ) ) {
                par = par.parent().parent(); // find a-node parent of this node
            }
            
            if ( par.children( 'div.data' ).children().eq(0).hasClass( 'marked' ) ) { // node is a descendant of marked a-node
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { // it is the last node
                
                    par.find( 'div.data' ).children().removeClass( 'bottomborder' );
                    add_side_border( node );
                    add_bottom_border( node );
                } else { // node is not the last node
                    add_side_border( node );
                }
            } else { // node is not a descendant of marked a-node
                if ( node_marked_earlier.length > 0 ) { // there is another marked node
                    unmark_a_node( node_marked_earlier.parent().parent() );
                }
                
                mark_a_node( par );
                add_side_border( par );
                
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { // it is the last node
                    par.find( 'div.data' ).children().removeClass( 'bottomborder' );
                    add_bottom_border( par );
                }
            }
        }
    }
    
    // unmark a-node, shade its nodes
    var unmark_a_node = function( node ) {
        node.children( 'div.data' ).children().removeClass( 'marked' );
        node.children( 'div.nodes' ).find( 'div.data' ).children().removeClass( 'leftborder' );
        node.children( 'div.nodes' ).find( 'div.data' ).children().removeClass( 'rightborder' );
        node.children( 'div.nodes' ).find( 'div.data' ).children().removeClass( 'bottomborder' );
        node.children( 'div.data' ).children().addClass( 'darkened' );
        node.children( 'div.nodes' ).find( 'div.data' ).children().addClass( 'darkened' );
    }
    
    // mark a-node, shade other nodes
    var mark_a_node = function( node ) {
        node.children( 'div.data' ).children().removeClass( 'darkened' );
        node.children( 'div.nodes' ).find( 'div.data' ).children().removeClass( 'darkened' );
        node.children( 'div.data' ).children().addClass( 'marked' );        
        node.siblings().find( 'div.data' ).children().addClass( 'darkened' );
    }
    
    // draw left and right borders
    var add_side_border = function( node ) {
        var data = node.children( 'div.nodes' ).find( 'div.data' ).children();
        var columns_number = perspective['columns'].length;
        var rows = data.length / columns_number;
        var i;
        var cell;
        for ( i = 0; i < rows; i += 1 ) {
            data.eq( i * columns_number ).addClass( 'leftborder' );
            data.eq( i * columns_number + columns_number - 1 ).addClass( 'rightborder' )
        }
    }
    
    // draw bottom border
    var add_bottom_border = function( node ) {
        var data = node.children( 'div.nodes' ).find( 'div.data' ).children();
        var columns_number = perspective['columns'].length;
        var rows = data.length / columns_number;
        var i;
        for (i = (rows - 1) * columns_number; i < rows * columns_number; i += 1) {
            data.eq(i).addClass( 'bottomborder' );
        }
    }

    // add nodes to table
    var add_node = function( id ) {
    var data;
    var schema = perspective['columns'];
    var html = [];
    var item;
    var col, col_type = [];
    var i, j;
    var container;
    
    if( arguments.length === 0 ) {
            data = filter( function ( element ) {
                return element['level'] === 'a';
            }, rows );
            container = $('#tbody');
        } else {
            data = filter( function ( element ) {
                return element['parent'] === parseInt( id, 10 );
            }, rows );
            container = $('#' + id + '> .nodes');
        }

    for ( i = 0; i < data.length; i += 1 ) {
        item = data[i];
        html.push( '<div id="', item['id'], '"' );
        html.push( 'class="', item['level'], ' ' );
        html.push( item['leaf'] === true ? 'leaf ' : 'node ' );
        html.push( i % 2 ? 'odd">' : 'even">' );
        html.push( '<div class="data">' );
        
        for ( j = 0; j < schema.length; j += 1 ) {
        col = schema[j];
        
        if ( col['key'] === 'type' || col['key'] === 'name' ) {
            col_type = col['key'] + ' cell';
        } else {
            col_type = 'value cell';
        }				
        
        html.push( '<div class="', col_type, '" ' );
        html.push( 'data-processable="', !!col['processable'], '" ' );				
        html.push( 'data-checkable="', !!col['checkable'], '">' );
        html.push( item[col['key']] );
        if( col['checkable'] === true ) {
            html.push( '<div class="checkbox"></div>' );
        }
            html.push( '</div>' );
        }
        html.push( '</div>' );
        if( item['leaf'] === false ) {
        html.push( '<div class="nodes"></div>' );
        }
        html.push( '</div>' );
    }
    
    container.append( $( html.join('') ));
    arm_nodes( id );
    };

    create_table();
    
})();
