/**
 *  Assert function by Ayman Hourieh
 *  Licenced under CC BY-NC-SA 3.0
 *  http://aymanh.com/9-javascript-tips-you-may-not-know#assertion
 *  
 *  Usage: 
 *  Assert.assert( exp, message );
 *
 *  For example:
 *  Assert.assert( n != 0, "n === 0" );
 *  sth = x / n;  
 */

var Assert = (function () {
        var AssertionException = function ( message ) {
            this.message = message;
        }

        AssertionException.prototype.toString = function () {
            return "AssertionException: " + this.message;
        };

        var assert = function ( exp, message ) {
            if( !Boolean( exp )) {
                throw new AssertionException( message );
            }
        };
    })();
