(function () {

    //  BUTTON I
    $('#i').click( function () {
	$.ajax({
	    url: "/button_i/",
	    complete: button_i_loaded
	});
    });
    
    function button_i_loaded( response, status ) {
        create_table( response.responseText, "table-container-i" );
    }

    //  BUTTON II
    $('#ii').click( function () {
	$.ajax({
	    url: "/button_ii/",
	    complete: button_ii_loaded
	});
    });
    
    function button_ii_loaded( response, status ) {
        create_table( response.responseText, "table-container-ii" );
    };


    //  BUTTON III
    $('#iii').click( function () {
	$.ajax({
	    url: "/button_iii/",
	    complete: button_iii_loaded
	});
    });
    
    function button_iii_loaded( response, status ) {
    };


    //  CLEAR VIEW BUTTON
    $('#clear').click( function() {
        $('table').remove();
    });

    function create_table( json_response, container_id ) {
   	var resp = JSON.parse( json_response );
	var resp_len = resp.length;
        var keys = get_keys( [resp[0]._id, resp[0].value] );
        var keys_len = keys.length;
	var table = [ "<table><thead><td class='index'>No.</td>" ];
	var inx = 0;
        var i, row, col, key;
        var container = $("#"+container_id);

        for( i = 0; i < keys_len; i += 1 ) {
            table[ ++inx ] = "<td>";
            table[ ++inx ] = keys[i].toUpperCase();
            table[ ++inx ] = "</td>";
        }
        table[ ++inx ] =  "</thead>";

	for( row = 0; row < resp_len; row += 1 ) {
	    table[ ++inx ] = "<tr><td class='index'>";
	    table[ ++inx ] = row + 1;
	    table[ ++inx ] = "</td>";

            for( col = 0; col < keys_len; col += 1 ) {
                key = keys[ col ];
	        table[ ++inx ] = "<td>";
                if( resp[ row ]._id[ key ] !== undefined ) {
	            table[ ++inx ] = resp[ row ]._id[ key ];
                }
                else {
                    table[ ++inx ] = resp[ row ].value[ key ];
                }
	        table[ ++inx ] = "</td>";
            }
	    table[ ++inx ] = "</tr>";
            
	}
	table[ ++inx ] =  "</table>";

        container.find('table').remove();
	container.append( $(table.join("")) ).find("tr:even").css( "background", "#ccc" );
    };


    function get_keys( list ) {
        var l = [];
        for( var i = 0; i < list.length; i += 1 ) {
            for( var key in list[i] ) {
                l.push( key );
            }
        }
        return l;
    }
})();