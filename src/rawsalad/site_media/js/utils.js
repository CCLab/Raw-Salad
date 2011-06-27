var _utils = (function () {
    var that = {};

    // get hashed table(by its element's level) containing elements from collection
    that.hash_list = function ( collection ) {
        var i, len = collection.length;
        var result = {};
        var level;
        var element;

        for ( i = 0; i < len; i += 1 ) {
            element = collection[ i ];
            level = element['data']['level'];

            if ( !result[ level ] ) {
                result[ level ] = [];
            }
            result[ level ].push( element );
        }
        return result;
    };


    that.next_letter = function ( letter ) {
        var number = letter.charCodeAt( 0 );

        return String.fromCharCode( number + 1 );
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

    return that;

})();

// this function cames from jQuery API example
$.fn.equalize_heights = function() {
    return this.height( Math.max.apply (
        this, $(this).map( function ( i, e ) {
            return $(e).height()
    }).get()
))};
