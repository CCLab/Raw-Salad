var _download = (function () {

    var that = {};
    
    that.current_sheet = function () {
        var i, j;
        var data = '';
        var html = [];
        var form;
        var columns = _utils.filter( function ( e ) {
                return e['basic'] === true;
           }, _store.active_columns() );
        
        _assert.not_equal( columns.length, 0,
                           ">> DOWNLOAD <br/>Columns length === 0" );
     
        var rows = _store.active_rows();
        
        _assert.not_equal( rows.length, 0,
                           ">> DOWNLOAD <br/>Rows length === 0" );

        for( i = 0; i < columns.length; i += 1 ) {
            data += columns[i]['label'];
            data += ';';
        }
        data += '|';
     
        for( i = 0; i < rows.length; i += 1 ) {
            for( j = 0; j < columns.length; j += 1 ) {
                data += rows[i][ columns[j]['key'] ];
                data += ';';
            }
            data += '|';
        }
     
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
