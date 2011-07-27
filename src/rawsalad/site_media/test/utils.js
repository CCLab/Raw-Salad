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

    that.next_id = (function () {
        var id = 1000;
        var fun = function () {
            return id++;
        };

        return fun;
    })();

    // go through the subtree of id-node and do fun
    that.with_subtree = function ( id, fun ) {
        $('tr.'+id).each( function () {
            that.with_subtree( $(this).attr('id'), fun );
            fun.call( $(this) );
        });
    }


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

    that.create_preloader = function( text ) {
        var preloader;
        var html = [];
        var x = screen.width / 2 - 200;

        html.push('<div id="preloader">');
        html.push( text );
        html.push('</div>');

        preloader = $( html.join('') );
        preloader.css({
            'top': '10px',
            'left': x
        });

        $('body').append( preloader );
        $('#wrapper').css( 'opacity': '0.3' );
    };

    that.clear_preloader = function() {
        $('#wrapper').css( 'opacity': '1' );
        $('#preloader').remove();
    };

    that.get_parent_id = function( id ) {
        var parent_id;
        var last_index = id.lastIndexOf( '-' );

        if ( last_index === -1 ) {
            parent_id = null;
        }
        else {
            parent_id = id.slice( 0, last_index );
        }

        return parent_id;
    }

    return that;

})();
