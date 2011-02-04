var Assert = (function () {
    var that = {};

    that.assert = function ( exp, message ) {
        if( !Boolean( exp )) {
            that.print_error( "assert", message );
        }
    };

    that.true = function ( obj, message ) {
        if( !obj ) {
            that.print_error( "true", message );
        }
    };
    
    that.false = function ( obj, message ) {
        if( !!obj ) {
            that.print_error( "false", message );
        }
    };

    that.equal = function ( obj1, obj2, message ) {
        if( obj1 !== obj2 ) {
            that.print_error( "equal", message );
        }
    };

    that.not_equal = function ( obj1, obj2, message ) {
        if( obj1 === obj2 ) {
            that.print_error( "not equal", message );
        }
    };

    that.browser = (function () {
        try {
            if( document ) {
                return true;
            }
        }
        catch( e ) {
            return false;
        }
    })();

    that.print_error = function ( type, message ) {
        if( !message ) {
            throw new that.AssertException( type );
        }
        else {
            if( that.browser ) {
                var style = "position: fixed; \
                             top: 0px; \
                             left: 0px; \
                             width: 200px; \
                             background: #a55; \
                             color: #fff; \
                             font-family: sans-serif; \
                             font-size: 11px; \
                             padding: 10px",
                    body = document.getElementsByTagName( 'body' )[0],
                    error = document.createElement( 'div' ),
                    msg;
                
                msg =  ">> <b>AssertException</b><br />";
                msg += ">> Type: " + type + "<br />";
                msg += ">> Message: " + message;
                    
                error.setAttribute( 'style', style );
                error.innerHTML = msg;

                body.appendChild( error );
            }
            else {
                var msg =  ">> AssertException ";
                    msg += ">> Type: " + type + " ";
                    msg += ">> Message: " + message;
                           
                print( msg );
            }
        }
    }
    
    that.AssertException = function( type ) {
        this.message = ">> AssertException >> Type: " + type;        
    };
    
    that.AssertException.prototype.toString = function () {
        return this.message;
    };
        
    return that;
})();
