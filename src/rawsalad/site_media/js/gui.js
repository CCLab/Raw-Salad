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
        $('#download-form').hide();
        $('#download-button').click( _download.current_sheet );
        $('#application').hide();

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
    that.init_app = function () {
        $('#open-close-choose-panel')
            .show();

        // make it "not hidden" (invisible though) to make zebra
        $('#application')
            .css( 'opacity', 0 )
            .show();

        that.make_zebra();
        hide_choose_panel();
    }


    that.make_zebra = function () {
        // TODO make it work with only current sheet
        $('tr').not(':hidden').each( function ( i ) {
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


    that.create_sheet_tab = function ( args ) {
        var html = [];
        var sheet_name = args.name;
        var new_sheet_nr = args.sheet_nr;
        var group_nr = args.group_nr;
        var filtered_sheet = args.filtered_sheet;
        var predecessor;
        var group_changed;

        html.push('<div id="snap-' + group_nr.toString() + '-' +
                  new_sheet_nr.toString() + '" class="snapshot active">');
        html.push(sheet_name);
        html.push('</div>');

        if ((new_sheet_nr - 1) === 0) {
            predecessor = $( '#basic-snapshot-' + group_nr.toString() );
        } else {
            predecessor = $( '#snap-' + group_nr.toString() +
                             '-' + (new_sheet_nr - 1).toString() );
        }

        $( html.join('') ).insertAfter( predecessor );

        $('#snapshots')
            .find('#snap-' + group_nr.toString() + '-' + new_sheet_nr.toString() )
            .each( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');
            })
            .click( function () {
                $('.snapshot').removeClass('active');
                $(this).addClass('active');

                group_changed = (_store.active_group_index() !== group_nr);
                if ( _store.active_sheet_index() !== new_sheet_nr || group_changed ) {

                     _sheet.change_active_sheet( {'sheet_nr': new_sheet_nr,
                                                  'group_changed': group_changed,
                                                  'filtered_sheet': filtered_sheet} );
                }
            });
    };

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
            .find('.more' )
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
                    name = col_id['dataset'] + '-' +
                           col_id['perspective'] + '-' +
                           col_id['issue'];
                    create_basic_snapshot_button({
                          'basic_snapshot_name': name
                    });
                }
                else {
                    // go back to application with focus on requested sheet
                    hide_choose_panel();
                }
            });
    };


    function create_basic_snapshot_button( args ) {
        var html = [];
        var max_group_nr;
        var name = args.basic_snapshot_name;

        max_group_nr = _store.max_group_number() - 1;
        html.push('<div id="basic-snapshot-' + max_group_nr.toString() +
                  '" class="basic-snapshot active">');
        html.push(name);
        html.push('</div>');

        $('.basic-snapshot').removeClass('active');
        $( html.join('') )
            .insertBefore('#save-snapshot')
            .click( function () {
                $('.basic-snapshot').removeClass('active');
                $(this).addClass('active');
                _sheet.show_basic_sheet( {'group_nr': max_group_nr} );
            });
    };

})();
