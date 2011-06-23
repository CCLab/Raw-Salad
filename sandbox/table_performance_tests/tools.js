// Copyright (c) 2011, Centrum Cyfrowe
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
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
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
// OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
// ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

//
// This is a helper functions collection usefull in data visualization

var Tools = (function () {
    var that = {};

    // get the array of elements under some condition
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
    
    // get hashed table(by its element's level) containing elements from collection
    that.hash_list = function ( collection ) {
        var i, len = collection.length;
        var result = [];
        var level;
        var element;
       
        for ( i = 0; i < len; i += 1 ) {
            element = collection[ i ];
            level = element['data']['level'];
            
            if ( !result[level] ) {
                result[ level ] = [];
            }
            result[level].push( element );
        }
        return result;
    };

    // get log10 of the value x
    that.log10 = function ( x ) {
        return Math.log( x ) / Math.log( 10 );
    };


    // remap a value to a new scale
    that.remap = function ( x, imin, imax, omin, omax ) {
        var imin = imin || 0;
        var imax = imax || 1;
        var omin = omin || 0;
        var omax = omax || 1;
        
        return omin + ( omax - omin ) * (( x - imin ) / ( imax - imin ));
    };

    // get the normalized array of key values from an object
    that.normalize_data = function ( data, key ) {
        var total = that.get_total( data, key );
        var i, length = data.length;
        var result = [];

        for( i = 0; i < length; ++i ) {
            result.push( data[i][key] / total );
        }
        return result;
    };


    // get sum of array elements
    that.get_sum = function ( data ) {
        if( data.length === 1 ) {
            return data[0];
        }
        return data[0] + that.get_sum( data.slice( 1 ));
    };


    // get sum of given key in the array of objects
    that.get_total = function ( data, key ) {
        if( data.length === 1 ) {
            return data[0][key];
        }
        return data[0][key] + that.get_total( data.slice( 1 ), key );
    };


    // change the string into Title case
    that.toTitleCase = function ( str ) {
        return  str[0].toUpperCase() + str.slice(1).toLowerCase();
    };


    // take a number and represent it as money string: 1 000 000
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
