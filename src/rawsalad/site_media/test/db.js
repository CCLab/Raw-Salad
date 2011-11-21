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

    that.get_context = function ( idef ) {
        console.log( '>>>> idef: ' + idef );
        $.ajax({
            url: 'get_context/',
            data: { idef: idef },
            type: 'GET',
            success: function ( res ) {
                console.log( '>>>> results:' );
                console.log( res )
            },
            error: function ( err ) {
                console.log( '>>>> ERROR:\n' + err )
            }
        });
    };


    that.save_permalink = function ( groups ) {
        // inform user it can take a while!!
        _utils.create_preloader( 'Zapisuję arkusze w bazie danych.<br />To może chwilę potrwać...' );

        $.ajax({
            url: _basic_url + 'store_state/',
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
            query: query.toLowerCase(),
            scope: scope.toString(),
            strict: strict.toString()
        };

        $.ajax({
            url: _basic_url + 'search/',
            data: data,
            dataType: 'json',
            success: function ( received_data ) {
                var html = [];
                var head_html = [];
                var table;
                var last_dataset = null;
                var results_panel = $('#pl-sr-results-panel');
                results_panel.empty();
                if( received_data['records_found_total'] === 0 ) { 
                    $('.pl-sr-results-col').hide();               
                    html.push( '<p> Niestety wyszukiwane hasło nie znajduje się wśród zebranych tutaj danych</p>' );
//                    results_panel.append( $( html.join( '' ) ) );
                }
                else {
                    $('.pl-sr-results-col').show();
                    received_data['result'].sort( function( a, b){
                        return a['dataset'] - b['dataset'];
                    });                                                                               
                    received_data['result'].forEach( function ( data_view ) {
                        var html = [];                        
                        var single_row = [];
                        var results_length = data_view['data'].length;
                        
                        
                        if ( data_view['dataset'] !== last_dataset ) {
                            if ( last_dataset !== null ) {
                                results_panel.append( $( head_html.join('') ) );
                                results_panel.append( table );
                            }
                            last_dataset =  data_view['dataset'];
                            head_html = [];
                            head_html.push( '<p class="pl-sr-results-colection-name">', _store.get_dataset_name( last_dataset ), '</p> ' );
                            table = $('<table><tbody></tbody></table>');                            
                        }
                       
                        html.push( '<tr>');
                        html.push( '<td class="pl-sr-results-number">' );
                        html.push( results_length );
                        html.push( '</td>' );    
                        html.push( '<td class="pl-sr-results-name">' );
                        html.push( data_view['perspective'] );
                        html.push( '</td>' );
                        single_row = $( html.join('') );
                        single_row
                            .click( function () {
                                that.add_search_data({
                                    dataset: data_view['dataset'].toString(),
                                    view: data_view['view'].toString(),
                                    issue: data_view['issue'].toString(),
                                    idef: data_view['data'].toString(),
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
                        table.append( single_row );
                    });
                    results_panel.append( $( head_html.join('') ) );
                    results_panel.append( table );

                }
                results_panel.append( $( html.join('') ));
                _utils.clear_preloader();

                $('#pl-sr-full')
                    .slideUp( 200 );

                $('#pl-sr-more')
                    .html('Pokaż zaawansowane');

                $('#pl-sr-results')
                    .slideDown( 200 )
                    .find('tr')
                    .each( function () {
                        var name_height = $(this).find('.pl-sr-results-name').height();
                        $(this)
                            .find('.pl-sr-results-number')
                            .height( name_height );
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
            query: search_list['query'],
        };
        _utils.create_preloader( "Wczytuję dane z bazy danych" );
        $.ajax({
            url: _basic_url + 'get_searched/',
            data: search_list,
            dataType: 'json',
            success: function ( received_data ) {
                console.log( '>>>> received object' );
                console.log( received_data );

                _sheet.display_search_result( col_id, received_data );         // TEST             
                _utils.clear_preloader();
 
//                if ( _store.group_exists( col_id ) ) {
//                    _sheet.create_searched_sheet( col_id, received_data );
//                }
//                else {
//                    _sheet.add_searched_group( col_id, received_data );
//                }

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
            url: _basic_url,
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
            url: '/app/',
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
