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


    that.money = function ( data, format ) {
        var result = [];
        var data = data + '';
        var value = '';
        var sufix = '.';
        if( format.indexOf('.') !== -1 ) {
             value = data.split('.')[0];
             sufix += data.split('.')[1] || '00';
             // just one digit provided
             if( sufix.length === 2 ) {
                 sufix += '0';
             }
             else if( sufix.length > 3 ) {
                 sufix = sufix.substr(0,3);
             }
        }
        else {
            value = data;
            sufix = '';
        }

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
        return value === '0' ? '0' : result.reverse().join(' ') + sufix;
    };

    that.uniq = function ( array, sort_it ) {
        var result = [];

        array.forEach( function ( e ) {
            if( result.indexOf( e ) === -1 ) {
                y.push( e )
            }
        });

        return sort_it ? result.sort() : result;
    };

    that.create_preloader = function( text ) {
        var preloader;
        var html = [];
        var x;
        var main_cover = $( '<div class="cover" id="main-cover" > </div>' );
        $('#wrapper')
            .append(main_cover);
        $('#main-cover')
             .height( $('#wrapper').height() )
             .width( $('#wrapper').width() );



        html.push('<div id="preloader">');
        html.push( text );
        html.push('</div>');

        preloader = $( html.join('') );

        $('body').append( preloader );
        preloader.css({ 'top': '-1px' });
        x = ($(window).width() - $('#preloader').width()) / 2;
        preloader.css({ 'left': x });
        $('#wrapper').css( 'opacity', '0.3' );
    };

    that.clear_preloader = function() {
        $('#main-cover').remove();
        $('#wrapper').css( 'opacity', '1' );
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

    that.beforeunload = function ( e ) {
        e = e || window.event;

        // For IE and Firefox prior to version 4
        if (e) {
            e.returnValue = translation['js_unload_warning'];
        }

        // For Safari
        return translation['js_unload_warning'];
    };

    return that;

})();
