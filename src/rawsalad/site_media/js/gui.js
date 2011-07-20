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
        $('#table-tab').click( function () {
            $('#table-container').show();
            $('#search-container').hide();
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

        $('#permalink-tab').click( function () {
            $('#table-container').hide();
            $('#search-container').hide();
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

        $('#download-button').click( function () {
            var ids = {};
            var table = $('#download-table');
            var checkboxes = table.find('input:checkbox:checked');

            checkboxes.each( function () {
                var box = $(this);
                var box_id = box.attr('id');
                var group = box_id.split('-')[0];
                var sheet = box_id.split('-')[1];
                var scope = table
                                .find('input:radio[name=scope-'+box_id+']:checked')
                                .val();

                if( !ids[group] ) {
                    ids[group] = [];
                }

                ids[group].push({
                    id: sheet,
                    scope: scope
                });
            });

            _download.selected( ids );
        });

        _tools.prepare_tools();

        // arm open/close button and hide it!
        $('#open-close-choose-panel')
            .click( hide_top_panels );

        $('#download-panel').hide();
        $('#top-menu')
            .find('div')
            .click( function () {
                do_panels( $(this) );
            });


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
                $('#info-info')
                    .html('');
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
            });

        init_choose_panel();
    };


    // used once when some perspective is chosen for the very first time
    that.init_app = function ( collection_name ) {

        if( arguments.length !== 0 ){
            _store.set_active_sheet_name( collection_name );        
        }        
        that.refresh_gui();        
                
//        that.create_sheet_tab({
//            // TODO move name from func arg to store!!
//            name: collection_name,
//            group_nr: _store.active_group_index(),
//            sheet_nr: _store.active_sheet_index()
//        });

        $('#application').show();
        that.make_zebra();
        hide_top_panels();
    }

// TODO remove this:
//    that.create_sheet_tab = function ( args ) {
//        that.create_only_sheet_tab( args );
//        _table.clean_table();
//        _table.init_table();
//    };


    that.refresh_gui = function () {   
        var groups = _store.get_all_groups();
//        var all_snapshots = [];
        var close_sheet;
        var active_group = _store.active_group_index();
        var active_sheet = _store.active_sheet_index();
        // 1  clear gui, 
        $('.snapshot').remove();        
        // 2 create new gui
        groups.forEach( function ( group, group_num ){
            var sheets = _store.get_sheets( group_num );
            sheets.forEach( function (sheet, sheet_num){
                var  sheet_name = sheet['name'];
                var html = [];
                var new_snap;
                html.push( '<div ' );
                html.push( 'id="snap-' + group_num + '-' + sheet_num + '" ' );
                html.push( 'class="snapshot" ' );
                html.push( 'title="', sheet_name, '">' );
                html.push( sheet_name.length > 20 ?
                    sheet_name.slice( 0, 17 ) + '...' :
                    sheet_name );
                html.push( '</div>' );

                new_snap = $( html.join('') );
                new_snap
                    .click( function () {
                        _store.active_group( group_num );//
                        _store.active_sheet( sheet_num );//
                        that.refresh_gui();                    
                    });
                    
                if ( ( group_num === active_group ) && ( sheet_num === active_sheet ) ) {      
                    close_sheet = $( '<div class="close-sheet-button" >x</div>' );
                    if ( !(groups.length == 1 && sheets.length == 1) ){
                        new_snap
                            .append(close_sheet
                                .click( function(){
                                    _store.remove_active_sheet();
                                    that.refresh_gui();
                                })
                           )
                           .addClass( 'active' );
                    }else{
                        new_snap.addClass( 'active' );
                    }
                }
//                all_snapshots.append();  
                $('#snapshots').append( new_snap );
            })                
        });           
        // TODO - finish this
        // 3 clear and get new tabs from _store
        if( $('.snapshot').length == 10 ) {
            $('#save-snapshot' ).hide();
        }

         $('#sort-form').hide().html('');
         $('#filter-form').hide().html('');
        _table.clean_table();     
        _table.init_table();
    };

// TODO remove this:
//    that.create_only_sheet_tab = function ( args ) {
//        var html = [];

//        var group_nr = args.group_nr || _store.active_group_index();
//        var sheet_nr = args.sheet_nr || _store.active_sheet_index();
//        var sheet_name = args.name || "Arkusz " + group_nr + '-' + sheet_nr;

//        var group_changed = _store.active_group_index() !== group_nr;
//        var sheet_changed = _store.active_sheet_index() !== sheet_nr;
//        var new_tab;
//        var close_sheet;


//        to refresh_gui 
//        html.push( '<div id="snap-' + group_nr + '-' + sheet_nr + '" ' );
//        html.push( 'class="snapshot" ' );
//        html.push( 'title="', sheet_name, '">' );
//        html.push( sheet_name.length > 20 ?
//                   sheet_name.slice( 0, 17 ) + '...' :
//                   sheet_name );
//        html.push( '</div>' );

//        new_tab = $( html.join('') );

//        close_sheet = $( '<div class="close-sheet-button" >x</div>' );

//        $('.snapshot').removeClass('active');
//        $('.close-sheet-button').remove();
//        
//        new_tab
//            .append(close_sheet
//                .click( function(){
//                    _store.remove_active_sheet();
//                    alert("Sheet dleyted");
//                    
//                    _table.clean_table();
//                    _table.init_table();
//                })             
//            )
//            .addClass( 'active' )
//            .click( function () {
//                var id_elements = $(this).attr('id').split('-');
//                var group_nr = id_elements[1];
//                var sheet_nr = id_elements[2];

//                $('.snapshot').removeClass('active');
//                $('.close-sheet-button').remove();
//                $(this).addClass('active')
//                    .append(close_sheet.click( function(){
//                        _store.remove_active_sheet();
//                        alert("Sheet dleyted");
//                        _table.clean_table();
//                        _table.init_table();
//                    })
//                )

//                _store.active_group( group_nr );
//                _store.active_sheet( sheet_nr );

//                $('#sort-form').hide().html('');
//                $('#filter-form').hide().html('');
//                
//                
//                _table.clean_table();
//                _table.init_table();
//            });

 //       $('.close-sheet-button').click( function(){
 //           _store.remove_active_sheet();
 //           allert("Sheet dleyted");
            // add reload        
 //       });


//        if( sheet_nr === 0 ) {
//            $('#snapshots').append( new_tab );
//        }
//        else {
//            new_tab.insertAfter( '#snap-'+group_nr+'-'+(sheet_nr-1));
//        }

//        if( $('.snapshot').length == 10 ) {
//            $('#save-snapshot' ).hide();
//        }

//        _store.active_sheet( sheet_nr );
//        _store.active_group( group_nr );

//        $('#sort-form').hide().html('');
//        $('#filter-form').hide().html('');
//    };


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
    }

    that.show_table_tab = function() {
        $('#table-container').show();
        $('#search-container').hide();
        $('#download-container').hide();
        $('#permalink-container').hide();

        $('#tabs')
            .find('div')
            .removeClass('active')
            .addClass('inactive');

        $('#table-tab')
            .addClass('active')
            .removeClass('inactive');
    };


    return that;


