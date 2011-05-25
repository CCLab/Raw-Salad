//
//    Table creation functionality
//
var _table = (function () {

    var that = {};


    that.clean_table = function () {
        $('#table').empty();
    };

    that.init_table = function () {
        generate_header();
        generate_table_body();
    };
    
    
    that.add_node = function( id ) {
        var data;
        var schema;
        var html = [];
        var item;
        var i;
        var container;
        var html_result;
        var row_html = [];
        
        // if it's the first time, prepare the top-level data
        if( arguments.length === 0 ) {
            data = _utils.filter( function ( element ) {
                return element['level'] === 'a';
            }, _store.active_rows() );
            container = $('#tbody');
        } 
        else {
            data = _utils.filter( function ( element ) {
                return element['parent'] === id;
            }, _store.active_rows() );
            container = $('#' + id + '> .nodes');
        }
        
        schema = _utils.filter( function ( element ) {
            return element['basic'] === true;
        }, _store.active_columns() );

        for ( i = 0; i < data.length; i += 1 ) {
            item = data[i];
            row_html = generate_row( item, schema );
            html.push( row_html );
        }
        
        html_result = $( html.join('') );
        container.append( html_result );
        
        that.arm_nodes( id );
        _gui.make_zebra();
    };


    // add action listener to newly created nodes
    that.arm_nodes = function ( id ) {
        var node;
        
        // no parameters for a-level nodes
        if( arguments.length === 0 ) {      
            node = $('.a');
        } 
        else {
            node = $('#'+id+' > .nodes');
        }
        
        // add action listener to the cell
        node.find('.data')
            .find('.type')
            .click( function () {
                // get subtree of this level
                var nodes = $(this).parent().next();
                // get level's id
                var id = $(this).parent().parent().attr('id');
                var current_level = $(this).parent().parent();
            
                // if the subtree not loaded yet --> load it
                if( nodes.find('div').length === 0 ) {
                    if ( _db.add_pending_node( id ) ) {
                        _db.download_node( id );
                    }
                }
                else {
                    nodes.toggle();
                }
                
                _gui.highlight( current_level );
            });	                             
        
        node.find( '.data' ).each( function () {
            $(this).children( '.cell' ).equalize_heights();
        });
    };    


    // P R I V A T E   I N T E R F A C E
    var generate_header = function () {
        var i;
        var columns;
        var html = [ '<div id="thead"><div class="data">' ];
        var col, col_type;
        
        // get all the basic view columns definitions        
        columns = _utils.filter( function ( element ) {
                    return element['basic'] === true;
                }, _store.active_columns() );
                
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
        html.push( '<div style="overflow: hidden; height: 1px;">.</div>');
        
        $('#table')
            .append( $( html.join('') ));
    };
    
    
    // TODO >> what is "simple_mode"
    var generate_table_body = function( simple_mode ) {
        var container;
        var html_row;
        var id;
        var item;
        var schema;
        var level;
        var rows;
        
        var next_letter = function( letter ) {
            var number = letter.charCodeAt( 0 );
            return String.fromCharCode( number + 1 );
        };
        
        schema = _utils.filter( function ( element ) {
            return element['basic'] === true;
        }, _store.active_columns() );
                

        for ( level = 'a'; level != 'z'; level = next_letter( level )) {
            rows = _utils.filter( function ( element ) {
                return element['level'] === level;
            }, _store.active_rows() );
            
            for ( i = 0; i < rows.length; i += 1 ) {
                item = rows[ i ];
                if ( !item[ 'parent' ] || simple_mode ) {
                    container = $('#tbody');
                } else {
                    container = $('#'+ item[ 'parent' ] +' > .nodes');
                }
                
                html_row = generate_row( item, schema );
                container.append( html_row.join('') );
                
                if ( !!item[ 'parent' ] ) {
                    id = item[ 'parent' ];                 
                    that.arm_nodes( id );
                }
            }
        }
        
        that.arm_nodes();
        _gui.make_zebra();
    };    
    

    // generates the html code for a single row
    var generate_row = function( item, schema ) {
        var i;
        var col;
        var col_type;
        var html = [];
    
        html.push( '<div id="', item['idef'], '"' );
        html.push( 'class="', item['level'], ' ' );
        html.push( item['leaf'] === true ? 'leaf">' : 'node">' );
        html.push( '<div class="data">' );
        
        // TODO >> recode this loop to make it work with all the datasets
        for ( i = 0; i < schema.length; i += 1 ) {
            col = schema[i];
            
            if ( col['key'] === 'type' || col['key'] === 'name' ) {
                col_type = col['key'] + ' cell';
            } else {
                col_type = 'value cell';
            }				
            
            html.push( '<div class="', col_type, '">' );

            if( col_type === 'value cell' )
            {
                html.push( _utils.money( item[col['key']] ) );
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
        
        return html;
    };    
    
    
    return that;

})();
