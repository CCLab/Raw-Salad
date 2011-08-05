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

var _download = (function () {

    var that = {};

    // ids = { '0': [ '2', '4' ], '4': [ '1' ], 'full': [ '0-1-2012.csv', '3-2-2011.csv' ] }
    that.selected = function ( ids ) {
        var i, columns;
        var group, sheet;
        var csv_string = '';

        for( group_id in ids ) {
            ids[group_id].forEach( function ( e ) {
                if( group_id === 'full' ) {
                    csv_string += e;
                }
                else {
                    sheet = _store.get_sheet( group_id, e );
                    columns = sheet['columns'];

                    csv_string += 'ID;Rodzic;Poziom;';

                    for( i = 0; i < columns.length; i += 1 ) {
                        csv_string += columns[i]['label'];
                        csv_string += ';';
                    }
                    csv_string += '|';

                    if( sheet['filtered'] ) {
                        csv_string += add_filtered( sheet );
                    }
                    else {
                        csv_string += add_total( sheet );
                        csv_string += add_children( sheet );
                    }
                }
                // end of file string
                csv_string += '--file--';
            });
        }

        window.onbeforeunload = null;

        // send it to server for further processing!!
        $('#pl-dl-hidden-form')
            .find('input')
            .val( csv_string )
            .end()
            .submit();
    };

    return that;


//  P R I V A T E   I N T E R F A C E

    function add_filtered( sheet ) {
        var result = '';
        var rows_copy = [];
        $.extend( true, rows_copy, sheet['rows'] );
        
        if ( !sheet['sorted'] ) {
            rows_copy.sort( function (a, b) {
                if ( a['data']['idef_sort'] < b['data']['idef_sort'] ) {
                    return -1;
                }
                else {
                    return a['data']['idef_sort'] > b['data']['idef_sort'];
                };
            });
        }
        rows_copy.forEach( function ( e ) {
            result = add_child( e['data'], sheet['columns'], result );
        });

        return result;
    }


    function add_row( node, columns ) {
        var result = '';

        result += node['idef'] + ';';
        if( !!node['parent'] === false ) {
            result += ';';
        }
        else {
            result += node['parent'] + ';';
        }
        result += node['level'] + ';';

        columns.forEach( function ( e ) {
            result += node[ e['key'] ];
            result += ';';
        });

        result += '|';

        return result;
    }


    function add_child( node, columns, csv ) {
        var result = '';
        var parent_position = csv.indexOf( '|' + node['parent'] );
        var next_position;

        result += node['idef'] + ';';
        result += node['parent'] + ';';
        result += node['level'] + ';';

        columns.forEach( function ( e ) {
            result += node[ e['key'] ];
            result += ';';
        });

        result += '|';

        if( parent_position !== -1 ) {
            next_position = csv.indexOf( '|', parent_position+1 ) + 1;
            csv = csv.slice( 0, next_position ) + result + csv.slice( next_position );
        }
        else {
            csv += result;
        }

        return csv;
    }


    function add_children( sheet, parent, result ) {
        var parent = parent || null;
        var result = result || '';
        var i, node, open;
        var columns = sheet['columns'];
        var children = sheet['rows'].filter( function ( e ) {
            return e['data']['parent'] === parent;
        });

        if( children.length === 0 ) {
            return result;
        }

        for( i = 0; i < children.length; i += 1 ) {
            node = children[i]['data'];
            open = children[i]['state']['open'];

            result += node['idef'] + ';';
            if( !!node['parent'] === false ) {
                result += ';';
            }
            else {
                result += node['parent'] + ';';
            }
            result += node['level'] + ';';

            for( j = 0; j < columns.length; j += 1 ) {
                result += node[ columns[j]['key'] ];
                result += ';';
            }
            result += '|';

            if( open === false ) {
                continue;
            }
            else {
                result = add_children( sheet, node['idef'], result );
            }
        }
        return result;
    }

    function add_total( sheet ) {
        var result = '';
        var columns = sheet['columns'];
        var total;

        try {
            total = sheet['rows']['total']['data'];
        }
        catch ( err ) {
            return '';
        }

        result += total['idef'] + ';';
        result += ';';
        result += total['level'] + ';';

        columns.forEach( function ( e ) {
            result += total[ e['key'] ];
            result += ';';
        });
        result += '|';

        return result;
    }

})();
