(function () {

    // initialize a table with header and a-level data
    var create_table = function() {
        var columns;
        var html = [ '<div id="thead"><div class="data">' ];
        var col, col_type;
        var i;

        // get all the basic view columns definitions        
        columns = filter( function ( element ) {
                    return element['basic'] === true;
                }, perspective['columns'] );

        // iterate through columns definitions
        for ( i = 0; i < columns.length; i += 1 ) {
            col = columns[i];
            
            // distinguish between type/key and values columns
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

        // create empty table body
        html.push( '<div id="tbody"></div>' );
        html.push( '<div style="overflow: hidden; height: 1px;">.</div>')

        // add new table to the table container
        $('#table').append( $( html.join('') ));
        
        // add a-level rows
        add_node();
    };
    

    // add action listener to newly created nodes
    var arm_nodes = function( id ) {
        var node;
        
        // no parameters for a-level nodes
        if( id === undefined ) {      
            node = $('.a');
        } else {
            node = $('#'+id+'> .nodes');
        }
        
        // add action listener to the cell
        node.find('.data').find('.type').click( function () {
            // get subtree of this level
            var nodes = $(this).parent().next();
            // get level's id
            var id = $(this).parent().parent().attr('id');
            var current_level = $(this).parent().parent();

            // if the subtree not loaded yet --> load it
            if( nodes.find('div').length === 0 ) {
                add_node( id );
            }
            // if there is a subtree already --> toggle it
            else {
                nodes.toggle();
            }
            highlight( current_level );
        });	                             

        // TODO: refactor it with 'selected' class objects list length
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
                        
                $('#selected-items').click( function () {
                    var list = [];
                    $('.selected').each( function () {
                        var text = $(this).parent().siblings('.type').text();
                        text += '\t';
                        text += $(this).parent().text();
                        
                        list.push( text );
                    });
                    var html = ['<ul>'];
                    var i;

                    for( i = 0; i < list.length; ++i ) {
                        html.push( '<li>' + list[i] + '</li>' );
                    }
                    html.push('</ul>');
                    
                    $('#selected-items-list').html('').append( $(html.join(''))).show();
                }).show();                           
                
                $('#add-snapshot').click( function () {
                    $('#snapshot-1').show();
                }).show();                
            }

            $(this).toggleClass( 'selected' );
            
        });
        
        node.find( '.data' ).each( function () {
            $(this).children( '.cell' ).equalize_heights();
        });
    }


    // make light/dark background for rows in table
    var make_zebra = function () {
        
        // get all visible rows
        var visible_list = $('.data').not( ':hidden' );
        
        // change background for each row
        visible_list.each( function ( i, e ) {
            // does row belongs to darkened grounp?
            var darkened = $(this).parents()
                                  .filter('.a')
                                  .children('.data')
                                  .hasClass('darkened');

            if( i % 2 === 0 ) {
                // if darkened, darken
                if( darkened === true ) {
                    $(this).css('background-color', '#f8f8f8');                    
                }
                // or keep it white
                else {
                    $(this).css('background-color', '#fff');                
                }
            }
            else {
                $(this).css('background-color', '#eee');            
            }
        });
    }
    
    
    // TODO refactor it not to involve children
    var highlight = function( node ) {        
        // highlight previously clicked group
        
        var already_marked = $('.marked');
        var i;
        var par;
        
        // a-node clicked
        if ( node.hasClass('a') ) { 
            // it's a marked a-node
            if ( node.children( '.marked' ).length !== 0 ) {
                unmark_a_node( node );
            } else { // not marked a-node clicked
                if ( already_marked.length > 0 ) { // there is another marked node
                    unmark_a_node( already_marked );
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
                    
                    par.find( '.bottomborder' ).removeClass( 'bottomborder' );
                    add_side_border( node );
                    add_bottom_border( node );
                } else { // node is not the last node
                    add_side_border( node );
                }
            } else { // node is not a descendant of marked a-node
                if ( already_marked.length > 0 ) { // there is another marked node
                    unmark_a_node( already_marked );
                }
                
                mark_a_node( par );
                add_side_border( par );
                
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { // it is the last node
                    par.find( 'div.data' ).children().removeClass( 'bottomborder' );
                    add_bottom_border( par );
                }
            }
        } 
        $('.top-border').removeClass('top-border');
        $('.marked').parent().next().children('.data').addClass('top-border');
        make_zebra();                        
    }
    
    // unmark a-node, shade its nodes
    var unmark_a_node = function( node ) {
        node.removeClass( 'marked' );
        node.find( '.data' ).removeClass( 'leftborder' );
        node.find( '.data' ).removeClass( 'rightborder' );
        node.find( '.data' ).removeClass( 'bottomborder' );
        node.find( '.data' ).addClass( 'darkened' );
    }
    
    // mark a-node, shade other nodes
    var mark_a_node = function( node ) {
        node.children( '.data' ).addClass( 'marked' ); 

        node.find( '.data' ).removeClass( 'darkened' );       
        node.siblings().find( '.data' ).addClass( 'darkened' );
    }
    
    // draw left and right borders
    var add_side_border = function( node ) {
        node.find( '.data' )
            .addClass( 'leftborder' )
            .addClass( 'rightborder' );
    }
    
    // draw bottom border
    var add_bottom_border = function( node ) {
        node.find('.data').last().addClass( 'bottomborder' );
    }



    // add nodes to table
    var add_node = function( id ) {
        var data;
        var schema;
        var html = [];
        var item;
        var col, col_type = [];
        var i, j;
        var container;
        var leaf = perspective['leaf'];
        var html_result;
        
        if( arguments.length === 0 ) {
            data = filter( function ( element ) {
                return element['level'] === 'a';
            }, rows );
            container = $('#tbody');
        } else {
            data = filter( function ( element ) {
                return element['parent'] === id;
            }, rows );
            container = $('#' + id + '> .nodes');
        }
        
        schema = filter( function ( element ) {
            return element['basic'] === true;
        }, perspective['columns'] );


        for ( i = 0; i < data.length; i += 1 ) {
            item = data[i];
            html.push( '<div id="', item['idef'], '"' );
            html.push( 'class="', item['level'], ' ' );
            html.push( item['leaf'] === true ? 'leaf">' : 'node">' );
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
                if( col['checkable'] === true ) {
                    html.push( '<div class="checkbox"></div>');
                }
                if( col_type === 'value cell' )
                {
                    html.push( '<span>' );
                    html.push( item[col['key']] );
                    html.push( '</span>' );
                }
                else {
                    html.push( item[col['key']] );
                }    
                html.push( '</div>' );
            }
            html.push( '</div>' );
            if( item['leaf'] !== true ) {
                html.push( '<div class="nodes"></div>' );
            }
            html.push( '</div>' );
        }
        html_result = $( html.join('') );
        container.append( html_result );
        arm_nodes( id );
        make_zebra();
    };

    create_table();
    
})();












