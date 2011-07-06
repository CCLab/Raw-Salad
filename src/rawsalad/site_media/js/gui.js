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

var _gui = (function () {

// P U B L I C   I N T E R F A C E
    var that = {};

    that.init_gui = function () {
        // hide what's not needed now
        $('#sort-form').hide();
        $('#filter-form').hide();
        $('#table-tab').click( function () {
            $('#table-container').show();
            $('#download-container').hide();
            $('#permalink-container').hide();

            $('#tabs')
                .find('div')
                .removeClass('active')
                .addClass('inactive');

            $(this)
                .addClass('active')
                .removeClass('inactive');
        });
        $('#download-container').hide();
        $('#download-tab').click( function () {
            $('#table-container').hide();
            $('#download-container').show();
            $('#permalink-container').hide();

            $('#tabs')
                .find('div')
                .removeClass('active')
                .addClass('inactive');

            $(this)
                .addClass('active')
                .removeClass('inactive');
        });
        $('#permalink-container').hide();
        $('#permalink-tab').click( function () {
            $('#table-container').hide();
            $('#download-container').hide();
            $('#permalink-container').show();

            $('#tabs')
                .find('div')
                .removeClass('active')
                .addClass('inactive');

            $(this)
                .addClass('active')
                .removeClass('inactive');
        });
        $('#download-form').hide();
        $('#download-button').click( _download.current_sheet );
        $('#application').hide();

          $('#download-container').find('.radio > input').attr( 'disabled', 'true' );
          $('#download-container').find('.check > input').change( function () {
            if( $(this).attr('checked') ) {
              $('#download-container').find('.radio > input').attr( 'disabled', '' );
            }
            else {
              $('#download-container').find('.radio > input').attr( 'disabled', 'true' );
            }
          });
        _tools.prepare_tools();

        // arm open/close button and hide it!
        $('#open-close-choose-panel')
            .click( function () {
                // if choose panel is open
                if( $('#choose-panel:visible').length > 0 ) {
                    hide_choose_panel();
                }
                else {
                    show_choose_panel();
                }
            })
            .hide();

        // arm back-to-datasets button
        $('#back-to-datasets')
            .hover(
                function () {
                    $(this)
                        .attr( 'src', '/site_media/img/datasets_over.png' )
                        .css('cursor', 'pointer');
                },
                function () {
                    $(this).attr( 'src', '/site_media/img/datasets.png' );
                }
            )
            .click( function () {
                $('#info-title')
                    .html('Dostępne kolekcje');
                $('#info-text')
                    .html('Wybierz jedną z dostępnych kolekcji danych.');

                $(this)
                    .hide();
                $('#choose-perspectives')
                    .hide();
                $('#choose-datasets')
                    .show();

                // clear the perspectives list
                $('#choose-perspectives')
                    .html('');
            })
            .hide();

        $('#choose-perspectives').hide();
        init_choose_panel();
    };


    // used once when some perspective is chosen for the very first time
    that.init_app = function ( collection_name ) {
        $('#open-close-choose-panel')
            .show();

        that.create_sheet_tab({
            // TODO move name from func arg to store!!
            name: collection_name,
            group_nr: _store.active_group_index(),
            sheet_nr: _store.active_sheet_index()
        });

        $('#application').show();
        that.make_zebra();
        hide_choose_panel();
    }


    that.create_sheet_tab = function ( args ) {
        var html = [];

        var group_nr = args.group_nr || _store.active_group_index();
        var sheet_nr = args.sheet_nr || _store.active_sheet_index();
        var sheet_name = args.name || "Arkusz " + group_nr + '-' + sheet_nr;
        var filtered_sheet = args.filtered_sheet;

        var group_changed = _store.active_group_index() !== group_nr;
        var sheet_changed = _store.active_sheet_index() !== sheet_nr;
        var new_tab;

        html.push( '<div id="snap-' + group_nr + '-' + sheet_nr + '" ' );
        html.push( 'class="snapshot active" ' );
        html.push( 'title="', sheet_name, '">' );
        html.push( sheet_name.length > 13 ?
                   sheet_name.slice( 0, 10 ) + '...' :
                   sheet_name );
        html.push( '</div>' );

        new_tab = $( html.join('') );

        $('.snapshot').removeClass('active');
        new_tab
            .addClass( 'active' )
            .click( function () {
                var id_elements = $(this).attr('id').split('-');
                var group_nr = id_elements[1];
                var sheet_nr = id_elements[2];

                $('.snapshot').removeClass('active');
                $(this).addClass('active');

                _store.active_group( group_nr );
                _store.active_sheet( sheet_nr );

                _table.clean_table();
                _table.init_table();
            });

        if( sheet_nr === 0 ) {
            new_tab.insertBefore( '#save-snapshot' );
        }
        else {
            new_tab.insertAfter( '#snap-'+group_nr+'-'+(sheet_nr-1));
        }

        if( $('.snapshot').length == 10 ) {
            $('#save-snapshot' ).hide();
        }

        _store.active_sheet( sheet_nr );
        _store.active_group( group_nr );

        _table.clean_table();
        _table.init_table( filtered_sheet );
    };


    that.make_zebra = function () {
        $('tbody > tr').not(':hidden').each( function ( i ) {
            if( i % 2 === 0 ) {
                $(this).removeClass( 'odd' );

                $(this).addClass( 'even' );
            }
            else {
                $(this).removeClass( 'even' );
                $(this).addClass( 'odd' );
            }
        });
    };


    that.highlight_node = function () {
        var a_root = $('tr[data-selected="true"]');
        // next a-level node
        var a_root_index = parseInt( a_root.attr( 'data-index' ), 10 );
        var next = $('tr[data-index='+ (a_root_index + 1) +']');

        if( a_root.length === 0 ) {
            // nothing found - nothing to do
            return;
        }
        else {
            // jquery returns a list of objects even for single entity
            a_root = a_root[0];
        }

        a_root
            .siblings()
//            .not(':hidden')
            .addClass('dim');

        // make a-root background black
        $('tr.root').removeClass('root');
        a_root.addClass('root');

        // highlight the subtree
        _utils.with_subtree( a_root.attr('id'), function () {
            // uses 'this' instead of '$(this)' for fun.call reason
            this.removeClass( 'dim' );
        });

        // add the bottom border
        $('.next').removeClass('next');
        next.addClass('next');

//        that.make_zebra();
    }


    return that;


// P R I V A T E   I N T E R F A C E
    function show_choose_panel() {
        $('#choose-panel')
            .slideDown( 400 );

        $('#application')
            .animate({ opacity: 0.25 }, 300 );

        $('#open-close-choose-panel')
            .html('zwiń');
    }


    function hide_choose_panel() {
        $('#choose-panel')
            .slideUp( 400 );

        $('#application')
            .animate({ opacity: 1 }, 300 );

        $('#open-close-choose-panel')
            .html('zmień dane');
    };


    function init_choose_panel() {
        var i;
        var html = [];
        var datasets = _store.meta_datasets();
        var len = datasets.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );

        html.push( '<div class="left">' );
        for( i = 0; i < len; i += 1 ) {
            html.push( '<div class="position" ');
            html.push( 'data-set-id="', datasets[i]['idef'], '">' );
            html.push( '<div class="title">' );
            html.push( datasets[i]['name'] );
            html.push( '</div>' );
            html.push( '<div class="description">' );
            html.push( datasets[i]['description'] );
            html.push( '</div>' );
            html.push( '<div class="more">Zobacz dane</div>' );
            html.push( '</div>' );

            if( i === mid ) {
                html.push( '</div><div class="left second-column">' );
            }
        }
        html.push( '</div>' );
        $('#choose-datasets')
            .append( $( html.join('') ))
            .find( '.position' )
            .find( '.more' )
            .click( function () {
                var dataset_id = $(this).parent().attr( 'data-set-id' );

                create_perspectives_panel( dataset_id );

                $('#choose-datasets')
                    .hide();
            });
    };

    function create_perspectives_panel( dataset_id ) {
        var i, j;
        var html = [];
        var perspectives = _store.meta_perspectives( dataset_id );
        var len = perspectives.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );
        var issues;
        var name;

        html.push( '<div class="left">' );
        for( i = 0; i < len; i += 1 ) {
            issues = perspectives[i]['issues'];

            html.push( '<div class="position" ' );
            html.push( 'data-set-id="', dataset_id, '" ' );
            html.push( 'data-per-id="', perspectives[i]['idef'], '">' );
            html.push( '<div class="title">' );
            html.push( perspectives[i]['name'] );
            html.push( '</div>' );
            html.push( '<div class="description">' );
            html.push( perspectives[i]['description'] );
            html.push( '</div>' );
            // iterates in revers order because of CSS "float: right"
            for( j = issues.length-1; j >= 0; j -= 1 ) {
                html.push( '<div class="more" ' );
                html.push( 'data-issue="', issues[j], '">' );
                html.push( issues[j] );
                html.push( '</div>' );
            }
            html.push( '<div class="more-desc">Zobacz dane:</div>' );
            html.push( '</div>' );

            if( i === mid ) {
                html.push( '</div><div class="left second-column">' );
            }
        }
        html.push( '</div>' );

        $('#info-title')
            // TODO interface this call!!!
            .html( _store.meta_datasets()[ dataset_id ]['name'] );
        $('#info-text')
            .html('Wybierz jedno z wydań danych.');

        $('#back-to-datasets')
            .show();

        $('#choose-perspectives')
            .append( $( html.join('') ))
            .show()
            .find( '.position' )
            .find( '.more' )
            .click( function () {
                var col_id = {
                    dataset: $(this).parent().attr( 'data-set-id' ),
                    perspective: $(this).parent().attr( 'data-per-id' ),
                    issue: $(this).attr( 'data-issue' )
                };

                // if new group is created, get data and show table
                if( _store.create_new_group( col_id ) ) {
                    // get top-level data from db
                    _db.get_init_data();
                }
                else {
                    // go back to application with focus on requested sheet
                    hide_choose_panel();
                }
            });
    };

})();
