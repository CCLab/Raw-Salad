var Assert = (function () {
        var that = {};
        var browser = is_browser();

        that.assert = function ( exp, message ) {
            if( !Boolean( exp )) {
                print_error( message );
            }
        };

        that.isTrue = function ( obj, message ) {
            if( !obj ) {
                print_error( message );
            }
        };
        
        that.isFalse = function ( obj, message ) {
            if( !!obj ) {
                print_error( message );
            }
        };

        function is_browser() {
            try {
                if( document ) {
                    return true;
                }
            }
            catch( e ) {
                return false;
            }
        }

        function print_error( message ) {
            if( browser ) {
                var style = "position: fixed; \
                    top: 0px; \
                    left: 0px; \  
                    width: 200px; \
                    background: #a55; \
                    color: #fff; \
                    font-family: sans-serif; \
                    font-size: 11px; \
                    padding: 10px";
                var body = document.getElementsByTagName( 'body' )[0];
                var error = document.createElement( 'div' );
                error.setAttribute( 'style', style );
                error.innerHTML = message;

                body.appendChild( error );
            }
            else {
                print( message );
            }
        }
        
        return that;
    })();
