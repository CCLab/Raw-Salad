(function () {

    var tab_data_object = {};
    
    var init_data_object = function( table_data_object ) {
        tab_data_object[ 'pending_nodes' ] = [];
    };
    
    var generate_header = function( table_data_object ) {
        var columns;
        var html = [ '<div id="thead"><div class="data">' ];
        var col, col_type;
        var i;
        
        // get all the basic view columns definitions        
        columns = filter( function ( element ) {
                    return element['basic'] === true;
                }, table_data_object.perspective['columns'] );
                
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
        
        $('#table').append( $( html.join('') ));
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
        node.find('.data').find('.type').click( function () {
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
    };
    
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
        arm_nodes( table_data_object, id );
        make_zebra();
    };

    // downloads requested nodes, appends them to object with other nodes
    // and adds html code for new nodes
    var download_node = function ( table_data_object, id ) {
        var node_to_download_data = {
            "action": "get_node",
            "col_nr": "1",
            "per_nr": "1",
            "par_id": id,
            "add_columns": []
        };
        
        $.ajax({
            data: node_to_download_data,
            dataType: "json",
            success: function( received_data ) {                        
                        var data = table_data_object.rows;
                        var i;
                        var start;
                        
                        for ( i = 0; i < received_data.length; i += 1 ) {
                            data.push( received_data[ i ] );
                        }
                        add_node( table_data_object, id );
                        remove_pending_node( table_data_object, id );
                    }
            });
    };
    
    // adds a node id to list of nodes waiting to be downloaded
    // and inserted in the table
    var add_pending_node = function ( table_data_object, id ) {
        var i;
        var pending_nodes = table_data_object[ 'pending_nodes' ];
        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                return false;
            }
        }
        
        pending_nodes.push( id );

        return true;
    };
    
    // removes a node id from the list of nodes waiting to be downloaded
    var remove_pending_node = function ( table_data_object, id ) {
        var i;
        var pending_nodes = table_data_object[ 'pending_nodes' ];
        
        for ( i = 0; i < pending_nodes.length; i += 1 ) {
            if ( pending_nodes[ i ] === id ) {
                pending_nodes.splice( i, 1 );
                return;
            }
        }
    };
    
    // when new perspective is opened, initial data
    // (perspective info + schema + a-nodes) is downloaded
    $('#choose-perspectives')
        .find('.position')
        .click( function () {
            var init_data_info = {
                "action": "get_init_data",
                "col_nr": "1",
                "per_nr": "1",
            };
            
            $.ajax({
                data: init_data_info,
                dataType: "json",
                success: function( received_data ) {
                        tab_data_object.perspective = received_data.perspective;
                        tab_data_object.rows = received_data.rows;
                        
                        generate_header( tab_data_object );
                        generate_table_body( tab_data_object );
                    }
                });
        });
        
    var sort = function ( table_data_object, sett ) {
        
        var new_table_data_object = {};
        $.extend( true, new_table_data_object, table_data_object );
        
        Utilities.prepare_sorting_setting( sett );
        Utilities.sort( new_table_data_object[ 'rows' ], sett );

        table_data_object[ 'rows' ] = new_table_data_object[ 'rows' ];
    };

    $('#sort-button')
        .click( function () {

            // setting that should be obtained from popup window
            var sett = [
                {
                    "pref": 1,
                    "name": "v_eu"
                }
            ];
            
            
            
            sort( tab_data_object, sett );
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object );
        });
        
    $('#filter-button')
        .click( function () {
            
            var mask = [
                //{ name: 'v_eu', pref: -1, value: 50000 },
                { name: 'name', pref: 1, value: 'gospod' }
            ];
            
            tab_data_object[ 'rows' ] = Utilities.filter( tab_data_object[ 'rows' ], mask );
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object, true );
        });

    init_data_object( tab_data_object );

})();

