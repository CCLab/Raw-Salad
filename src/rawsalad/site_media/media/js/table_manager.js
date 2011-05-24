(function () {
    var i;
    var tab_data_object;
    var sheet_list = {
        'active_sheet': 0,
        'sheets': [ { } ],
        'basic_sheet': {},
        'basic_pure': true
    };
    
    tab_data_object = sheet_list['sheets'][sheet_list['active_sheet']];
    
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
        var is_hidden;
        
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
                    is_hidden = item[ 'hidden' ];
                    arm_nodes( table_data_object, id, is_hidden );
                }
            }
        }
        
        arm_nodes( table_data_object );
        hide_hidden_nodes( table_data_object );
        
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
    var arm_nodes = function( table_data_object, id, is_hidden ) {
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
                    toggle_hidden_param( table_data_object, id );
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
    
    var toggle_hidden_param = function( table_data_object, id ) {
        var parent = filter( function ( element ) {
                return element['idef'] === id;
            }, table_data_object.rows );
        //Assert.assert( !parent['leaf'], 
        //               "cant hide leaf's children!!!" );
            
        parent[0]['hidden'] = !parent[0]['hidden'];
    };
    
    var hide_hidden_nodes = function( table_data_object ) {
        var parents_with_hidden_children;
        var node;
        var i;
        var id;
        var hidden_children;
        
        parents_with_hidden_children = filter( function ( element ) {
                return !!element['hidden'];
            }, table_data_object.rows );
            
        for ( i = 0; i < parents_with_hidden_children.length; i += 1 ) {
            id = parents_with_hidden_children[i]['idef'];
            node = $('#'+id);
            hidden_children = node.find('.data')
                                  .find('.type')
                                  .parent()
                                  .next();
                           
           hidden_children.toggle();
        }
    }
    
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
        var leaf = table_data_object.perspective['leaf'];
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

    // downloads requested nodes, appends them to object with other nodes
    // and adds html code for new nodes
    var download_node = function ( table_data, id ) {
        var node_to_download_data = {
            "action": "get_node",
            "col_nr": table_data.col_nr, 
            "per_nr": table_data.per_nr,
            "par_id": id,
            "add_columns": []
        };

        $.ajax({
            data: node_to_download_data,
            dataType: "json",
            success: function( received_data ) {                        
                        var data = table_data.rows;
                        var i;
                        var start;

                        for ( i = 0; i < received_data.length; i += 1 ) {
                            data.push( received_data[ i ] );
                        }
                        add_node( table_data, id );
                        remove_pending_node( table_data, id );
                        
                        if ( sheet_list["active_sheet"] === 0 ) {
                            sheet_list["basic_pure"] = false;
                        }
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

    $('#choose-collections')
        .find('.position')
        .hover( 
            function () {
                $(this).css('background-color', '#4abff7').css('cursor', 'pointer');
                $(this).find('.position-title').css('color', '#fff');
                $(this).find('.position-more').css('color', '#fff');
            },
            function () {
                $(this).css('background-color', '#fff');
                $(this).find('.position-title').css('color', '#009fe3');
                $(this).find('.position-more').css('color', '#009fe3');
            })
        .click( function () {
            var init_data_info = {
                action: "choose_collection",
                col_nr: $(this).attr('data-collection-number')
            };

            $.ajax({
                data: init_data_info,
                dataType: "json",
                success: function( received_data ) {
                    var html = [];

                    $('#choose-collection-name').html(received_data.collection.name);

                    for( i = 0; i < received_data.perspectives.length; ++i ) {
                        html.push( '<div class="position" data-index="', i, '" ');
                      
                        html.push( 'data-collection="', received_data.collection.number, '">' );
                        html.push( '<div class="position-title">' );
                        html.push( received_data.perspectives[i].name );
                        html.push( '</div>' );
                        html.push( '<div class="position-desc">' );
                        html.push( received_data.perspectives[i].description );
                        html.push( '</div>' );
                        html.push( '<div class="position-more">' );
                        html.push( 'Zobacz dane' );
                        html.push( '</div></div>' );
                    }
                    $('#info-text').html('Każda pozycja na liście udostępnia te same dane, lecz inaczej zorgranizowane.');
                    $('#choose-collections').toggle();
                    $('#choose-perspectives-list').append( $(html.join('')) );
                    $('#choose-perspectives-list')
                        .find('.position')
                        .click( function () {
                            var init_data_info = {
                                "action": "get_init_data",
                                "col_nr": $(this).attr('data-collection'),
                                "per_nr": $(this).attr('data-index'),
                                "issue": $(this).attr('data-issue')
                            };

                            $.ajax({
                                data: init_data_info,
                                dataType: "json",
                                success: function( received_data ) {
                                    tab_data_object.perspective = received_data.perspective;
                                    tab_data_object.rows = received_data.rows;
                                    tab_data_object["col_nr"] = init_data_info["col_nr"];
                                    tab_data_object["per_nr"] = init_data_info["per_nr"];
                                    tab_data_object["name"] = "Arkusz " + sheet_list["sheets"].length.toString();
                                    
                                    $.extend( true, sheet_list["basic_sheet"], tab_data_object );
                                    sheet_list["basic_pure"] = true;

                                    generate_header( tab_data_object );
                                    generate_table_body( tab_data_object );
                                    
                                    $('#choose-panel').slideUp(400);
                                    $('#application').fadeIn(400).animate({ opacity: 1 }, 300 );
                                    $('#open-close-choose-panel').show().html('zmień dane');
                                }
                            });
                        })
                        .hover( 
                            function () {
                                $(this).css('background-color', '#4abff7').css('cursor', 'pointer');
                                $(this).find('.position-title').css('color', '#fff');
                                $(this).find('.position-more').css('color', '#fff');
                            },
                            function () {
                                $(this).css('background-color', '#fff');
                                $(this).find('.position-title').css('color', '#009fe3');
                                $(this).find('.position-more').css('color', '#009fe3');
                            }
                        );
                    $('#choose-perspectives').toggle();                        
                }
            });
        });

        
    var sort = function ( table_data_object, sett ) {
        var id = "idef";
        
        var new_table_data_object = {};
        
        Utilities.prepare_sorting_setting( sett, id );
        Utilities.sort( table_data_object[ 'rows' ], sett );
    };


    $('#sort-button')
        .click( function () {
            $('#filter-form').hide();        
            $('#sort-form').html('').toggle();  
            add_sort_key();                      
        });

    $('#sort-form')
        .submit( function () {

            var column, order;
            var settings = [];
            var i, len = $('#sort-form select').length;
            
            for( i = 0; i < len; ++i ) {
                column = $('.key-'+i+' option:selected').val();
                if( column === "null" ) {
                    if( i === 1 ) {
                        $(this).hide();
                        return false;
                    }
                    else {
                        break;
                    }
                }
                order = parseInt($('.key-'+i+':radio:checked').val());                 

                settings.push(
                    {
                        "pref": order,
                        "name": column
                    }
                );
            }

            sort( tab_data_object, settings );
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object );
            
            $(this).hide();
            
            return false;
        });


    function add_sort_key( ) {
        var i, key;
        var perspective = tab_data_object['perspective']['columns'];
        var columns = [];
        var html = [];

        key = $('#sort-form > div').length;

        for( i = 0; i < perspective.length; ++i ) {
            if( perspective[i]['basic'] === true && 
                perspective[i]['processable'] === true ) {
                columns.push( 
                    {
                        name: perspective[i]['key'],
                        label: perspective[i]['label']
                    }
                );
            }
        }

        if( key === 2 ) {
            $('#add-sort-key' ).remove();
        }

        html.push( '<div id="key-', key, '">' );
        // columns select list
        html.push( '<select name="columns" class="key-', key, '">' );
        html.push( '<option value="null" class="key-', key, '" selected>' );
        html.push( 'Wybierz kolumnę</option>' );
        
        // TODO don't include already selected colmuns
        for( i = 0; i < columns.length; ++i ) {
            html.push( '<option value="', columns[i]['name'], '" class="key-', key, '">' );
            html.push( columns[i]['label'], '</option>' );
        }
        
        html.push( '</select>' );
        // ascending/descending radio buttons
        html.push( 'Rosnąco <input class="radio key-', key, '" type="radio" ' );
        html.push( 'name="key-', key, '-order" value="-1" checked />' );
        html.push( 'Malejąco <input class="radio key-', key, '" type="radio" ' );
        html.push( 'name="key-', key, '-order" value="1" />' );

        if( key === 0 ) {
            html.push( '<div id="add-sort-key">+</div>' );
            html.push( '<input type="submit" value="Sortuj" />' );
        }
        html.push( '</div>' );

        $('#sort-form').append( $(html.join('')) );

        if( key === 0 ) {
            $('#add-sort-key').click( function () {
                add_sort_key();   
            });
        }
    }
    
    function create_new_sheet( data_object, filtered_sheet ) {
        var html = [];
        var new_sheet_nr = sheet_list["sheets"].length;
        var new_sheet = { };
        
        $.extend( true, new_sheet, data_object );
        new_sheet["col_nr"] = data_object["col_nr"];
        new_sheet["per_nr"] = data_object["per_nr"];
        new_sheet["name"] = "Arkusz " + new_sheet_nr.toString();
        sheet_list["sheets"].push( new_sheet );
        
        if ( sheet_list["active_sheet"] === 0 && !sheet_list["basic_pure"] ) {
            sheet_list["sheets"][0] = {};
            $.extend( true, sheet_list["sheets"][0], sheet_list["basic_sheet"] );
            sheet_list["basic_pure"] = true;
        }
        
        sheet_list["active_sheet"] = new_sheet_nr;
        
        html.push('<div id="snap-' + new_sheet_nr.toString() + '" class="snapshot active">');
        html.push(new_sheet["name"]);
        html.push('</div>');
        html.push('<div id="save-snapshot">');
        html.push('Zapisz arkusz');
        html.push('</div>');
        
        $('#save-snapshot').remove();
        $('#snapshots').append( $( html.join('') ));
        $('#snapshots')
            .find('#snap-' + new_sheet_nr.toString())
            .each( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');
            })
            .click( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');
                if ( sheet_list["active_sheet"] !== new_sheet_nr ) {
                    sheet_list["active_sheet"] = new_sheet_nr;
                    tab_data_object = sheet_list["sheets"][new_sheet_nr];
                    $('#table').empty();
                    generate_header( tab_data_object );
                    generate_table_body( tab_data_object, filtered_sheet );
                }                
            });
        $('#save-snapshot')
            .click( function () {
                create_new_sheet( tab_data_object );
            });
        
        return new_sheet_nr;
    }

    $('#filter-button')
        .click( function () {
            $('#filter-form').toggle(); 
            $('#sort-form').hide();               
        });

    $('#filter-form')
        .submit( function () {

            var column, operation, query;
            var mask = [];
            var i, len = $('#filter-form select').length / 2;
            var tmp, type;
            var new_data_object, new_sheet_nr;
            for( i = 1; i < len; ++i ) {
                column = $('#filter-'+i+'-columns option:selected').val();
                if( column === "null" ) {
                    if( i === 1 ) {
                        $(this).hide();
                        return false;
                    }
                    else {
                        break;
                    }
                }                
                
                type = filter( function ( e ) {
                    return e['key'] === column;
                }, tab_data_object['perspective']['columns'] )[0]['type'];
                
                operation = $('#filter-'+i+'-operations option:selected').val();;
                query = $('#filter-'+i+'-query').val();

                tmp = parseInt( query, 10 ) / 1000;
                // if the column if numeric - check if the query is so
                if( type === 'number' ) {
                    // crazy way to check if tmp is a number!
                    if( !!tmp === true || tmp === 0 ) {
                        query = tmp;
                    }
                    else {
                        // characters for numeric column -- do nothing & quit
                        $(this).hide();            
                        return false;
                    }
                }
                
                mask.push(
                    {
                       name: column, 
                       pref: operation, 
                       value: query
                    }
                );
            }
            
            new_data_object = {};
            $.extend( true, new_data_object, tab_data_object );
            new_data_object['rows'] = Utilities.filter( tab_data_object['rows'], mask );
            new_sheet_nr = create_new_sheet( new_data_object, true );
            
            tab_data_object = sheet_list["sheets"][new_sheet_nr];
            
            $('#table').empty();
            generate_header( tab_data_object );
            generate_table_body( tab_data_object, true );

            $(this).hide();
                        
            return false;
       });
        



 
    for( i = 1; i <= $('#sort-form select').length; ++i ) {
        if( i > 1 ) {
            $('#key-'+i).hide();
        }

        (function (i) {
            $('#sort-form select.key-'+i).change( function () {    
                if( $('.key-'+i+' option:selected').val() !== "null" ) {
                    $('#key-'+(i+1)).show();
                }
            });
        })(i);
    }
    
    $('#save-snapshot')
        .click( function () {
            create_new_sheet( tab_data_object );
        });
        
    $('#basic-snapshot')
        .click( function () {
            $('.snapshot').removeClass('active');
            $(this).addClass('active');

            if ( sheet_list["active_sheet"] !== 0 ) {
                sheet_list["active_sheet"] = 0;
                tab_data_object = sheet_list["sheets"][0];
                
                $('#table').empty();
                generate_header( tab_data_object );
                generate_table_body( tab_data_object );
            }
        });

    $('#sort-form').hide();
    $('#filter-form').hide();    
    init_data_object( tab_data_object );

    $('#download-button').click( function () {

        $.ajax({
            url: '/download/',
            type: 'POST',
            data: { sheet: sheet_list["sheets"][sheet_list["active_sheet"]] },
            success: function () {
                console.log( "Works fine" );
            }
        });
    });

})();
