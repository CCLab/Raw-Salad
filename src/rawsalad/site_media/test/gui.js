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

        // arm top menu
        $('#top')
            .find('li')
            .click( function () {
                do_panels( $(this) );
            });

        $('#pl-fb-email.info')
            .focus( function () {
                if( $(this).hasClass( 'info' ) ) {
                    $(this)
                        .val( '' )
                        .removeClass('info');
                }
            });

        // arm close bar
        $('#pl-close-bar')
            .click( hide_top_panels );

        // arm application tabs (table/share)
        $('#app-tabs')
            .find('li')
            .click( function () {
                // TODO don't do that if tab already active
                var action = $(this).attr('id').split('-').pop();
                var tabs = $('#app-tabs').find('li');

                tabs.removeClass('active');
                $(this).addClass('active');

                $('.app-container:visible').hide();
                if( action === 'table' ) {
                    $('#app-' + action).show();
                    _gui.refresh_gui();
                }
                else {
                    update_share_tab();
                    $('#app-share').show();
                }
            });

        $('#app-tb-tl-clear-button')
            .click( function () {
                _store.reset_sheet();
                that.refresh_gui();
            });

        // arm back-to-datasets button
        $('.pl-ch-back > img')
            .hover(
                function () {
                    $(this)
                        .attr( 'src', '/site_media/img/datasets_over.png' )
                        .css( 'cursor', 'pointer' );
                },
                function () {
                    $(this).attr( 'src', '/site_media/img/datasets.png' );
                }
            )
            .click( function () {
                var panel = $('#pl-choose');

                panel
                    .find('.panel-title')
                    .html('Dostępne kolekcje')
                panel
                    .find('.panel-desc')
                    .html('Wybierz jedną z dostępnych kolekcji danych.');

                $('#pl-ch-views')
                    .hide()
                    .find('ul')
                    .remove();

                $('#pl-ch-datasets')
                    .show();
            });

        _tools.prepare_tools();


        $('#pl-dl-fl-tb-select')
            .click( function () {
                $('#pl-dl-fl-table')
                    .find('input')
                    .attr( 'checked', 'true' );
            });

        $('#pl-dl-fl-tb-unselect')
            .click( function () {
                $('#pl-dl-fl-table')
                    .find('input')
                    .removeAttr( 'checked' );
            });

        $('#pl-dl-button')
            .click( function () {
                var ids = {};
                var panel = $('#pl-download');
                var checkboxes = panel.find('input:checkbox:checked');

                if( checkboxes.length === 0 ) {
                    return;
                }

                checkboxes.each( function () {
                    var val = $(this).val();
                    var group;
                    var sheet;

                    // it's a full collection
                    if( val.indexOf( 'csv' ) !== -1 ) {
                        try {
                            ids['full'].push( val );
                        }
                        catch ( err ) {
                            ids['full'] = [ val ];

                        }
                    }
                    else {
                        group = val.split('-')[0];
                        sheet = val.split('-')[1];
                        try {
                            ids[ group ].push( sheet );
                        }
                        catch ( err ) {
                            ids[ group ] = [ sheet ];
                        }
                    }
                });

                _download.selected( ids );

                // close download panel
                if( $('#application').is(':visible') ) {
                    hide_top_panels();
                }
                else {
                    $('#tm-choose').trigger( $.Event( 'click' ) );
                }
            });

        $('#pl-fb-button')
            .click( function () {
                $.ajax({
                    url:'feedback/',
                    type: 'POST',
                    data: {
                        email: $('#pl-fb-email').val(),
                        message: $('#pl-fb-message').val()
                    },
                    success: function () {
                        // close feedback panel
                        if( $('#application').is(':visible') ) {
                            hide_top_panels();
                        }
                        else {
                            $('#tm-choose').trigger( $.Event( 'click' ) );
                        }
                    }
                });
            });

        $('#pl-sr-more')
            .click( function () {
                if( $('#pl-sr-full').is(':visible') ) {
                    $('#pl-sr-full').slideUp( 200 );
                    $(this).html( 'Pokaż zaawansowane' );
                }
                else {
                    $('#pl-sr-unselect').trigger( $.Event( 'click' ));
                    $('#pl-sr-full').slideDown( 200 );
                    $(this).html( 'Zamknij zaawansowane' );
                }
            });


        $('#pl-sr-select').click( function () {
            // select all checkboxes
            $('#pl-sr-table')
                .find(':checkbox')
                .attr( 'checked', 'true' );
        });

        $('#pl-sr-unselect').click( function () {
            // unselect all checkboxes
            $('#pl-sr-table')
                .find(':checkbox')
                .removeAttr( 'checked' );
        });

        $('#pl-sr-full').hide();
        $('#pl-sr-results').hide();

        $('#pl-sr-button')
            .click( function () {
                if(  $('#pl-sr-query').val() === '' ) {
                    return;
                }

                _db.search( $('#pl-sr-query').val(), ['0-0-2011', '0-1-2011', '0-1-2012',
                                                      '0-2-2011', '0-2-2012', '1-0-2011',
                                                      '1-1-2011', '1-1-2012', '1-2-2011',
                                                      '1-2-2012', '2-1-2011', '2-2-2011',
                                                      '2-3-2011', '2-4-2011', '3-0-2011',
                                                      '3-1-2011' ], false );
            });

        $('#pl-sr-form')
            .submit( function () {
                $('#pl-sr-button').trigger( $.Event( 'click' ) );
                return false;
            });

        init_choose_panel();
    };


    // used once when some perspective is chosen for the very first time
    that.init_app = function ( collection_name ) {

        if( arguments.length !== 0 ){
            _store.set_active_sheet_name( collection_name );
        }
        that.refresh_gui();

        $('#application').show();
        that.make_zebra();
        hide_top_panels();
    };


    that.refresh_gui = function () {
        var groups = _store.get_all_groups();
        var close_sheet;
        var active_group = _store.active_group_index();
        var active_sheet = _store.active_sheet_index();

        // 1  clear gui,
        $('#app-tb-sheets').empty();

        // 2  new gui
        groups.forEach( function ( group, group_num ){
            group['sheets'].forEach( function ( sheet, sheet_num ) {
                var sheet_name = sheet['name'];
                var html = [];
                var new_sheet;


                html.push( '<li ' );
                html.push( 'id="snap-' + group_num + '-' + sheet_num + '" ' );
                html.push( 'class="sheet tab button" ' );
                html.push( 'title="', sheet_name, '">' );
                html.push( sheet_name.length > 20 ?
                           sheet_name.slice( 0, 17 ) + '...' :
                           sheet_name );
                html.push( '</li>' );

                new_snap = $( html.join('') );
                new_snap
                    .click( function () {
                        _store.active_group( group_num );
                        _store.active_sheet( sheet_num );
                        that.refresh_gui();
                    });

                if( ( group_num === active_group ) && ( sheet_num === active_sheet ) ) {
                    close_sheet = $( '<div class="close-sheet-button button" >x</div>' );
                    if( !( groups.length === 1 && group['sheets'].length === 1 ) ) {
                        new_snap
                            .append( close_sheet
                                        .click( function() {
                                            _store.remove_active_sheet();
                                            that.refresh_gui();
                                        })
                            )
                    }
                    new_snap.addClass('active');
                    $('#app-tb-tl-title').html( sheet_name );
                }
                $('#app-tb-sheets').append( new_snap );
            })
        });

        // TODO - finish this
        // 3 clear and get new tabs from _store
        //if( $('.snapshot').length == 10 ) {
        //    $('#save-snapshot' ).hide();
        //}

        // close all unnecessary tools
        //that.clear_app();
        // show some data finally
        _table.clean_table();
        _table.init_table();
    };


    that.make_zebra = function () {
        $('#app-tb-datatable')
            .find('tr:visible')
            .each( function ( i ) {
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
        var table = $('#app-tb-datatable');
        var a_root = table.find('tr[data-selected="true"]');
        var a_root_index = parseInt( a_root.attr('data-index'), 10 );
        // next a-level node
        var next = table.find('tr[data-index='+ (a_root_index + 1) +']');

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
            .addClass('dim');

        // make a-root background black
        table.find('tr.root').removeClass('root');
        a_root.addClass('root');

        // highlight the subtree
        _utils.with_subtree( a_root.attr('id'), function () {
            // uses 'this' instead of '$(this)' for fun.call reason
            this.removeClass( 'dim' );
        });

        // add the bottom border
        table.find('.next').removeClass('next');
        next.addClass('next');
    }


    that.show_table_tab = function() {
        hide_top_panels();
        $('#app-tbs-table').trigger( $.Event('click') );
    };


    return that;


// P R I V A T E   I N T E R F A C E

    function do_panels( button ) {
        // TODO refactor this - it's stupid!
        var creation_funcs = {
            choose: no_action,
            download: update_download_panel,
            search: no_action,
            more: no_action,
            english: no_action,
            feedback: no_action
        }

        var active = button.hasClass( 'active' );
        var action = button.attr('id').split('-').pop();
        var panel = $('#pl-' + action );

        if( active && $('#application').is(':hidden') ) {
            return;
        }

        $('#top')
            .find('.active')
            .removeClass( 'active' );

        if( !active ) {
            button.addClass( 'active' );
        }

        if( panel.is(':visible') ) {
            hide_top_panel( panel );
        }
        else if( !$('.panel:visible').length ) {
            creation_funcs[ action ]();
            show_top_panel( panel );
        }
        else {
            $('.panel:visible').slideUp( 400, function () {
                creation_funcs[ action ]();
                show_top_panel( panel );
            });
        }
    }

    function show_top_panel( panel ) {
        // show panel
        panel.slideDown( 400 );

        if( $('#application').is(':visible') ) {
            // dim the application
            $('#application')
                .animate({ opacity: 0.25 }, 300 );

            // show close panels bar
            $('#pl-close-bar')
                .show();
        }
    }


    function hide_top_panel( panel ) {
        // hide panel
        panel.slideUp( 400 );

        // undim the application
        $('#application')
            .animate({ opacity: 1 }, 300 );

        // hide close bar
        $('#pl-close-bar')
            .hide();
    }


    function hide_top_panels() {
        // deactivate menu positions
        $('#top')
            .find('.active')
            .removeClass('active');

        // close active panel
        $('.panel:visible')
            .slideUp( 400 );

        // undim the application
        $('#application')
            .animate({ opacity: 1 }, 300 );

        // hide close bar
        $('#pl-close-bar')
            .hide();
    }

    // update download panel with currently open sheets
    function update_download_panel() {
        var html = [];

        $('#pl-download').find('input:checked').removeAttr('checked');

        // if no sheets available yet, hide sheets download panel and quit
        if( !_store.active_group() ) {
            $('#pl-dl-sheets').hide();
            return;
        }
        $('#pl-dl-sheets').show();

        html.push( '<tbody>' );
        $('.sheet').each( function ( i, sheet ) {
            var id = $(this).attr('id').split('-');
            var group = id[1];
            var sheet = id[2];
            var name = $(this).attr('title');

            html.push( '<tr>' );
            // add (un)select all buttons
            if( i === 0 ) {
                html.push( '<td class="pl-dl-select-buttons" ' );
                html.push( 'rowspan="', $('.sheet').length, '">' );
                html.push( '<div id="pl-dl-sh-select" class="grey button">');
                html.push( 'Zaznacz wszystkie</div>' );
                html.push( '<br class="clear"/>' );
                html.push( '<div id="pl-dl-sh-unselect" class="grey button"> ');
                html.push( 'Odznacz wszystkie</div>' );
                html.push( '</td>' );
            }
            html.push( '<td class="check">' );
            html.push( '<input type="checkbox" ');
            html.push( 'value="', ( group + '-' + sheet ));
            html.push( '" /></td>' );
            html.push( '<td>', name, '</td>' );
            html.push( '</tr>' );
        });
        html.push( '</tbody>' );

        $('#pl-dl-sh-table')
            .empty()
            .append( $( html.join('') ));

        $('#pl-dl-sh-select').click( function () {
            // select all checkboxes
            $('#pl-dl-sh-table')
                .find(':checkbox')
                .attr( 'checked', 'true' );
        });

        $('#pl-dl-sh-unselect').click( function () {
            // unselect all checkboxes
            $('#pl-dl-sh-table')
                .find(':checkbox')
                .removeAttr( 'checked' );
        });
    }


    function no_action() {
        // left empty on purpose :)
    }


    function init_choose_panel() {
        var html = [];
        var datasets = _store.meta_datasets();
        var len = datasets.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );

        html.push( '<ul class="left">' );
        datasets.forEach( function ( set, i ) {

            html.push( '<li>' );
            html.push( '<header>' );
            html.push( '<h3>', set['name'], '</h3>' );
            html.push( '</header>' );
            html.push( '<section>' );
            html.push( '<p>', set['description'], '</p>' );
            html.push( '<div class="blue button right" ');
            html.push( 'data-set-id="', set['idef'], '">' );
            html.push( 'Zobacz dane</div>' );
            html.push( '</section>' );
            html.push( '</li>' );

            if( i === mid ) {
                html.push( '</ul><ul class="left">' );
            }
        });
        html.push( '</ul>' );

        $('#pl-ch-datasets')
            .append( $( html.join('') ))
            .find( '.button' )
            .click( function () {
                var dataset_id = $(this).attr( 'data-set-id' );

                create_views_panel( dataset_id );

                $('#pl-ch-datasets')
                    .hide();
            });
    };


    function create_views_panel( dataset_id ) {
        var html = [];
        var views = _store.meta_perspectives( dataset_id );
        var len = views.length;
        var mid = len % 2 === 0 ? Math.floor( len / 2 )-1 : Math.floor( len / 2 );
        var panel = $('#pl-choose');

        html.push( '<ul class="left">' );
        views.forEach( function ( view, i ) {
            html.push( '<li>' );
            html.push( '<header>' );
            html.push( '<h3>', view['name'], '</h3>' );
            html.push( '</header>' );
            html.push( '<section>' );
            html.push( '<p>', view['description'], '</p>' );

            view['issues']
                .reverse()
                .forEach( function ( issue ) {
                    html.push( '<div class="right blue button" ' );
                    html.push( 'data-set-id="', dataset_id, '" ' );
                    html.push( 'data-view-id="', view['idef'], '" ' );
                    html.push( 'data-issue="', issue, '">' );
                    html.push( issue );
                    html.push( '</div>' );
                });

            html.push( '<p class="right pl-ch-more">Zobacz dane: </p>' );
            html.push( '</section>' );
            html.push( '</li>' );

            if( i === mid ) {
                html.push( '</ul><ul class="left">' );
            }
        });
        html.push( '</ul>' );

        $('#pl-ch-views')
            .append( $( html.join('') ))
            .show()
            .find( '.button' )
            .click( function () {
                var button = $(this);
                var col_id = {
                    dataset: button.attr( 'data-set-id' ),
                    perspective: button.attr( 'data-view-id' ),
                    issue: button.attr( 'data-issue' )
                };

                // if new group is created, get data and show table
                if( _store.group_exists( col_id ) ) {
                    // get top-level data from db
                    _db.get_init_data( col_id );
                }
                else {
                    // go back to application with focus on requested sheet
                    hide_top_panels();
                }
            });

        panel
            .find('.panel-title')
            .html( _store.meta_datasets()[ dataset_id ]['name'] );
        panel
            .find('.panel-desc')
            .html('Wybierz jedno z wydań danych.');

        // show back icon
        $('.pl-ch-back > img')
            .show();
    };

    function update_share_tab() {
        var html = [];

        $('#app-sh-table').find('input:checked').removeAttr('checked');

        html.push( '<tbody>' );
        $('.sheet').each( function ( i, sheet ) {
            var id = $(this).attr('id').split('-');
            var group = id[1];
            var sheet = id[2];
            var name = $(this).attr('title');

            html.push( '<tr>' );
            // add (un)select all buttons
            if( i === 0 ) {
                html.push( '<td class="app-sh-select-buttons" ' );
                html.push( 'rowspan="', $('.sheet').length, '">' );
                html.push( '<div id="app-sh-select" class="rounded grey button">');
                html.push( 'Zaznacz wszystkie</div>' );
                html.push( '<br class="clear"/>' );
                html.push( '<div id="app-sh-unselect" class="rounded grey button"> ');
                html.push( 'Odznacz wszystkie</div>' );
                html.push( '</td>' );
            }
            html.push( '<td class="check">' );
            html.push( '<input type="checkbox" ');
            html.push( 'value="', ( group + '-' + sheet ));
            html.push( '" /></td>' );
            html.push( '<td>', name, '</td>' );
            html.push( '</tr>' );
        });
        html.push( '</tbody>' );

        $('#app-sh-table')
            .empty()
            .append( $( html.join('') ));

        $('#app-sh-select').click( function () {
            // select all checkboxes
            $('#app-sh-table')
                .find(':checkbox')
                .attr( 'checked', 'true' );
        });

        $('#app-sh-unselect').click( function () {
            // unselect all checkboxes
            $('#app-sh-table')
                .find(':checkbox')
                .removeAttr( 'checked' );
        });
    }
})();
