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

var _algorithms = (function () {
    var that = {};

//  P U B L I C   I N T E R F A C E

    // sorts part of an array data with a hybrid sorting algorithm
    // which uses merge sort for dividing big part of an array and mergin them
    // and bubble sort for sorting small arrays. Uses setting sorting_setting.
    that.sort = function ( data, sorting_setting, start, end, border ) {
        var start = start || 0;
        var end = end || data.length - 1;
        var border = border || 2;
        var middle;

        // an array is small enough to use bubble sort
        if ( start > end - border )
            bubble_sort( data, sorting_setting, start, end);
        else {
            middle = get_middle( start, end );

            // sort two arrays separately
            that.sort( data, sorting_setting, start, middle, border );
            that.sort( data, sorting_setting, middle + 1, end, border );

            // merge sorted arrays
            merge( data, sorting_setting, start, middle, end);
        }
    };

    // filters collection
    that.filter = function ( data, filter_mask ) {
        var i;
        var result = [ ];
        var passed_filter_object = {};

        prepare_mask( filter_mask );

        // for each element in collection
        for ( i = 0; i < data.length; i += 1 ) {
            // checks if the object passes through the filter
            if ( check_obj( data[i], filter_mask ) ) {
                $.extend( true, passed_filter_object, data[ i ] );
                result.push( passed_filter_object );
                passed_filter_object = {};
            }
        }
        return result;
    };

    that.prepare_sorting_setting = function( sorting_setting, key ) {
        var hidden_attribute = {
            "pref": -1,
            "name": key
        };

        sorting_setting.push( hidden_attribute );
    };

//  P R I V A T E   I N T E R F A C E

//   S O R T I N G   H E L P E R   F U N C T I O N S

    // sorts data in range [start; end] with bubble_sort algorithm
    // with setting sorting_setting, which decides when an object is bigger than another
    var bubble_sort = function( data, sorting_setting, start, end ) {
        var start = start || 0;
        var end = end || data.length - 1;

        var i;
        var j;
        var sorted;

        for ( i = start, sorted = 0; i < end; i += 1, sorted += 1 ) {
            for ( j = start; j < end - sorted; j += 1 ) {
                if ( compare_obj( data[j]['data'], data[j+1]['data'], sorting_setting ) == -1 ) {
                    swap( data, j, j+1 );
                }
            }
        }
    };

    // sorts part of an array data with merge sort algorithm using setting sett
    var merge_sort = function( data, sorting_setting, start, end ) {
        var start = start || 0;
        var end = end || data.lenght - 1;
        var middle;

        if ( start > end - 1 ) {
            return;
        }

        middle = get_middle( start, end );

        // sort two arrays separately
        merge_sort( data, sorting_setting, start, middle );
        merge_sort( data, sorting_setting, middle + 1, end );

        // merge sorted arrays
        merge( data, sorting_setting, start, middle, end);
    };

    // merges two subarrays, 1st: data[start, middle], 2nd: data[middle+1, end]
    // result is that data[start, end] is sorted
    var merge = function( data, sorting_setting, start, middle, end ) {
        var i = 0;
        var j = 0;
        var ind = start;

        var subarray1 = data.slice(start, middle + 1);
        var subarray2 = data.slice(middle + 1, end + 1);

        // put the smallest actually element in the first available place in data
        while ( i < subarray1.length && j < subarray2.length ) {

            if ( compare_obj( subarray1[i], subarray2[j], sorting_setting ) == 1 ) {
                data[ind] = subarray1[i];
                i += 1;
            } else {
                data[ind] = subarray2[j];
                j += 1;
            }
            ind += 1;
        }

        if ( i < subarray1.length ) {
            // put last elements from subarray1 in the last spots in data
            while ( i < subarray1.length ) {
                data[ind] = subarray1[i];
                ind += 1;
                i += 1;
            }
        } else {
            // put last elements from subarray2 in the last spots in data
            while ( j < subarray2.length ) {
                data[ind] = subarray2[j];
                ind += 1;
                j += 1;
            }
        }
    };

    // changes elements in array
    var swap = function( data, i, j) {
        var tmp = data[i];
        data[i] = data[j];
        data[j] = tmp;
    };


    // gets middle point between start and end
     var get_middle = function( start, end ) {
        var length = start + end;
        var rest = length % 2;
        var temp = length - rest;

        return ( temp / 2 );
    }

    // compares values of specified attribute of two objects, returned value depends on preference
    var compare_atr = function( ob1, ob2, attr, pref ) {
        var compare_value;
        var alphabet;

        if ( typeof ob1[attr] === "number" ) {
            if ( ob1[attr] < ob2[attr] ) {
                compare_value = -1;
            } else if ( ob1[attr] > ob2[attr] ) {
                compare_value = 1;
            } else {
                return 0;
            }
        } else {
            alphabet = "0123456789a\u0105bc\u0107de\u0119fghijkl\u0142mn\u0144o\u00f3pqrs\u015btuvwxyz\u017a\u017c";
            return alpha( alphabet, pref, false )( ob1[ attr ], ob2[ attr ] );
        }

        // changes value to return basing on value of pref
        return compare_value * pref;
    }

    // alpha is slighlty modified function from
    // http://stackoverflow.com/questions/3630645/how-to-compare-utf-8-strings-in-javascript/3633725#3633725
    // written by Mic and Tomasz Wysocki
    var alpha = function( alphabet, dir, case_sensitive ) {
        dir = dir || 1;
        function compare_letters( a, b ) {
            var ia = alphabet.indexOf( a );
            var ib = alphabet.indexOf( b );
            if ( ia === -1 || ib === -1 ) {
                if ( ib !== -1 )
                    return a > 'a';
                if ( ia !== -1 )
                    return 'a' > b;
                return a > b;
            }
            return ia > ib;
        }

        return function( a, b ) {
            var pos = 0;
            var min = Math.min( a.length, b.length );
            case_sensitive = case_sensitive || false;
            if ( !case_sensitive ) {
                a = a.toLowerCase();
                b = b.toLowerCase();
            }
            while( a.charAt( pos ) === b.charAt( pos ) && pos < min ) {
                pos++;
            }

            return compare_letters( a.charAt(pos), b.charAt(pos)) ? dir : -dir;
        };
    };

    // compares two objects, compares their attributes mentioned in sorting_setting
    var compare_obj = function( ob1, ob2, sorting_setting ) {
        var i;
        var result = 0;
        var key;
        var pref;

        // for each attribute in sorting_setting
        for ( i = 0; i < sorting_setting.length; i += 1 ) {
            key = sorting_setting[i].name;
            pref = sorting_setting[i].pref;

            if ( i !== sorting_setting.length - 1 ) {
                result = compare_atr( ob1, ob2, key, pref );
            } else {
                result = id_comparison( ob1, ob2, sorting_setting );
            }

            if ( result !== 0 ) {
                break;
            }
        }

        return result;
    };

    var id_comparison = function( ob1, ob2, sorting_setting ) {
        var key;
        var pref;
        var sett_length = sorting_setting.length;
        var id1_tokenized;
        var id2_tokenized;
        var min_length;
        var i;
        var result;
        var token_to_int1;
        var token_to_int2;

        key = sorting_setting[ sett_length - 1 ].name;
        pref = sorting_setting[ sett_length - 1 ].pref;

        id1_tokenized = ob1[key].split("-");
        id2_tokenized = ob2[key].split("-");

        min_length = (id1_tokenized.length < id2_tokenized.length) ?
                            id1_tokenized.length : id2_tokenized.length;

        result = 1;
        for ( i = 0; i < min_length; i += 1 ) {
            token_to_int1 = parseInt( id1_tokenized[i] );
            token_to_int2 = parseInt( id2_tokenized[i] );

            if ( token_to_int1 < token_to_int2 ) {
                result = -1;
            } else if ( token_to_int1 > token_to_int2 ) {
                result = 1;
            }
        }

        return result * pref;
    }

//   F I L T E R I N G   H E L P E R   F U N C T I O N S

    // looks for every criterion that is string value and
    // changes it to lower case
    var prepare_mask = function( mask ) {
        var i;
        var value;
        var type;

        for ( i = 0; i < mask.length; i += 1 ) {
            type = typeof mask[ i ];
            if ( type === "string" ) {
                value = mask[ i ].value;
                mask[ i ].value = value.toLowerCase();
            }
        }
    };

    // checks if an object passes through a filter
    var check_obj = function( obj, filter_mask ) {
        var i;
        var key;
        var pref;
        var value;

        // for each attribute of an object which is also in filter_mask
        for ( i = 0; i < filter_mask.length; i += 1 ) {
            key = filter_mask[i].name;
            pref = filter_mask[i].pref;
            value = filter_mask[i].value;
            // one of attributes does not pass through a filter
            if ( !check_attr( obj, key, pref, value ) ) {
                return false;
            }
        }
        return true;
    };

    // checks if specfied attribute of an object passes a filter
    var check_attr = function( obj, attr, pref, value ) {
        var obj_val = obj[attr];
        var type = typeof obj_val;

        if ( type === "number" ) {
            if ( pref === 'lt' && obj_val < value) {
                return true;
            } else if ( pref === 'gt' && obj_val > value ) {
                return true;
            } else if ( pref === 'eq' && obj_val === value ) {
                return true;
            }
        } else {
            // is string
            var str = obj[attr].toLowerCase();

            if ( pref === -2 && !starts_with( str, value ) ||
                 pref === -1 && !contains( str, value ) ||
                 pref === 1 && contains( str, value ) ||
                 pref === 2 && starts_with( str, value ) ) {
                 return true;
            } else {
                return false;
            }
        }

        return false;
    };

    var starts_with = function( str, value ) {
        return ( str.indexOf( value ) === 0 );
    };

    var contains = function( str, value ) {
        return ( str.indexOf( value ) !== -1 );
    };

    return that;
})();
