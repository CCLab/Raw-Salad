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
            $(this).toggleClass( 'selected' );
        });
    }

    var make_zebra = function () {
        // makes zebra in table
    }
    
    var highlight = function( node ) {
        // highlight previously clicked group
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
