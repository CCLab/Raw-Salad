//
//  Object responsible for GUI manipulation
//

var _gui = (function () {

    // P U B L I C  I N T E R F A C E
    var that = {};
   
    that.init_gui = function () {
        // hide what's not needed now
        $('#sort-form').hide();
        $('#filter-form').hide();  
        $('#download-form').hide();                       
        $('#download-button').click( _download.current_sheet );
        $('#application').hide();  
        
        // arm open/close button and hide it!
        $('#open-close-choose-panel')
            .click( function () {
                // if choose panel is open
                if( $('#choose-panel:visible').length > 0 ) {
                    that.hide_choose_panel();
                }
                else {
                    that.show_choose_panel();                
                }    
            })
            .hide();
        
        // arm back-to-datasets button
        $('#back-to-datasets')
            .hover(
                function () {
                    $(this)
                        .attr( 'src', '/site_media/img/datasets_over.png' )
                        .css('cursor', 'pointer');                
                },
                function () {
                    $(this).attr( 'src', '/site_media/img/datasets.png' );
                }
            )
            .click( function () {
                $('#info-title')
                    .html('Dostępne kolekcje');
                $('#info-text')
                    .html('Wybierz jedną z dostępnych kolekcji danych.');

                $(this)
                    .hide();
                $('#choose-perspectives')
                    .hide();
                $('#choose-datasets')
                    .show();            

                // clear the perspectives list
                $('#choose-perspectives')
                    .html('');
            })
            .hide();
            
        $('#choose-perspectives').hide();            
        init_choose_panel();
    };
    

    var init_choose_panel = function () {
        var i;
        var html = [];
        var datasets = _store.meta_datasets();
        var len = datasets.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );
                
        html.push( '<div class="left">' );
        for( i = 0; i < len; i += 1 ) {
            html.push( '<div class="position" ');
            html.push( 'data-set-id="', datasets[i]['idef'], '">' );            
            html.push( '<div class="title">' );
            html.push( datasets[i]['name'] );
            html.push( '</div>' );
            html.push( '<div class="description">' );
            html.push( datasets[i]['description'] );
            html.push( '</div>' );            
            html.push( '<div class="more">Zobacz dane</div>' );
            html.push( '</div>' );

            if( i === mid ) {
                html.push( '</div><div class="left second-column">' );
            }
        }
        html.push( '</div>' );
        
        $('#choose-datasets')
            .append( $( html.join('') ))
            .find( '.position' )
            .find( '.more' )
            .click( function () {
                var dataset_id = $(this).parent().attr( 'data-set-id' );
                
                create_perspectives_panel( dataset_id );
                
                $('#choose-datasets')
                    .hide();
            });
    };
    
    var create_perspectives_panel = function ( dataset_id ) {
        var i, j;
        var html = [];
        var perspectives = _store.meta_perspectives( dataset_id );
        var len = perspectives.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );
        var issues;   
        var name;        

        html.push( '<div class="left">' );
        for( i = 0; i < len; i += 1 ) {
            issues = perspectives[i]['issues'];
            
            html.push( '<div class="position" ' );
            html.push( 'data-set-id="', dataset_id, '" ' );            
            html.push( 'data-per-id="', perspectives[i]['idef'], '">' );            
            html.push( '<div class="title">' );
            html.push( perspectives[i]['name'] );
            html.push( '</div>' );
            html.push( '<div class="description">' );
            html.push( perspectives[i]['description'] );
            html.push( '</div>' );          
            // iterates in revers order because of CSS "float: right"
            for( j = issues.length-1; j >= 0; j -= 1 ) {
                html.push( '<div class="more" ' );
                html.push( 'data-issue="', issues[j], '">' );                            
                html.push( issues[j] );
                html.push( '</div>' );
            }
            html.push( '<div class="more-desc">Zobacz dane:</div>' );
            html.push( '</div>' );

            if( i === mid ) {
                html.push( '</div><div class="left second-column">' );
            }            
        }
        html.push( '</div>' );
        
        $('#info-title')
            .html( _store.meta_datasets()[ dataset_id ]['name'] );
        $('#info-text')
            .html('Wybierz jedno z wydań danych.');

        $('#back-to-datasets')
            .show();
            
        $('#choose-perspectives')
            .append( $( html.join('') ))
            .show()
            .find( '.position' )
            .find('.more' )
            .click( function () {
                var id = {
                    dataset: $(this).parent().attr( 'data-set-id' ),
                    perspective: $(this).parent().attr( 'data-per-id' ),
                    issue: $(this).attr( 'data-issue' )
                };
                                    
                // if new group is created, get data and show table   
                if( _store.create_new_group( id ) ) {
                    // get top-level data from db                
                    _db.get_init_data();
                    name = id['dataset'] + '-' + id['perspective'] + '-' + id['issue'];
                    that.create_basic_snapshot_button( {'basic_snapshot_name': name} );
                } 
                else {
                    // go back to application with focus on requested sheet
                    that.hide_choose_panel();
                }
            });
    };
    

    // used once when some perspective is chosen for the very first time
    that.init_app = function () {
        $('#open-close-choose-panel')    
            .show();
            
        $('#application')
            .fadeIn( 400 );
            
        that.hide_choose_panel();
    }

    
    that.show_choose_panel = function () {
        $('#choose-panel')
            .slideDown(400);
            
        $('#application')
            .animate({ opacity: 0.25 }, 300 );
            
        $('#open-close-choose-panel')
            .html('zwiń'); 
    }
    

    that.hide_choose_panel = function () {   
        $('#choose-panel')
            .slideUp( 400 );
            
        _gui.make_zebra();

        $('#thead').find( '.data' ).each( function () {
            $(this).children( '.cell' ).equalize_heights();
        });        

        $('.a').find( '.data' ).each( function () {
            $(this).children( '.cell' ).equalize_heights();
        });        

        $('#application')
            .animate({ opacity: 1 }, 300 );
            
        $('#open-close-choose-panel')
            .html('zmień dane');
    };
    


   
    that.make_zebra = function () {
        // get all visible rows
        var visible_list = $('.data').not( ':hidden' );

        _assert.not_equal( visible_list.length, 0,
                           "No visible elements in the table" );
                                   
        // change background for each row
        visible_list.each( function ( i, e ) {
            // does row belongs to darkened grounp?
            var darkened = $(this).parents()
                                  .filter('.a')
                                  .children('.data')
                                  .hasClass('darkened');

            // TODO - refactor it with CSS classes!!!
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
    
    
    that.equalize_table = function () {
        $('#thead').find( '.data' ).each( function () {
            $(this).children( '.cell' ).equalize_heights();
        });
        
        $('.node').each( function () {
            $(this).find( '.data' ).each( function () {
                $(this).children( '.cell' ).equalize_heights();
            });
        });        
    };
    
    
    // TODO refactor it not to involve children
    that.highlight = function( node ) {        

        // highlight previously clicked group
        var already_marked = $('.marked');
        var i;
        var par;
        
        // a-node clicked
        if ( node.hasClass('a') ) { 
            // it's a marked a-node
            if ( node.children( '.marked' ).length !== 0 ) {
                unmark_a_node( node );
            } 
            else { // not marked a-node clicked
                if ( already_marked.length > 0 ) { // there is another marked node
                    unmark_a_node( already_marked );
                }
                mark_a_node( node );
                add_side_border( node );
                add_bottom_border( node );
            }
        } 
        else { // not a-node clicked
            
            // find a-node parent of this node
            par = node.parent().parent();
            while ( !par.hasClass( 'a' ) ) {
                par = par.parent().parent(); 
            }
            
            // node is a descendant of marked a-node
            if ( par.children( 'div.data' ).children().eq(0).hasClass( 'marked' ) ) { 
                // it is the last node
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { 
                    
                    par.find( '.bottomborder' ).removeClass( 'bottomborder' );
                    add_side_border( node );
                    add_bottom_border( node );
                } 
                else { 
                    add_side_border( node );
                }
            } else { 
                // there is another marked node
                if ( already_marked.length > 0 ) { 
                    unmark_a_node( already_marked );
                }
                
                mark_a_node( par );
                add_side_border( par );
                
                // it is the last node
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { 
                    par.find( 'div.data' ).children().removeClass( 'bottomborder' );
                    add_bottom_border( par );
                }
            }
        } 
        
        $('.top-border').removeClass('top-border');
        $('.marked').parent().next().children('.data').addClass('top-border');

        that.make_zebra();                        
    }
    
    
    
    that.create_sheet_tab = function ( sheet_name, new_sheet_nr, filtered_sheet ) {
        var html = [];
        
        html.push('<div id="snap-' + new_sheet_nr.toString() + '" class="snapshot active">');
        html.push(sheet_name);
        html.push('</div>');
        
        html.push('<div id="save-snapshot">');
        html.push('Zapisz arkusz');
        html.push('</div>');
        
        //TODO: change it so that adding a new sheet does not involve
        //      removing and adding New sheet button
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
                if ( _store.active_sheet_index() !== new_sheet_nr ) {
                    _sheet.change_active_sheet( new_sheet_nr );
                }
            });
            
        $('#save-snapshot')
            .click( function () {
                _sheet.create_new_sheet( _store.active_sheet(), "Nowy arkusz" );
            });
    };
    
    that.create_basic_snapshot_button = function( args ) {
        var html = [];
        var max_group_nr;
        var name = args.basic_snapshot_name;
        
        max_group_nr = _store.max_group_nr() - 1;
        html.push('<div id="basic-snapshot-' + max_group_nr.toString() +
                  '" class="basic-snapshot active">');
        html.push(name);
        html.push('</div>');
        
        $('#snapshots').append( $( html.join('') ));
        
        $('#basic-snapshot-' + max_group_nr.toString())
            .click( function () {
                $('.basic-snapshot').removeClass('active');
                $(this).addClass('active');
                _sheet.show_basic_sheet( {'group_nr': max_group_nr} );
            });
    };
    
    
    // P R I V A T E   I N T E R F A C E
    
    // unmark a-node, shade its nodes
    var unmark_a_node = function( node ) {
        node.find( '.marked' ).removeClass( 'marked' );
        node.find( '.data' ).removeClass( 'leftborder' );
        node.find( '.data' ).removeClass( 'rightborder' );
        node.find( '.data' ).removeClass( 'bottomborder' );
        node.find( '.data' ).addClass( 'darkened' );
        $('#tbody').find('.darkened').removeClass('darkened');
    }
    
    // mark a-node, shade other nodes
    var mark_a_node = function( node ) {
        var previous_node = $('#tbody')
                                .find('.marked')
                                .parent();
                                
        unmark_a_node( previous_node );
            
        node.children( '.data' )
            .addClass( 'marked' ); 

        node.find( '.data' )
            .removeClass( 'darkened' );       
            
        node.siblings()
            .find( '.data' )
            .addClass( 'darkened' );
    }
    
    // draw left and right borders
    var add_side_border = function( node ) {
        node.find( '.data' )
            .addClass( 'leftborder' )
            .addClass( 'rightborder' );
    }
    
    // draw bottom border
    var add_bottom_border = function( node ) {
        node.find('.data')
            .last()
            .addClass( 'bottomborder' );
    }

    return that;
    
})();
