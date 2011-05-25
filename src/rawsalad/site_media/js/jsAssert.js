// Copyright (c) 2011, Centrum Cyfrowe
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification, 
// are permitted provided that the following conditions are met:
//
//   * Redistributions of source code must retain the above copyright notice, 
//     this list of conditions and the following disclaimer.
//   * Redistributions in binary form must reproduce the above copyright notice, 
//     this list of conditions and the following disclaimer in the documentation 
//     and/or other materials provided with the distribution.
//   * Neither the name of the Centrum Cyfrowe nor the names of its contributors 
//     may be used to endorse or promote products derived from this software 
//     without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
// GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
// OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

var Assert = (function () {
    var that = {};

    that.assert = function ( exp, message ) {
        if( !Boolean( exp )) {
            that.print_error( "assert", message );
        }
    };

    that.is_true = function ( obj, message ) {
        if( !obj ) {
            that.print_error( "true", message );
        }
    };
    
    that.is_false = function ( obj, message ) {
        if( !!obj ) {
            that.print_error( "false", message );
        }
    };

    that.is_equal = function ( obj1, obj2, message ) {
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
        var body,
            error, 
            msg,
            style;

        if( !message ) {
            throw new that.AssertException( type );
        }
        else {
            if( that.browser ) {
                style = "position: fixed; \
                             top: 0px; \
                             left: 0px; \
                             width: 200px; \
                             background: #a55; \
                             color: #fff; \
                             font-family: sans-serif; \
                             font-size: 11px; \
                          padding: 10px";
                body = document.getElementsByTagName( 'body' )[0];
                error = document.createElement( 'div' );
                msg =  ">> <b>AssertException</b><br />";
                msg += ">> Type: " + type + "<br />";
                msg += ">> Message: " + message;
                    
                error.setAttribute( 'style', style );
                error.innerHTML = msg;

                body.appendChild( error );
                
                throw new that.AssertException( type );
            }
            else {
                msg =  ">> AssertException ";
                msg += ">> Type: " + type + " ";
                msg += ">> Message: " + message;
                           
                print( msg );
                
                throw new that.AssertException( type );                
            }
        }
    };
    
    that.AssertException = function( type ) {
        this.message = ">> AssertException >> Type: " + type;        
    };
    
    that.AssertException.prototype.toString = function () {
        return this.message;
    };
        
    return that;
})();
