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

var _assert = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    that.assert = function ( exp, message ) {
        if( !Boolean( exp )) {
            show_error( "assert", message );
        }
    };

    that.is_true = function ( obj, message ) {
        if( !obj ) {
            show_error( "true", message );
        }
    };

    that.is_false = function ( obj, message ) {
        if( !!obj ) {
            show_error( "false", message );
        }
    };

    that.is_equal = function ( obj1, obj2, message ) {
        if( obj1 !== obj2 ) {
            show_error( "equal", message );
        }
    };

    that.not_equal = function ( obj1, obj2, message ) {
        if( obj1 === obj2 ) {
            show_error( "not equal", message );
        }
    };


//  P R I V A T E   I N T E R F A C E
    var is_browser = (function () {
        try {
            if( document ) {
                return true;
            }
        }
        catch( e ) {
            return false;
        }
    })();


    return that;

    function show_error( type, message ) {
        var html = [];
        var error;
        var msg;
        var style;

        if( !message ) {
            throw new AssertException( type );
        }
        else {
            if( is_browser ) {

                style = {
                    'position': 'fixed',
                     'top': '0px',
                     'left': '0px',
                     'width': '200px',
                     'background-color': '#a55',
                     'color': '#fff',
                     'font-family': 'sans-serif',
                     'font-size': '11px',
                     'padding': '10px'
                };

                html.push( '<div id="error-popup">' );
                html.push( '>> <b>AssertException</b><br />' );
                html.push( '>> Type: <br />' );
                html.push( '<b>', type, '</b><br />' );
                html.push( '>> Message: <br />' );
                html.push( '<b>', message, '</b><br />' );

                error = $( html.join('') );
                error.css( style )
                     .click( function () {
                         $(this).remove();
                     });

                $('body').append( error );

                throw new AssertException( type );
            }
            else {
                msg =  ">> AssertException ";
                msg += ">> Type: " + type + " ";
                msg += ">> Message: " + message;

                console.log( msg );

                throw new AssertException( type );
            }
        }
    };


    AssertException = function( type ) {
        this.message = ">> AssertException >> Type: " + type;
    };

    AssertException.prototype.toString = function () {
        return this.message;
    };

})();