// P R I V A T E   I N T E R F A C E



    function create_download_panel() {
        var html = [];
        if( !_store.active_group() ) {
            $('#sheets-download').hide();
            return;
        }

        $('#sheets-download').show();
        $('.snapshot').each( function () {
            var id = $(this).attr('id').split('-');
            var group = id[1];
            var sheet = id[2];
            var name = $(this).attr('title');

            html.push( '<tr>' );
            html.push( '<td class="check">' );
            html.push( '<input type="checkbox" ');
            html.push( 'id="', ( group + '-' + sheet ));
            html.push( '" /></td>' );
            html.push( '<td class="radio">' );
            html.push( '<input type="radio" name="scope-', group, '-', sheet );
            html.push( '" value="sheet" checked />' )
            html.push( '</td>' );
            html.push( '<td class="space"></td>' );
            html.push( '<td class="radio">' );
            if( sheet === '0' ) {
                html.push( '<input type="radio" name="scope-', group, '-', sheet );
                html.push( '" value="full" />' )
                html.push( '</td>' );
                html.push( '<td class="name group">' );
                html.push( name );
            }
            else {
                html.push( '</td>' );
                html.push( '<td class="name indent">' );
                html.push( ' > ' + name );
            }
            html.push( '</td>' );
            html.push( '</tr>' );
        });
        $('#download-table > tbody').empty().append( html.join('') );

        $('#download-table .radio > input').hide();
        $('#download-table .check > input' ).change( function () {
            if( $(this).attr('id').split('-')[1] === '0' ) {
                if( $(this).attr('checked') ) {
                    $(this).parent().parent().find('.radio > input').show();
                }
                else {
                    $(this).parent().parent().find('.radio > input').hide();
                }
            }
        });

        $('#download-select-all').click( function () {
            $('#download-table').find(':checkbox').not(':checked' ).trigger( $.Event('click') );
        });

        $('#download-unselect-all').click( function () {
            $('#download-table').find(':checkbox:checked' ).trigger( $.Event('click') );
        });
    }

    function create_search_panel () {
    }

    function do_panels( button ) {
        var creation_funcs = {
            choose: function () {},
            download: create_download_panel,
            search: create_search_panel
        }

        var active = button.hasClass( 'active' );
        var action = button.attr('id').split('-').pop();
        var panel = $('#'+ action +'-panel');

        if( active && $('#application').is(':hidden') ) {
            return;
        }

        $('#top-menu')
            .find('.active')
            .removeClass( 'active' );

        if( !active ) {
            button.addClass( 'active' );
        }

        if( panel.is(':visible') ) {
            hide_top_panel( panel );
        }
        else if( !$('#top-panels > div:visible').length ) {
            creation_funcs[ action ]();
            show_top_panel( panel );
        }
        else {
            $('#top-panels > div:visible').slideUp( 400, function () {
                creation_funcs[ action ]();
                show_top_panel( panel );
            });
        }
    }

    function show_top_panel( panel ) {
        panel.slideDown( 400 );

        $('#application')
            .animate({ opacity: 0.25 }, 300 );

        if( $('#application').is(':visible') ) {
            $('#open-close-choose-panel')
                .show();
        }
    }


    function hide_top_panel( panel ) {
        panel.slideUp( 400 );

        $('#application')
            .animate({ opacity: 1 }, 300 );

        $('#open-close-choose-panel')
            .hide();
    }

    function hide_top_panels() {
        $('#top-menu')
            .find('.selected')
            .removeClass('selected');

        $('#top-panels > div:visible')
            .slideUp( 400 );

        $('#application')
            .animate({ opacity: 1 }, 300 );

        $('#open-close-choose-panel')
            .hide();
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

        $('#info-info')
            .html( 'Wybrano kolekcję: ' );

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
                if( _store.group_exists( col_id ) ) {
                    // get top-level data from db
                    _db.get_init_data( col_id );
                }
                else {
                    // go back to application with focus on requested sheet
                    hide_top_panels();
                }
            });
    };
   
})();
