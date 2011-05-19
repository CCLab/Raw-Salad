var _utils = (function () {
    var that = {};
    
    that.filter = function ( fn, list ) {
        var result = [];
        var element;
        var i;
            
        for( i = 0; i < list.length; i += 1 ) {
            element = list[ i ];
            if( fn( element ) ) {
                result.push( element );
            }
        } 
        
        return result;
    };

    that.money = function ( value ) {
        var result = [];
        var value = "" + value;

        var cut = function ( value ) {
            if( value.length <= 3 ) {
                result.push( value );
            }
            else {
                result.push( value.slice( value.length - 3 ));
                cut( value.slice( 0, value.length - 3 ));
            }
        }
        cut( value );
        return value === '0' ? '0' : result.reverse().join(' ') + " 000";
    };


    // this function cames from jQuery API example
    $.fn.equalize_heights = function() {
        return this.height( Math.max.apply (
            this, $(this).map( function ( i, e ) { 
                return $(e).height() 
        }).get()
    ))};
    

    return that;
    
})();
