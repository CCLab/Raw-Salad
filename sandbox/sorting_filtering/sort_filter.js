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

// B U B B L E   S O R T
// TODO: Merge the bubble_srt functions into one using:
//
//     function bubble_sort( data, settings, start, end ) {
//        var start = start || 0;
//        var end = end || data.lenght;
//      

// sorts data with bubble_sort algorithm with given settings,
// which decides when an object is bigger than another
// data - collection to sort
// settings - setting deciding how to compare two objects
function bubble_sort( data, settings ) {
    var i;
    var j;
    var length = data.length;
    
    for ( i = 0; i < length - 1; i += 1 ) {
        for ( j = 0; j < length - i - 1; j += 1 ) {
            // obiekt o mniejszym numerze jest lepszy, wiersze lepsze na górze
            /*print( 'test: ' );
            print( j );
            print( ' vs ' );
            println( j+1 );*/
            if ( compare_obj( data[j], data[j+1], settings ) === -1 ) {
                swap( data, j, j+1 );
                /*print( j );
                print( ' <-> ' );
                println( j+1 );*/
            }
        }
    }
};

// sorts data in range [start; end] with bubble_sort algorithm
// with settings, which decides when an object is bigger than another
// data - collection to sort
// settings - setting deciding how to compare two objects
// start - index of the first element of data to sort
// end - index of the last element of data to sort
function bubble_sort_r( data, settings, start, end ) {
    var i;
    var j;
    var k;
    
    for ( i = start, k = 0; i < end; i += 1, k+= 1 ) {
        for ( j = start; j < end - k; j += 1 ) {
            // obiekt o mniejszym numerze jest lepszy, wiersze lepsze na górze
            /*print( 'test: ' );
            print( j );
            print( ' vs ' );
            println( j+1 );*/
            if ( compare_obj( data[j], data[j+1], settings ) == -1 ) {
                swap( data, j, j+1 );
                /*print( j );
                print( ' <-> ' );
                println( j+1 );*/
            }
        }
    }
};

// M E R G E   S O R T 

// TODO: merge two merge_sort functions into one
//       just like bubble sort - JS doesn't need delegation in this case
//  
// sorts part of an array data with merge sort algorithm using setting settings
// data - collection to sort
// settings - decides how objects are compared
// first index = start, last index = end
function merge_sort_r( data, settings, start, end ) {
    if ( start > end - 1 )
        return;

    // TODO: 
    // var middle = get_middle( start, end );
    var middle = int_div( (start + end), 2);
    
    // sort two arrays separately
    merge_sort_r( data, settings, start, middle );
    merge_sort_r( data, settings, middle + 1, end );
    
    // merge sorted arrays
    merge( data, settings, start, middle, end);
};

// sorts the whole array with merge sort algorithm using setting sett
// data - collection to sort
// settings - decides how objects are compared
function merge_sort( data, settings ) {
    merge_sort_r( data, settings, 0, data.length - 1 );
};

// merges two subarrays, 1st: data[start, middle], 2nd: data[middle+1, end]
// result is that data[start, end] is sorted
// data - collection to sort
// settings - decides how objects are compared
function merge( data, settings, start, middle, end) {
    var i = 0;
    var j = 0;
    var index = start;
    
    var array1 = data.slice(start, middle + 1);
    var array2 = data.slice(middle + 1, end + 1);
    
    // put the smallest actually element in the first available place in data
    //print('MERGE: ['); print(start); print('--'); print(end); println(']');
    while ( i < array1.length && j < array2.length ) {
        //print( 'i: '); print( i ); print( 'j: '); print( j ); print('| ');
        if ( compare_obj( array1[i], array2[j], settings ) == 1 ) {
            data[index] = array1[i];
            i += 1;
        } else {
            data[index] = array2[j];
            j += 1;
        }
        index += 1;
    }
    
    if ( i < array1.length ) {
        // put last elements from array1 in the last spots in data
        while ( i < array1.length ) {
            data[index] = array1[i];
            index += 1;
            i += 1;
        }
    } else {
        // put last elements from array2 in the last spots in data
        while ( j < array2.length ) {
            data[index] = array2[j];
            index += 1;
            j += 1;
        }
    }
    //println('');
};



// H Y B R I D   S O R T

// TODO: call it sort as we a general purpose interface
//       make border automatic depending on the data and settings length
 
// sorts part of an array data with a hybrid sorting algorithm
// which uses merge sort for dividing big part of an array and mergin them
// and bubble sort for sorting small arrays. Uses settings.
// data - collection to sort
// settings - decides how objects are compared
// first index = start, last index = end
// border - value indicating when bubble_sort should be used
function hybrid_sort_r( data, settings, start, end, border ) {
    if ( start > end - border ) // an array is small enough to use bubble sort
        bubble_sort_r( data, settings, start, end);
    else {
        // TODO: 
        // var middle = get_middle( start, end );
        var middle = int_div( (start + end), 2);
        
        // sort two arrays separately
        hybrid_sort_r( data, settings, start, middle, border );
        hybrid_sort_r( data, settings, middle + 1, end, border );
        
        // merge sorted arrays
        merge( data, settings, start, middle, end);
    }
};

