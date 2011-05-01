(function () {
    
    // tworzy tabele przy pomocy obiektu json
    var generate_table_header = function( table_data_object ) {
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
        
        return html;
    };
    
    var generate_table_data = function( table_data_object ) {
        var data;
        var schema;
        var html = [];
        var item;
        var col, col_type = [];
        var i, j;
        var container;
        var leaf = perspective['leaf'];
        var html_result;
        
        data = table_data_object.rows;
        
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
                download_node( table_data_object, id );
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
    
    var reset_table = function( table_data_object ) {
        var i;
        var not_leaf_nodes = filter( function ( element ) {
                return !!element['leaf'];
            }, table_data_object.rows );
            
        $('#tbody').empty();
        add_node( table_data_object );
        
            
        for ( i = 0; i < not_leaf_nodes.length; i += 1 ) {
            add_node( table_data_object, not_leaf_nodes[ i ] );
        }
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
        
        $.ajaxSetup({ 
            beforeSend: function(xhr, settings) {
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie != '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = jQuery.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            } 
        });
        
        $.ajax({
            type: "POST",
            data: node_to_download_data,
            dataType: "json",
            success: function( received_data ) {                        
                        var data = table_data_object.rows;
                        var i;
                        var start;
                        for ( i = 0; i < data.length; i += 1 ) {
                            if ( data[ i ].idef === id ) {
                                start = i + 1;
                                break;
                            }
                        }
                        
                        for ( i = 0; i < received_data.length; i += 1 ) {
                            data.splice( start + i, 0, received_data[ i ] );
                        }
                        add_node( table_data_object, id );
                    }
            });        
    };
    
    var td_object = {
        "perspective": {
            "name": "budzet_zadaniowy", 
            "idef": 1, 
            "collection": "dd_budg2011_go", 
            "perspective": "Bud\u017cet zadaniowy", 
            "columns": [
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "idef", 
                    "label": "Numer"
                }, 
                {
                    "type": "string", 
                    "label": "Typ", 
                    "processable": true, 
                    "key": "type", 
                    "basic": true
                }, 
                {
                    "type": "string", 
                    "label": "Nazwa", 
                    "processable": true, 
                    "key": "name", 
                    "basic": true
                }, 
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "czesc", 
                    "label": "Cz\u0119\u015b\u0107"
                }, 
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "cel", 
                    "label": "Cel"
                }, 
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "miernik_nazwa", 
                    "label": "Miernik"
                }, 
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "miernik_wartosc_bazowa", 
                    "label": "Warto\u015b\u0107 bazowa"
                }, 
                {
                    "type": "string", 
                    "processable": true, 
                    "key": "miernik_wartosc_rb", 
                    "label": "Warto\u015b\u0107 br."
                }, 
                {
                    "label": "OG\u00d3\u0141EM", 
                    "processable": true, 
                    "key": "v_total", 
                    "basic": true, 
                    "checkable": true, 
                    "type": "number"
                }, 
                {
                    "label": "Bud\u017cet Pa\u0144stwa", 
                    "processable": true, 
                    "key": "v_nation", 
                    "basic": true, 
                    "checkable": true, 
                    "type": "number"
                }, 
                {
                    "label": "Środki Europejskie", 
                    "processable": true, 
                    "key": "v_eu", 
                    "basic": true, 
                    "checkable": true, 
                    "type": "number"
                }
            ]
        },
        
        "rows": [
            {
                "leaf": false, 
                "name": "ZARZ\u0104DZANIE PA\u0143STWEM", 
                "parent": null, 
                "level": "a", 
                "idef": "1", 
                "v_eu": 25140, 
                "v_total": 1561521, 
                "v_nation": 1536381, 
                "type": "FUNKCJA 1"
            },
            {
                "leaf": false, 
                "name": "BEZPIECZE\u0143STWO WEWN\u0118TRZNE I PORZ\u0104DEK PUBLICZNY", 
                "parent": null, 
                "level": "a", 
                "idef": "2", 
                "v_eu": 58779, 
                "v_total": 14170616, 
                "v_nation": 14111837, 
                "type": "FUNKCJA 2"
            }, 
            {
                "leaf": false, 
                "name": "EDUKACJA, WYCHOWANIE I OPIEKA", 
                "parent": null, 
                "level": "a", 
                "idef": "3", 
                "v_eu": 1016384, 
                "v_total": 14379196, 
                "v_nation": 13362812, 
                "type": "FUNKCJA 3"
            }
        ]
    };
    
    var show_header = function( html_code ) {
        $('#table').append( $( html_code.join('') ));
    };
    var show_rows = function( html_code, id ) {
        $('#tbody').append( $( html_code.join('') ));
        arm_nodes( td_object, id );
        make_zebra();
    };
    
    show_header( generate_table_header( td_object ) );
    show_rows( generate_table_data( td_object ) );
    
})();

