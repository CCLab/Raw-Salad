var _download = (function () {

    var that = {};
    
    that.current_sheet = function () {
        var i, j;
        var data = '';
        var html = [];
        var form;
        var columns, rows;
        
        var add_children = function ( parent ) {
            var i;
            var children = _utils.filter( function ( e ) {
                return e['parent'] === parent;
            }, _store.active_rows() );
            
            if( children.length === 0 ) {
                return;
            }
            
            for( i = 0; i < children.length; i += 1 ) {
                data += children[i]['idef'] + ';';
                if( !!children[i]['parent'] === false ) {
                    data += ';'
                }
                else {
                    data += children[i]['parent'] + ';';
                }
                data += children[i]['level'] + ';';

                for( j = 0; j < columns.length; j += 1 ) {
                    data += children[i][ columns[j]['key'] ];
                    data += ';';
                }
                data += '|';
                
                if( children[i]['hidden'] === true ) {
                    continue;
                }
                else {
                    add_children( children[i]['idef'] );
                }
            }
        };


        columns = _utils.filter( function ( e ) {
                return e['basic'] === true;
           }, _store.active_columns() );
        
        _assert.not_equal( columns.length, 0,
                           ">> DOWNLOAD <br/>Columns length === 0" );

        data += 'ID;Rodzic;Poziom;';
             
        for( i = 0; i < columns.length; i += 1 ) {
            data += columns[i]['label'];
            data += ';';
        }
        data += '|';
     
        add_children( null );
        
        _assert.not_equal( data, '', 
                           ">> DOWNLOAD <br/>Data string empty" );
        
        $('#download-form')
            .find('input')
            .val( data.slice( 0, data.length-1 ) )
            .end()
            .submit();
    };
    
    return that;
})();