// TODO: merge two hybrid_sorts into one function
//
// sorts the whole array with hybrid sort(merge sort + bubble sort)
// algorithm using setting sett
// data - collection to sort
// sett - decides how objects are compared
// border - value indicating when bubble sort should be used
function hybrid_sort( data, sett, border ) {
    hybrid_sort_r( data, sett, 0, data.length - 1, border);
};



// S O R T I N G   H E L P E R   F U N C T I O N S

// TODO: Use jQuery extend method instead:
//       http://api.jquery.com/jQuery.extend/
// 
// function used to deep copying objects
// obj - object to copy
// returns copy of that object
function clone_obj( obj ) {
    if ( typeof obj !== 'object' || obj === null ) {
        return obj;
    }
 
    var c = obj instanceof Array ? [] : {};
 
    for (var i in obj) {
        var prop = obj[i];
 
        if (typeof prop == 'object') {
           if (prop instanceof Array) {
               c[i] = [];
 
               for (var j = 0; j < prop.length; j++) {
                   if (typeof prop[j] != 'object') {
                       c[i].push(prop[j]);
                   } else {
                       c[i].push(clone_obj(prop[j]));
                   }
               }
           } else {
               c[i] = clone_obj(prop);
           }
        } else {
           c[i] = prop;
        }
    }
 
    return c;
}

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


// TODO: why not to make:
//
//       function get_middle( start, end ) ??
//
// instead of int_div - get_middle means sth at least...
function get_middle( start, end ) {
    var length = start + end;
    var rest = length % 2;
    var temp = length - rest;

    return ( temp / 2 );
}
// TODO - use the one above instead of int_div
// division for integers
// returns ( big div small)
function int_div( big, small ) {
    var rest = big % small;
    var tmp = big - rest;
    return ( tmp / small );
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



/*****************************************************************************
 *                                                                           *
 *                             FILTERING                                     *
 *                                                                           *
 *****************************************************************************/

// TODO: let's talk about it before you code :D
//
// name: name of attribute which will be checked during filtering,
// pref: preference 1 means -> bigger values are good, -1 -> lower values are good
// value - border value of the attribute
/*var mask = [
            { name: 'y2010', pref: '1', value: '100000' },
            { name: 'y2011', pref: '-1', value: '300000' }
];*/

// checks if specfied attribute of an object passes a filter
// obj - object to check
// attr - name of the attribute to check
// pref - decides if value of the attribute should be higher or lower
// value - border value
// returns true if yes, false if not
function check_attr( obj, attr, pref, value ) {
    var obj_val = obj[attr];
    
    if ( pref == -1 && obj_val < value) {
        return true;
    } else if ( pref == 1 && obj_val > value ) {
        return true;
    }
    return false;
}

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
        // one of attributes does not pass through a filter
        if ( !check_atr( obj, key, pref, value ) ) {
            return false;
        }
    }
    return true;
};

// filters collection
// data - collection to filter
// filter_mask - filter(array of filters)
// returns array of elements that passed through the filter
function filter_coll( data, filter_mask ) {
    var i;
    var result = [ ];
    
    // for each element in collection
    for ( i = 0; i < data.length; i += 1 ) {
        // checks if the object passes through the filter
        if ( check_obj( data[i], filter_mask ) ) {
            result[result.length] = clone_obj( data[i] );
        }
    }
    return result;
};


/*****************************************************************************
 *                                                                           *
 *                             TESTING_FUNCTIONS                             *
 *                                                                           *
 *****************************************************************************/

 // checks if objects are equal
function check_eq_ob( ob1, ob2, sch ) {
    var i;
    var name;
    var result = true;
    for ( i = 0; i < sch.length; i += 1 ) {
        name = sch[i];
        if ( ob1.name !== ob2.name ) {
            result = false;
            break;
        }
    }
    return result;
};

// checks if collections are equal
function check_eq_collections( coll1, coll2, sch ) {
    var i;
    var result = true;
    
    if ( coll1.length != coll2.length ) {
        print( 'Rozmiary kolekcji rozne: ' ); print( coll1.length );
        print( ' vs ' ); println( coll2.length );
        result = false;
        return result;
    }
    
    for ( i = 0; i < coll1.length; i += 1 ) {
        result = check_eq_ob( coll1[i], coll2[i], sch );
        if ( !result ) {
            print('Obiekty rozne. Indeks: '); println( i );
            break;
        }
    }
    
    return result;
};

