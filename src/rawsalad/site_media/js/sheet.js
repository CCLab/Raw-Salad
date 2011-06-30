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

var _sheet = (function () {

    //  P U B L I C   I N T E R F A C E
    var that = {};

    that.create_new_sheet = function ( sheet_data, sheet_name, filtered_sheet ) {
        var group_nr = _store.active_group_index();
        var sheet_nr = _store.next_sheet_number();
        var new_sheet = {};

        $.extend( true, new_sheet, sheet_data );
        new_sheet["name"] = sheet_name + ' ' + sheet_nr;

        _store.add_new_sheet( new_sheet );
        _gui.create_sheet_tab({
            'name': new_sheet['name'],
            'sheet_nr': sheet_nr,
            'group_nr': group_nr,
            'filtered_sheet': filtered_sheet
        });
    }

    return that;

// P R I V A T E  I N T E R F A C E
    var clean_basic_sheet = function () {
        var active_sheet_number;
        var basic_sheet;
        var basic_sheet_rows = [];

        active_sheet_number = _store.active_sheet_index();

        ////TODO : can't get basic_sheet
        //basic_sheet = _store.basic_sheet();
        //$.extend( true, basic_sheet_rows, basic_sheet['rows'] );

        _store.active_sheet_index(0);
        _store.acitve_sheet_rows( basic_sheet_rows );
        _store.active_basic_changed( false );

        _store.active_sheet_index( active_sheet_number );
    };

}) ();
