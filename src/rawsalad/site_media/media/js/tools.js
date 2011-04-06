//  T O O L S   A N D   U T I L I T I E S

// this function cames from jQuery API example
$.fn.equalize_heights = function() {
  return this.height( Math.max.apply(this, $(this).map(function(i,e){ return $(e).height() }).get() ) )
}

var filter = function ( fn, list ) {
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

Math.randint = function ( x ) {
    return Math.floor( Math.random() * x );
};
 
