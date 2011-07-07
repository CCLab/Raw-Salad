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

    // ids = { '0': [{ id: 2, scope: 'full' }, { id: 3, scope: 'sheet' }], '4': [{ id: 1, scope: 'sheet' }] }
    that.selected = function ( ids ) {
        var i;
        var group, sheet;
        var csv_string = '';

        for( i in ids ) {
            ids[i].forEach( function ( e ) {
                if( e[scope] === 'full' ) {
                    // get data directly from server!!
                }
                else {
                    sheet = _store.get_sheet( i, e[id] );
                    csv_string += add_children( sheet )
                }
            }
        }

        console.log( csv_string );
    };


    that.current_sheet = function () {
        var i, j;
        var data = '';
        var html = [];
        var form;
        var columns, rows;

        var add_children = function ( parent ) {
            var i, node;
            var children = _store.active_rows().filter( function ( e ) {
                return e['data']['parent'] === parent;
            });

            if( children.length === 0 ) {
                return;
            }

            for( i = 0; i < children.length; i += 1 ) {
                node = children[i]['data'];
                data += node['idef'] + ';';
                if( !!node['parent'] === false ) {
                    data += ';'
                }
                else {
                    data += node['parent'] + ';';
                }
                data += node['level'] + ';';

                for( j = 0; j < columns.length; j += 1 ) {
                    data += node[ columns[j]['key'] ];
                    data += ';';
                }
                data += '|';

                if( node['hidden'] === true ) {
                    continue;
                }
                else {
                    add_children( node['idef'] );
                }
            }
        };


        columns = _store.active_columns().filter( function ( e ) {
                return e['basic'] === true;
           });

        _assert.not_equal( columns.length, 0,
                           ">> DOWNLOAD <br/>Columns length === 0" );

        data += 'ID;Rodzic;Poziom;';

        for( i = 0; i < columns.length; i += 1 ) {
            data += columns[i]['label'];
            data += ';';
        }
        data += '|';

        add_children( null );

        $('#download-form')
            .find('input')
            .val( data.slice( 0, data.length-1 ) )
            .end()
            .submit();
    };

    return that;


//  P R I V A T E   I N T E R F A C E

        function add_children( sheet, parent, result ) {
            var parent = parent || null;
            var result = result || '';
            var i, node;
            var columns = sheet['columns'];
            var children = sheet['rows'].filter( function ( e ) {
                return e['data']['parent'] === parent;
            });

            if( children.length === 0 ) {
                return result;
            }

            for( i = 0; i < children.length; i += 1 ) {
                node = children[i]['data'];
                result += node['idef'] + ';';
                if( !!node['parent'] === false ) {
                    result += ';'
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

                if( node['hidden'] === true ) {
                    continue;
                }
                else {
                    add_children( sheet, node['idef'], result );
                }
            }
        };


})();
