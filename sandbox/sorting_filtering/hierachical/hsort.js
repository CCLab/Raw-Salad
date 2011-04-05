// function used to deep copying objects
// obj - object to copy
// returns copy of that object
function clone_obj( obj ) {
    if ( typeof obj !== 'object' || obj == null ) {
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

// division for integers
// returns ( big div small)
function int_div( big, small ) {
    var rest = big % small;
    var tmp = big - rest;
    return ( tmp / small );
};

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
    compare_value = compare_value * pref;
    return compare_value;
};

// compares two objects, compares their attributes mentioned in sett
// ob1, ob2 - objects to compare
// sett - setting deciding how objects will be compared
// returns -1 -> ob1 < ob2
//          0 -> ob1 == ob2
//          1 -> ob1 > ob2
function compare_obj( ob1, ob2, sett ) {
    var i;
    var res = 0;
    var key;
    var pref;
    
    // for each attribute in sett
    for ( i = 0; i < sett.length; i += 1 ) {
        key = sett[i].name;
        pref = sett[i].pref;
        res = compare_atr( ob1, ob2, key, pref );
        if ( res != 0 ) {
            break;
        }
    }
    return res;
};


/*****************************************************************************
 *                                                                           *
 *                             SORTING                                       *
 *                                                                           *
 *****************************************************************************/

// sorts data with bubble_sort algorithm with setting sett,
// which decides when an object is bigger than another
// data - collection to sort
// sett - setting deciding how to compare two objects
function bubble_sort( data, sett ) {
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
            if ( compare_obj( data[j], data[j+1], sett ) == -1 ) {
                swap( data, j, j+1 );
                /*print( j );
                print( ' <-> ' );
                println( j+1 );*/
            }
        }
    }
};

// sorts data in range [start; end] with bubble_sort algorithm
// with setting sett, which decides when an object is bigger than another
// data - collection to sort
// sett - setting deciding how to compare two objects
// start - index of the first element of data to sort
// end - index of the last element of data to sort
function bubble_sort_r( data, sett, start, end ) {
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
            if ( compare_obj( data[j], data[j+1], sett ) == -1 ) {
                swap( data, j, j+1 );
                /*print( j );
                print( ' <-> ' );
                println( j+1 );*/
            }
        }
    }
};

