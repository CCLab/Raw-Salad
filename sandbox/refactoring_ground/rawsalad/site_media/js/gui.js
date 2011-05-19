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
        $('#application').hide();    
        
        $('#open-close-choose-panel')
            .click( function () {
                // if choose panel is open
                if( $('#choose-panel:visible').length > 0 ) {
                    that.close_choose_panel();
                }
                else {
                    that.open_choose_panel();                
                }    
            })
            .hide();
        
        $('#choose-perspectives').hide();            
        $('#back-to-collections')
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
                $('#choose-collection-name')
                    .html('Dostępne kolekcje');
                $('#info-text')
                    .html('Wybierz jedną z dostępnych kolekcji danych.');

                $('#choose-collections')
                    .toggle();            
                $('#choose-perspectives')
                    .toggle();

                // clear the perspectives list
                $('#choose-perspectives-list')
                    .html('');
            });
    };

    // TODO Create choose panel!!!!
    // TODO 

    // used once when some perspective is chosen for the very first time
    that.init_app = function () {
        $('#open-close-choose-panel')    
            .show();
            
        $('#application')
            .fadeIn( 400 );
            
        that.close_choose_panel();
    }


    that.close_choose_panel = function () {   
        $('#choose-panel')
            .slideUp( 400 );
            
        $('#application')
            .animate({ opacity: 1 }, 300 );
            
        $('#open-close-choose-panel')
            .html('zmień dane');
    };
    
    
    that.open_choose_panel = function () {
        $('#choose-panel')
            .slideDown(400);
            
        $('#application')
            .animate({ opacity: 0.25 }, 300 );
            
        $('#open-close-choose-panel')
            .html('zwiń'); 
    }

   
    that.make_zebra = function () {
        // get all visible rows
        var visible_list = $('.data').not( ':hidden' );
        
        // TODO >> each is told to be slow - will we need it to be fast?!
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
                that.unmark_a_node( node );
            } 
            else { // not marked a-node clicked
                if ( already_marked.length > 0 ) { // there is another marked node
                    that.unmark_a_node( already_marked );
                }
                that.mark_a_node( node );
                that.add_side_border( node );
                that.add_bottom_border( node );
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
                    that.add_side_border( node );
                    that.add_bottom_border( node );
                } 
                else { 
                    that.add_side_border( node );
                }
            } else { 
                // there is another marked node
                if ( already_marked.length > 0 ) { 
                    that.unmark_a_node( already_marked );
                }
                
                that.mark_a_node( par );
                that.add_side_border( par );
                
                // it is the last node
                if ( par.children( 'div.nodes' ).find( '.node' ).last().attr( 'id' ) === node.attr( 'id' ) ) { 
                    par.find( 'div.data' ).children().removeClass( 'bottomborder' );
                    that.add_bottom_border( par );
                }
            }
        } 
        
        $('.top-border').removeClass('top-border');
        $('.marked').parent().next().children('.data').addClass('top-border');

        that.make_zebra();                        
    }
    
    
    // P R I V A T E   I N T E R F A C E
    
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
