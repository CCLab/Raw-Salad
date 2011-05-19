    var generate_header = function( table_data_object ) {
        var columns;
        var html = [ '<div id="thead"><div class="data">' ];
        var col, col_type;
        var i;
        
        // get all the basic view columns definitions        
        columns = filter( function ( element ) {
                    return element['basic'] === true;
                }, table_data_object['perspective']['columns'] );
                
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
    
    var generate_table_body = function( table_data_object, simple_mode ) {
        var container;
        var html_row;
        var id;
        var item;
        var schema;
        var level;
        var rows;
        
        var nextLetter = function( letter ) {
            var number = letter.charCodeAt( 0 );
            return String.fromCharCode( number + 1 );
        };
        
        schema = filter( function ( element ) {
            return element['basic'] === true;
        }, table_data_object.perspective['columns'] );
                
        for ( level = 'a'; level != 'w'; level = nextLetter( level ) ) {
            rows = filter( function ( element ) {
                return element['level'] === level;
            }, table_data_object['rows'] );
            
            for ( i = 0; i < rows.length; i += 1 ) {
                item = rows[ i ];
                if ( !item[ 'parent' ] || simple_mode ) {
                    container = $('#tbody');
                } else {
                    container = $('#'+ item[ 'parent' ] + '> .nodes');
                }
                
                html_row = generate_row( item, schema );
                container.append( html_row.join('') );
                
                if ( !!item[ 'parent' ] ) {
                    id = item[ 'parent' ];
                    arm_nodes( table_data_object, id );
                }
            }
        }
        
        arm_nodes( table_data_object );
        make_zebra();
        
    };
    
    var generate_row = function( item, schema ) {
        var col;
        var col_type;
        var html = [];
    
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
//            if( col['checkable'] === true ) {
//                html.push( '<div class="checkbox"></div>');
//            }
            if( col_type === 'value cell' )
            {
//                html.push( '<span>' );
                html.push( money( item[col['key']] ) );
//                html.push( '</span>' );
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


    
    // add action listener to newly created nodes
    var arm_nodes = function( table_data_object, id ) {
        var node;
        
        // no parameters for a-level nodes
        if( id === undefined ) {      
            node = $('.a');
        } else {
            node = $('#'+id+'> .nodes');
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
                    if ( add_pending_node( table_data_object, id ) ) {
                        download_node( table_data_object, id );
                    }
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
    };    


   // add nodes to table
    var add_node = function( table_data_object, id ) {
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
            }, table_data_object.rows );
            container = $('#tbody');
        } else {
            data = filter( function ( element ) {
                return element['parent'] === id;
            }, table_data_object.rows );
            container = $('#' + id + '> .nodes');
        }
        
        schema = filter( function ( element ) {
            return element['basic'] === true;
        }, table_data_object.perspective['columns'] );


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
//                if( col['checkable'] === true ) {
//                    html.push( '<div class="checkbox"></div>');
//                }
                if( col_type === 'value cell' )
                {
//                    html.push( '<span>' );
                    html.push( money( item[col['key']] ));
//                    html.push( '</span>' );
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
        arm_nodes( table_data_object, id );
        make_zebra();
    };