// merges two subarrays, 1st: data[start, middle], 2nd: data[middle+1, end]
// result is that data[start, end] is sorted
// data - collection to sort
// sett - decides how objects are compared
function merge( data, sett, start, middle, end) {
    var i = 0;
    var j = 0;
    var ind = start;
    
    var array1 = data.slice(start, middle + 1);
    var array2 = data.slice(middle + 1, end + 1);
    
    // put the smallest actually element in the first available place in data
    //print('MERGE: ['); print(start); print('--'); print(end); println(']');
    while ( i < array1.length && j < array2.length ) {
        //print( 'i: '); print( i ); print( 'j: '); print( j ); print('| ');
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
    //println('');
};

// sorts part of an array data with merge sort algorithm using setting sett
// data - collection to sort
// sett - decides how objects are compared
// first index = start, last index = end
function merge_sort_r( data, sett, start, end ) {
    if ( start > end - 1 )
        return;
    var middle = int_div( (start + end), 2);
    
    // sort two arrays separately
    merge_sort_r( data, sett, start, middle );
    merge_sort_r( data, sett, middle + 1, end );
    
    // merge sorted arrays
    merge( data, sett, start, middle, end);
};

// sorts the whole array with merge sort algorithm using setting sett
// data - collection to sort
// sett - decides how objects are compared
function merge_sort( data, sett ) {
    merge_sort_r( data, sett, 0, data.length - 1 );
};

// sorts part of an array data with a hybrid sorting algorithm
// which uses merge sort for dividing big part of an array and mergin them
// and bubble sort for sorting small arrays. Uses setting sett.
// data - collection to sort
// sett - decides how objects are compared
// first index = start, last index = end
// border - value indicating when bubble_sort should be used
function hybrid_sort_r( data, sett, start, end, border ) {
    if ( start > end - border ) // an array is small enough to use bubble sort
        bubble_sort_r( data, sett, start, end);
    else {
        var middle = int_div( (start + end), 2);
        
        // sort two arrays separately
        hybrid_sort_r( data, sett, start, middle, border );
        hybrid_sort_r( data, sett, middle + 1, end, border );
        
        // merge sorted arrays
        merge( data, sett, start, middle, end);
    }
};

// sorts the whole array with hybrid sort(merge sort + bubble sort)
// algorithm using setting sett
// data - collection to sort
// sett - decides how objects are compared
// border - value indicating when bubble sort should be used
function hybrid_sort( data, sett, border ) {
    hybrid_sort_r( data, sett, 0, data.length - 1, border);
};

/*****************************************************************************
 *                                                                           *
 *                             FILTERING                                     *
 *                                                                           *
 *****************************************************************************/

// name: name of attribute which will be checked during filtering,
// pref: preference 1 means -> bigger values are good, -1 -> lower values are good
// value - border value of the attribute
/*var mask = [
            { name: 'y2010', pref: '1', value: '100000' },
            { name: 'y2011', pref: '-1', value: '300000' }
];*/

// checks if specfied attribute of an object passes a filter
// obj - object to check
// atr - name of the attribute to check
// pref - decides if value of the attribute should be higher or lower
// value - border value
// returns true if yes, false if not
function check_atr( obj, atr, pref, value ) {
    var obj_val = obj[atr];
    
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
/*var schema1 = [ { key: 'name' },
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
println( '<hr>' );*/

var schema1 = [ { key: 'idef' },
                { key: 'level' },
                { key: 'name' },
                { key: 'parent' },
                { key: 'v_total' },
                { key: 'v_nation' }
];

var setting1 = [ { name: 'v_total', pref: 1 },
                 { name: 'v_nation', pref: -1}
];


function compare_obj_budg( ob1, ob2 ) {
    var i;
    var res = 0;
    var key;
    var pref;
    var id1, id2;
    var tokens1, tokens2;
    var min_length;
    var res = 0;
    var x1, x2;
    
    if ( ob1.level !== "d" ) {
        id1 = ob1.idef;
    } else {
        id1 = ob1.parent;
    }
    
    if ( ob2.level !== "d" ) {
        id2 = ob2.idef;
    } else {
        id2 = ob2.parent;
    }
    tokens1 = id1.split( '-' );
    tokens2 = id2.split( '-' );
    
    min_length = ( tokens1.length < tokens2.length ) ?
                                            tokens1.length : tokens2.length;
    for ( i = 0; i < min_length; i += 1 ) {
        if ( parseInt( tokens1[i] ) < parseInt( tokens2[i] ) ) {
            res = 1;
            break;
        } else if ( parseInt( tokens1[i] ) > parseInt( tokens2[i] ) ) {
            res = -1;
            break;
        }
    }
    
    if ( res === 0 ) {
        if ( ob1.level < ob2.level ) {
            res = 1;
        } else if ( ob1.level > ob2.level ) {
            res = -1;
        }
        /*if ( ob1.level !== 'd' ) {
            res = 1;
        } else if ( ob2.level !== 'd' ) {
            res = -1;
        }*/
        else {
            tokens1 = ob1.idef.split( '-' );
            tokens2 = ob2.idef.split( '-' );
            x1 = tokens1[tokens1.length - 1].substring( 2 );
            x2 = tokens2[tokens2.length - 1].substring( 2 );
            x1 = parseInt( x1 );
            x2 = parseInt( x2 );
            
            if ( x1 < x2 ) {
                res = 1;
            } else {
                res = -1;
            }
        }
    }
    
    return res;
};


// merges two subarrays, 1st: data[start, middle], 2nd: data[middle+1, end]
// result is that data[start, end] is sorted
// data - collection to sort
function init_merge( data, start, middle, end) {
    var i = 0;
    var j = 0;
    var ind = start;
    
    var array1 = data.slice(start, middle + 1);
    var array2 = data.slice(middle + 1, end + 1);
    
    // put the smallest actually element in the first available place in data
    //print('MERGE: ['); print(start); print('--'); print(end); println(']');
    while ( i < array1.length && j < array2.length ) {
        //print( 'i: '); print( i ); print( 'j: '); print( j ); print('| ');
        if ( compare_obj_budg( array1[i], array2[j] ) == 1 ) {
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
    //println('');
};

// Initial sort part of an array data(only works for budget collection)
// data - collection to sort
// sett - decides how objects are compared
// first index = start, last index = end
function init_sort_r( data, start, end ) {
    if ( start > end - 1 )
        return;
    var middle = int_div( (start + end), 2);
    
    // sort two arrays separately
    init_sort_r( data, start, middle );
    init_sort_r( data, middle + 1, end );
    
    // merge sorted arrays
    init_merge( data, start, middle, end);
};

// Initial sort of data(only works for budget collection)
// data - collection to sort
function init_sort( data ) {
    init_sort_r( data, 0, data.length - 1 );
};

function swap_lev_c( data, ind1, ind2 ) {
    var children1 = 0;
    var children2 = 0;
    var i;
    var mid;
    var max;
    var j;
    
    for ( i = ind1 + 1; i < data.length; i += 1 ) {
        if ( data[i].level !== 'd' ) {
            break;
        }
        children1 += 1;
    }
    for ( i = ind2 + 1; i < data.length; i += 1 ) {
        if ( data[i].level !== 'd' ) {
            break;
        }
        children2 += 2;
    }
    if ( children1 === children2 ) {
        for ( i = 0; i < children1; i += 1 ) {
            swap( data, ind1 + i, ind2 + i );
        }
    } else {
        if ( ind1 < ind2 ) {
            max = ind2 + children2;
            mid = ( ind1 + max ) / 2;
        } else {
            max = ind1 + children1;
            mid = ( ind2 + max ) / 2;
        }
        for ( i = ind1, j = 0; i <= mid; i += 1, j += 1 ) {
            swap( data, i, max - j );
        }
    }
};

function sort( data, sett1 ) {
    var i;
    var j;
    var rows = [ ];
    var ind1;
    var ind2;
    var a;
    var b;
    var c;
    
    for ( i = 0; i < data.length; i += 1 ) {
        if ( data[i].level !== 'c' ) {
            continue;
        }
        
        for ( j = i; j < data.length; j += 1 ) {
            if ( data[j].level === 'c' ) {
                rows.push( j );
            } else if ( data[j].level < 'c' ) {
                break;
            }
        }
    
        for ( a = 0, c = 0; a < rows.length - 1; a += 1, c+= 1 ) {
            for ( b = 0; b < rows.length - c - 1; b += 1 ) {
                // obiekt o mniejszym numerze jest lepszy, wiersze lepsze na górze
                
                ///////////////////////////////////////////////////
                // glupie porownanie, bo sprawdza nastepny wiersz po wierszu z poziomem c,
                // a co jak jest kilka wierszy dzieci poziomu d wzgledem tego wiersza c?
                // nie wiem, jak dokladnie sortowac, wzgledem ktorego poziomu:(
                ///////////////////////////////////////////////////
                ind1 = rows[b]; 
                ind2 = rows[b+1];
                if ( compare_obj( data[ind1+1], data[ind2+1], sett ) == -1 ) {
                    swap_lev_c( data, ind1, ind2 );
                }
            }
        }
        
        i = j - 1;
        rows = [ ];
    }
};



var dejta_copy = clone_obj( data['rows'] );

init_sort( dejta_copy );

print( ' wynik: ' );
printColl( dejta_copy, schema1 );



// does not work
sort( dejta_copy, setting1 );
println( '<hr>' );
printColl( dejta_copy, schema1 );
