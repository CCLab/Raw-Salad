var _download = (function () {

    var that = {};
    
    that.current_sheet = function () {
        var i;
        var data;
        var sheet = _store.active_sheet();
        var html = [];
        var form;
        var columns = _utils.filter( function ( e ) {
                return e['basic'] === true;
           }, _store.active_columns() );
           
        
        
        
        html.push( '<form action="/download/" method="post" name="input">' );
        html.push( '<input type="text" name="sheet" />' );
        html.push( '</form>' );
        
        form = $( html.join( '' ));

        form.find('input')
            .val( data )
            .end()
            .submit();
    };
    
    return that;
})();