// tests if sorting functions gave the same results
function compare_sorts( data, sett, sch, debug ) {
    var result, result2;
    var bubble_copy = clone_obj( data );
    var merge_copy = clone_obj( data );
    var hybrid_copy = clone_obj( data );
    
    bubble_sort( bubble_copy, sett );
    merge_sort( merge_copy, sett );
    hybrid_sort( hybrid_copy, sett, 2 );
    
    result = check_eq_collections( bubble_copy, merge_copy, sch );
    result2 = check_eq_collections( bubble_copy, hybrid_copy, sch );
    
    if ( debug ) {
        println( 'WYNIKI SORTOWANIA BUBBLESORTEM: ' );
        printColl( bubble_copy, sch );
        println( '<hr>' );
        printShort( bubble_copy, sett );
        println( '<hr>' );
        println( 'WYNIKI SORTOWANIA MERGESORTEM: ' );
        printColl( merge_copy, sch );
        println( '<hr>' );
        printShort( merge_copy, sett );
        println( '<hr>' );
        println( 'WYNIKI SORTOWANIA HYBRIDSORTEM: ' );
        printColl( hybrid_copy, sch );
        println( '<hr>' );
        printShort( hybrid_copy, sett );
    }
    
    println( '' );
    if ( result && result2 ) {
        println( 'TEST SORTOWANIA: ok' );
    } else {
        println( 'TEST SORTOWANIA: zle' ); 
    }
    println( '<hr>' );
    
    return result;
};

// checks filter function
// WARNING: tests only if elements that passed through a filter should pass,
// does not check if some elements that didn't passed, shouldn't pass
function check_filter( data, filter, sch, debug ) {
    var filtered_data = filter_coll( data, filter );
    
    var i;
    var j;
    var key;
    var value;
    var border_value;
    var pref;
    var result = true;
    
    for ( i = 0; i < data.length; i += 1 ) {
        for ( j = 0; j < filter.length; j += 1 ) {
            key = filter[j].name;
            pref = filter[j].pref;
            border_value = filter[j].value;
            
            value = data[i].key;
            if ( ( pref == 1 && value < border_value ) ||
                 ( pref == -1 && value > border_value ) ) {
                print( 'Blad, obiekt nr: ' ); print( i );
                print( 'parametr: ' ); print( key );
                print( 'wartosc: ' ); print( value );
                print( 'wartosc_graniczna: ' ); print( border_value );
                print( 'preferencja: ' ); println( pref );
                result = false;
            }
        }
    }
    
    if ( debug ) {
        printColl( filtered_data, sch );
    }
    
    println( '' );
    
    if ( result ) {
        println( 'TEST FILTROWANIA: ok' );
    } else {
        println( 'TEST FILTROWANIA: zle' ); 
    }
    println( '<hr>' );
};


/*****************************************************************************
 *                                                                           *
 *                             TESTS                                         *
 *                                                                           *
 *****************************************************************************/

 // schema of data
var schema1 = [ { key: 'name' },
                { key: 'val1' },
                { key: 'val2' },
                { key: 'val3' }
];

// preferences deciding when an object is bigger than another
var setting1 = [ { name: 'val1', pref: 1 },
                 { name: 'name', pref: -1 },
                 { name: 'val2', pref: 1 },
                 { name: 'val3', pref: -1 }
];

// used to filter data
var filter = [ { name: 'val1', pref: '1', value: '499' },
               { name: 'val1', pref: '-1', value: '750' },
               { name: 'val2', pref: '1', value: '10' },
               { name: 'val2', pref: '-1', value: '40' }
];


function test_all() {
    compare_sorts( data_5k, setting1, schema1, true );
    check_filter( data_5k, filter, schema1, true );
};

println( '--------> test_all() <--------');
test_all();

function measure_time() {
    var start_bubble, start_merge, start_hybrid;
    var elapsed_bubble, elapsed_merge, elapsed_hybrid;
    var bubble_copy = clone_obj( data_10k );
    var merge_copy = clone_obj( data_10k );
    var hybrid_copy = clone_obj( data_10k );
    
    start_bubble = new Date().getTime();
    bubble_sort( bubble_copy, setting1 );
    elapsed_bubble = new Date().getTime() - start_bubble;
    print( 'elapsed_bubble: ' );
    println( elapsed_bubble );
    
    start_merge = new Date().getTime();
    merge_sort( merge_copy, setting1 );
    elapsed_merge = new Date().getTime() - start_merge;
    print( 'elapsed_merge: ' );
    println( elapsed_merge );
    
    start_hybrid = new Date().getTime();
    hybrid_sort( hybrid_copy, setting1, 5 );
    elapsed_hybrid = new Date().getTime() - start_hybrid;
    print( 'elapsed_hybrid: ' );
    println( elapsed_hybrid );
};

println( '--------> measure_time() <--------' );
measure_time();
println( '<hr>' );