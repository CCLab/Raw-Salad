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
				this_node = $(this).parent().parent().children('div.data').children();
				children = $(this).parent().parent().children();
				style = $(this).parent().parent().children('div.nodes').attr('style');
				
				// if this node isn't watched and forgotten or has hidden children
				if ( ((!this_node.hasClass( 'forgotten' )) && (!this_node.hasClass( 'watched' )) ) ||
					((children.length > 1) && (style === "display: none;")) ) {
					nodes.toggle();
				}
				highlight( $(this).parent().parent() );                
            }
            make_zebra();
        });	                             

        node.find('.checkbox').click( function () {
            $(this).toggleClass( 'selected' );
        });
    }

    var make_zebra = function () {
        // makes zebra in table
    }
    
    var highlight = function( node ) {
		var opened_earlier = $(".open");
		var watched_earlier = $(".watched");
		var children;
		var parent;
		var siblings;
		var this_node;
		var descendants;
		
        // highlight previously clicked group
		
		/*	algorithm of colouring nodes		
		if (was_recently_open) {
			his_children_lost_colors;
			if (is a-node) {
				it_loses_his_color;
			} else {
				his_parent_becomes_open;
				he_his_brothers_and_their_children_become_watched;
			}
		} else {
			recently_open_become_forgotten;
			recently_watched_become_forgotten;
			this_node_becomes_open;
			his_descendants_become_watched;
		}
		*/
		if (node.children().length > 1 &&
			node.children('div.data').children().hasClass( 'open' ))
		{
			children = node.children('div.nodes').find('div.data').children();
			children.removeClass( 'forgotten' );
			children.removeClass( 'watched' );
			
			if (node.hasClass('a')) {
				node.children('div.data').children().removeClass( 'open' );
			} else {
				parent = node.parent().parent().children('div.data').children();
				parent.removeClass( 'forgotten' );
				parent.addClass( 'open' );
				
				node.children('div.data').children().removeClass( 'open' );
				
				siblings = node.parent().children().find('div.data').children();
				siblings.removeClass( 'forgotten' );
				siblings.addClass( 'watched' );
			}
			
		} else {
			opened_earlier.removeClass( 'open' );
			opened_earlier.addClass( 'forgotten' );
			watched_earlier.removeClass( 'watched' );
			watched_earlier.addClass( 'forgotten' );
			
			this_node = node.children('div.data').children();
			this_node.removeClass( 'watched' );
			this_node.removeClass( 'forgotten' );
			this_node.addClass( 'open' );
			
			descendants = node.children('div.nodes').children().find('div.data').children();
			descendants.removeClass( 'forgotten' );
			descendants.removeClass( 'open' );
			descendants.addClass( 'watched' );
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
