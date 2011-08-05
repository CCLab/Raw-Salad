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

var _db = (function () {

//  P U B L I C   I N T E R F A C E
    var that = {};

    that.save_permalink = function ( groups ) {
        // inform user it can take a while!!
        _utils.create_preloader( 'Zapisuję arkusze w bazie danych.<br />To może chwilę potrwać...' );

        $.ajax({
            url: 'store_state/',
            type: 'GET',
            data: {
                state: JSON.stringify( groups )
            },
            dataType: 'json',
            success: function ( received_data ) {
              $('#app-sh-permalink')
                .slideDown( 100 )
                .find('input')
                .val( 'http://otwartedane.pl/'+received_data['id'] )
                .focus()

                _utils.clear_preloader();
            }
        });
    };

    that.search = function ( query, scope, strict ) {
        var data = {
            query: query,
            scope: scope.toString(),
            strict: strict.toString()
        };

        $.ajax({
            url: 'search/',
            data: data,
            dataType: 'json',
            success: function ( received_data ) {
                var html = [];
                var tbody = $('#pl-sr-results').find('tbody');
                tbody.empty();

                if( received_data['records_found_total'] === 0 ) {
                    html.push( '<tr style="background-color: #e3e3e3">' );
                    html.push( '<td>Niestety wyszukiwane hasło nie znajduje się wśród zebranych tutaj danych</td>' );
                    html.push( '</tr>' );

                    tbody.append( $( html.join( '' ) ) );
                }
                else {
                    received_data['strict']['result'].forEach( function ( collection ) {
                        var html = [];
                        var single_row;
                        var idefs = [];
                        var results_length = collection['data'].length;
                        var results_limit = 250;

                        html.push( '<tr style="background-color: #e3e3e3">' );
                        html.push( '<td class="pl-sr-results-number right">', collection['data'].length, '</td>' );
                        html.push( '<td class="pl-sr-results-name">' );
                        html.push( '<div class="pl-sr-results-name-text left">', collection['perspective'], '</div>' );
                        html.push( '<div class="pl-sr-results-button left">&gt;</div>' );
                        if( results_length > results_limit ) {
                            html.push( '<div style="font-weight: bold; margin-top:5px; clear: both; color: #7345c6">' );
                            html.push( 'Zbyt wiele wyników - nie sposób ich wyświetlić</div>' );
                        }
                        html.push( '</td>' );
                        html.push( '</tr>' );

                        single_row = $( html.join('') );
                        collection['data'].forEach( function ( result ) {
                            idefs.push( result['idef'] );
                        });

                        if( results_length < results_limit ) {
                            single_row
                                .click( function () {
                                    that.add_search_data({
                                        dataset: collection['dataset'].toString(),
                                        view: collection['view'].toString(),
                                        issue: collection['issue'].toString(),
                                        idef: idefs.toString(),
                                        query: query
                                    });
                                })
                                .find( '.pl-sr-results-name' )
                                    .hover(
                                        function () {
                                            $(this)
                                                .css( 'cursor', 'pointer' )
                                                .find( '.pl-sr-results-name-text' )
                                                .css( 'color', '#1ea3e8' )
                                                .end()
                                                .find( '.pl-sr-results-button' )
                                                .css( 'background-color', '#1ea3e8' );
                                        },
                                        function () {
                                            $(this)
                                                .find( '.pl-sr-results-name-text' )
                                                .css( 'color', '#000' )
                                                .end()
                                                .find( '.pl-sr-results-button' )
                                                .css( 'background-color', '#c1c1c1' );
                                        }
                                    );
                        }

                        tbody.append( single_row );
                    });
                }
                _utils.clear_preloader();

                $('#pl-sr-full')
                    .slideUp( 200 );

                $('#pl-sr-results')
                    .slideDown( 200 )
                    .find('tr')
                    .each( function () {
                        var h = $(this).find('.pl-sr-results-name').height();

                        $(this)
                            .find('.pl-sr-results-number')
                            .height( h );
                    });

                $('#pl-sr-show').show();
            }
        });
    };

    that.add_search_data = function ( search_list ) {
        var col_id = {
            dataset: search_list['dataset'],
            view: search_list['view'],
            perspective: search_list['view'],
            issue: search_list['issue'],
        };
        _utils.create_preloader( "Wczytuję dane z bazy danych" );
        $.ajax({
            url: 'get_searched/',
            data: search_list,
            dataType: 'json',
            success: function ( received_data ) {
                if ( _store.group_exists( col_id ) ) {
                    _sheet.create_searched_sheet( col_id, received_data );
                }
                else {
                    _sheet.add_searched_group( col_id, received_data );
                }
                _utils.clear_preloader();
                _gui.show_table_tab();

                $('#app-tb-datatable > tbody td').each( function () {
                    if( $(this).html().toLowerCase().indexOf( search_list['query'].toLowerCase() ) !== -1 ) {
                        $(this).parent().css( 'background-color', '#F3E58A' );
                    }
                });
            }
        }); // $.ajax
    };

    // gets the top-level from db
    that.get_init_data = function (col_id) {
        // ajax call data object
        var init_data_info = {
            "action": "get_init_data",
            "dataset": col_id.dataset,
            "perspective": col_id.view,
            "issue": col_id.issue
        };

        _utils.create_preloader( "Wczytuję dane z bazy danych" );
        $.ajax({
            data: init_data_info,
            dataType: "json",
            success: function( received_data ) {
                var data = {
			// TODO get rid of colkumns here
			// TODO move it to create sheet function
//                    columns: received_data.perspective.columns,
                    rows: received_data.rows,
                    name: received_data.perspective.perspective
                };

                // create group
                _store.create_group({
                   "dataset": col_id.dataset,
                   "view": col_id.view,
                   "issue": col_id.issue,
                   "columns": received_data.perspective.columns,
                });
                _store.init_basic_sheet( data );
                // create a table
                _table.init_table();
                _utils.clear_preloader();
                // initialize an application
                _gui.init_app( data['name'] );
            }
        });
    };


    // downloads requested nodes, appends them to object with other nodes
    // and adds html code for new nodes
    that.download_node = function ( parent_id ) {
        // ajax call data object
        var download_data = {
            action: 'get_node',
            dataset: _store.dataset(),
            perspective: _store.view(),
            issue: _store.issue(),
            parent: parent_id,
        };

        $.ajax({
            data: download_data,
            dataType: 'json',
            success: function( received_data ) {

                // store new data in model
                _store.add_data( received_data );
                // render new data in table
                // TODO is parent_id really necessary?!
                _table.add_node( parent_id );

                // if it was a basic sheet sign it changed
                if ( _store.active_sheet_index() === 0 ) {
                    _store.active_basic_changed( true );
                }
            }
        });
    };

    return that;

})();
