(function () {

    //  C S S  R E L A T E D   F U N C T I O N    

    var arm_cells = function ( class_name ) {
        $( class_name ).find('.type').click( function () {
            var cell = $(this);
            var parent_id = cell.parent().attr('id');
    
            cell.toggleClass( 'closed' );
            cell.toggleClass( 'open' );
            if( $('.' + parent_id).length === 0 ) {
                add_new_data( parent_id );
            }
            else {
                // broken ---> it should be recursive
                $('.' + parent_id ).toggle();
            }
        });
    };


    //  D A T A   R E L A T E D   F U N C T I O N S     
    
    // this function uses globals, but it will be reimplemented
    // for ajax db connection!!
    var create_table = function () { 
        var schema = perspective['columns'];
        var data = filter( function ( element ) {
                return element['level'] === 'a';
            }, rows );
        var item;
        var col;
        var i, j;
        var html = [ '<table><thead><tr>' ];
        
        for( i = 0; i < schema.length; i += 1 ) {
            col = schema[i];
            html.push( '<th id="', col['key'], '">', col['label'], '</th>' );
        }
        
        html.push( '</tr></thead><tbody>' );

        for( i = 0; i < data.length; i += 1 ) {
            item = data[i];
            html.push( '<tr id="', item['id'], '" ' );
            html.push( 'class="', item['level'], '-node" ' );
            html.push( 'data-level="', item['level'], '">' );
            
            for( j = 0; j < schema.length; j += 1 ) {
                col = schema[j];
                html.push( '<td class="' );
                if( col['key'] === 'type' ) {
                    html.push( 'closed ' );
                }
                html.push( col['key'], '" ' );     
                html.push( 'data-processable="', !!col['processable'], '" ' );
                html.push( 'data-checkable="', !!col['checkable'], '">' );
                html.push( item[ col['key'] ] );
                if( !!col['checkable'] ) {
                    html.push( '<div class="checkbox"></div>' );
                }
                html.push( '</td>' );
            }
            html.push( '</tr>' );
        }
        
        html.push( '</tbody></table>' );
        
        $('#table-container').append( $( html.join('') ));
        arm_cells('.a-node');        
    }
    create_table();
    
    // this function uses globals, but it will be reimplemented
    // for ajax db connection!!
    var add_new_data = function ( parent_id ) {
        var parent = $('#'+parent_id);
        var parent_level = parent.attr('data-level');
        var schema = perspective['columns'];
        var data;
        var item;
        var col;
        var i, j;
        var html = [];

        
        data = filter( function ( element ) {
                return element['parent'] === parseInt( parent_id, 10 );
            }, rows );
        
        for( i = 0; i < data.length; i += 1 ) {
            item = data[i];
            html.push( '<tr id="', item['id'], '" ' );
            html.push( 'class="', item['level'], '-node ' );
            html.push( parent_id, '" ' );
            html.push( 'data-level="', item['level'], '">' );
            
            for( j = 0; j < schema.length; j += 1 ) {
                col = schema[j];
                html.push( '<td class="' );
                if( col['key'] === 'type' ) {
                    html.push( 'closed ' );
                }
                html.push( col['key'], '" ' );     
                html.push( 'data-processable="', !!col['processable'], '" ' );
                html.push( 'data-checkable="', !!col['checkable'], '">' );
                html.push( item[ col['key'] ] );
                if( !!col['checkable'] ) {
                    html.push( '<div class="checkbox"></div>' );
                }
                html.push( '</td>' );
            }
            html.push( '</tr>' );                
        }
        parent.after( $( html.join('') ));
        arm_cells( '.' + item['level'] + '-node');                                        
    };

  
})();



























