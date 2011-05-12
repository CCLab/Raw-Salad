var Utilities = (function () {
    var that = {};
    
    /*****************************************************************************
     *                                                                           *
     *                             SORTING                                       *
     *                                                                           *
     *****************************************************************************/
    /*
      General sorting interface is:
         
         - for whole collection:
             type_of_sort( data, settings )

         - for range of the collection:
             type_of_sort( data, settings, start, end )

         - settings object is a list of prefferences each containing two fields:
             name - a key to be used as a base for sorting
             pref - sorting order (1 - ascending, -1 - descending)

             [{
                 pref: 1,
                 name: "age"
              },
              {
                 pref: -1,
                 name: "name"
              }]
    */
    
    // S O R T

    // sorts part of an array data with a hybrid sorting algorithm
    // which uses merge sort for dividing big part of an array and mergin them
    // and bubble sort for sorting small arrays. Uses setting sett.
    // data - collection to sort
    // sett - decides how objects are compared
    // optional arguments:
    // start - first index; default -> start = 0
    // end - last index; default -> end = data.length - 1
    // border - value indicating when bubble_sort should be used
    that.sort = function ( data, sett, start, end, border ) {
        var start = start || 0;
        var end = end || data.length - 1;
        var border = border || 2;
        
        if ( start > end - border ) // an array is small enough to use bubble sort
            bubble_sort( data, sett, start, end);
        else {
            var middle = get_middle( start, end );
            
            // sort two arrays separately
            that.sort( data, sett, start, middle, border );
            that.sort( data, sett, middle + 1, end, border );
            
            // merge sorted arrays
            merge( data, sett, start, middle, end);
        }
    };
     

    // B U B B L E   S O R T

    // sorts data in range [start; end] with bubble_sort algorithm
    // with setting sett, which decides when an object is bigger than another
    // data - collection to sort
    // sett - setting deciding how to compare two objects
    // optional arguments:
    // start - index of the first element of data to sort; default -> start = 0
    // end - index of the last element of data to sort; default -> end = data.length - 1
    function bubble_sort( data, sett, start, end ) {
        var start = start || 0;
        var end = end || data.length - 1;
        
        var i;
        var j;
        var k;
        
        for ( i = start, k = 0; i < end; i += 1, k+= 1 ) {
            for ( j = start; j < end - k; j += 1 ) {
                if ( compare_obj( data[j], data[j+1], sett ) == -1 ) {
                    swap( data, j, j+1 );
                }
            }
        }
    };

    // M E R G E   S O R T 

    // sorts part of an array data with merge sort algorithm using setting sett
    // data - collection to sort
    // sett - decides how objects are compared
    // optional arguments:
    // start - first index; default -> start = 0
    // end - last index; default -> end = data.length - 1
    function merge_sort( data, sett, start, end ) {
        var start = start || 0;
        var end = end || data.lenght - 1;
        
        if ( start > end - 1 )
            return;
        var middle = get_middle( start, end );
        
        // sort two arrays separately
        merge_sort( data, sett, start, middle );
        merge_sort( data, sett, middle + 1, end );
        
        // merge sorted arrays
        merge( data, sett, start, middle, end);
    };

    // merges two subarrays, 1st: data[start, middle], 2nd: data[middle+1, end]
    // result is that data[start, end] is sorted
    // data - collection to sort
    // sett - decides how objects are compared
    function merge( data, sett, start, middle, end ) {    
        var i = 0;
        var j = 0;
        var ind = start;
        
        var array1 = data.slice(start, middle + 1);
        var array2 = data.slice(middle + 1, end + 1);
        
        // put the smallest actually element in the first available place in data
        while ( i < array1.length && j < array2.length ) {

            if ( compare_obj( array1[i], array2[j], sett ) == 1 ) {
                data[ind] = array1[i];
                i += 1;
            } else {
                data[ind] = array2[j];
                j += 1;
            }
            ind += 1;
        }
        
        if ( i < array1.length ) {
            // put last elements from array1 in the last spots in data
            while ( i < array1.length ) {
                data[ind] = array1[i];
                ind += 1;
                i += 1;
            }
        } else {
            // put last elements from array2 in the last spots in data
            while ( j < array2.length ) {
                data[ind] = array2[j];
                ind += 1;
                j += 1;
            }
        }
    };


    /*****************************************************************************
     *                                                                           *
     *                             FILTERING                                     *
     *                                                                           *
     *****************************************************************************/

    // name: name of attribute which will be checked during filtering,
    // two types of masks:
    // a) numeric:
    //   pref: -2 -> < value
    //   pref: -1 -> <= value
    //   pref: 0 -> == value
    //   pref: 1 -> >= value
    //   pref: 2 -> > value
    // b) string:
    //   pref: -2 -> does not start value
    //   pref: -1 -> does not contain value
    //   pref: 1 -> contains value
    //   pref:2 -> starts from value
    /*var mask = [
                { name: 'y2010', pref: '1', value: '100000' },
                { name: 'y2011', pref: '-1', value: '300000' }
    ];*/
    
    // filters collection
    // data - collection to filter
    // filter_mask - filter(array of filters)
    // returns array of elements that passed through the filter
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
    
    // looks for every criterion that is string value and
    // changes is to lower case
    // mask - filtering mask to be changed
    function prepare_mask( mask ) {
        var i;
        var attr;
        var value;
        var type;
        
        for ( i = 0; i < mask.length; i += 1 ) {
            type = mask[ i ].type;
            if ( type === "string" ) {
                value = mask[ i ].value;
                mask[ i ].value = value.toLowerCase();
            }
        }
    };
    
    // checks if an object passes through a filter
    // obj - object to check
    // filter_mask - filter(array of filters)
    // returns true if yes, false if not
    function check_obj( obj, filter_mask ) {
        var i;
        var key;
        var pref;
        var value;
        
        // for each attribute of an object which is also in filter_mask
        for ( i = 0; i < filter_mask.length; i += 1 ) {
            key = filter_mask[i].name;
            pref = filter_mask[i].pref;
            value = filter_mask[i].value;
            debugger;
            // one of attributes does not pass through a filter
            if ( !check_attr( obj, key, pref, value ) ) {
                return false;
            }
        }
        return true;
    };

    // checks if specfied attribute of an object passes a filter
    // obj - object to check
    // attr - name of the attribute to check
    // pref - decides if value of the attribute should be higher or lower
    // value - border value
    // returns true if yes, false if not
    function check_attr( obj, attr, pref, value ) {
        var obj_val = obj[attr];
        var type = obj[ "type" ];
        
        if ( type === "number" ) {
            if ( pref === -1 && obj_val < value) {
                return true;
            } else if ( pref === 1 && obj_val > value ) {
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
    
    function is_number( obj, attr ) {
        var i;
        var cols = data[columns];
        var numeric = false;
        for ( i = 0; i < cols.length; i += 1 ) {
            if ( cols[i].key === attr && cols[i].type === "number") {
                numeric = true;
                break;
            }
        }
        return numeric;
    };
    
    function starts_with( str, value ) {
        return ( str.indexOf( value ) === 0 );
    };
    
    function contains( str, value ) {
        return ( str.indexOf( value ) !== -1 );
    };
    
    
    // S O R T I N G   H E L P E R   F U N C T I O N S
    
    // adds hidden parameter to sorting setting to avoid a situation,
    // when two rows are equal
    // sett - setting to be modified
    that.prepare_sorting_setting = function( sett ) {
        var hidden_attribute = {
            "pref": -1,
            "name": "idef"
        };
        
        sett.push( hidden_attribute );
    };


    // prints an element using given schema
    // el - element to print
    // sch - schema containing attributes of the element to print
    function printEl( el, sch ) {
        document.writeln( '{ ' );
        var i;
        var key;
        
        // for each attribute in a schema
        for ( i = 0; i < sch.length; i += 1 ) {
            key = sch[i].key;
            document.writeln( key + ': ' + el[key] + ' ');
        }
        document.writeln( '} <br>' );
    };

    // prints elements of a collection using given schema of those elements
    // coll - collection of objects to print
    // sch - schema containing attributes of elements to print
    function printColl( coll, sch ) {
        var i;
        
        // for each element in a collection
        for ( i = 0; i < coll.length; i += 1 ) {
            printEl( coll[i], sch );
        }
    };

    // prints short version of elements belonging to a collection after sorting
    // using setting, which tells which parameters should be printed
    // coll - collection of objects to print
    // sett - setting that specifies which attributes will be printed
    function printShort( coll, sett ) {
        var i, j;
        var key1, key2;
        var value;
        var ch;
        var pref;
        
        // for each element in a collection
        for ( i = 0; i < coll.length; i += 1 ) {
            print( '{ ' );
            // for each attribute that should be printed
            for ( j = 0; j < sett.length; j += 1 ) {
                key = sett[j].name;
                pref = sett[j].pref;
                value = coll[i][key];
                
                // special letters: R - attr. should rise, M - should lower
                // O - doesn't matter
                if ( pref == 1 ) {
                    print( '(R)' );
                } else if ( pref == 0 ) {
                    print( '(O)' );
                } else if ( pref == -1 ) {
                    print( '(M)' );
                }
                
                print( key );
                print( '=' );
                print( value );
                print( ',' );
            }
            println( '}' );
        }
    };

    // prints argument, shorter version, used for convenience
    // arg - object to print
    function print( arg ) {
        document.writeln( arg );
    };

    // the same as print plus prints end line after the argument
    // arg - object to print
    function println( arg ) {
        document.writeln( arg + '<br>' );
    };

    // changes elements in array
    // data - collection with elements
    // i - index of the first element
    // j - index of the second element
    function swap( data, i, j) {
        var tmp = data[i];
        data[i] = data[j];
        data[j] = tmp;
    };


    // gets middle point between start and end
    function get_middle( start, end ) {
        var length = start + end;
        var rest = length % 2;
        var temp = length - rest;

        return ( temp / 2 );
    }

    // compares values of specified attribute of two objects, returned value depends on preference
    // ob1, ob2 - objects to compare
    // attr - attribute that will be checked
    // pref - preference
    // if pref. = 1, then returns 1, if attribute of the first object is higher than the second one,
    // 0 if values are equal, otherwise -1
    // if pref. = -1, then reurns opposite values than if pref = 1
    // if pref. = 0, then returns 0
    function compare_atr( ob1, ob2, attr, pref ) {
        var compare_value;

        if ( ob1[attr] < ob2[attr] ) {
            compare_value = -1;
        } else if ( ob1[attr] > ob2[attr] ) {
            compare_value = 1;
        } else {
            return 0;
        }
        
        // changes value to return basing on value of pref
        return compare_value * pref;
    }

    // compares two objects, compares their attributes mentioned in sett
    // ob1, ob2 - objects to compare
    // sett - setting deciding how objects will be compared
    // returns -1 -> ob1 < ob2
    //          0 -> ob1 == ob2
    //          1 -> ob1 > ob2
    function compare_obj( ob1, ob2, sett ) {
        var i;
        var result = 0;
        var key;
        var pref;
        
        // for each attribute in sett
        for ( i = 0; i < sett.length; i += 1 ) {
            key = sett[i].name;
            pref = sett[i].pref;

            result = compare_atr( ob1, ob2, key, pref );
            if ( result !== 0 ) {
                break;
            }
        }

        return result;
    };
    
    

    return that;
})();