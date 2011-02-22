(function () {
    var resp;
    
    $.each( [{ url: "/first/", complete: first_loaded }, 
	     { url: "/second/", complete: second_loaded }],
            function ( i, v ) {
                $.ajax( v );
            }
          );
    
    
    function first_loaded( response, status ) {
   	resp = JSON.parse( response.responseText );        
        create_table( "table-container-i" );
    }


    function second_loaded( response, status ) {
   	resp = JSON.parse( response.responseText );        
        create_table( "table-container-ii" );
    };
    

    function create_table( container_id ) {
	var resp_len = resp.length;
        var keys = get_keys( [resp[0]._id, resp[0].value] );
        var keys_len = keys.length;
	var table = [ "<table><thead><tr>" ];
	var inx = 0;
        var i, row, col, key, val;
        var container = $("#"+container_id);

        for( i = 0; i < keys_len; i += 1 ) {
            table[ ++inx ] = "<th>";
            table[ ++inx ] = keys[i].toUpperCase();
            table[ ++inx ] = "</th>";
        }
        table[ ++inx ] =  "</tr></thead><tbody>";

	for( row = 0; row < resp_len; row += 1 ) {
	    table[ ++inx ] = "<tr>";
            for( col = 0; col < keys_len; col += 1 ) {
                key = keys[ col ];
                val = resp[ row ]._id[ key ];

	        table[ ++inx ] = "<td>";
                if( val !== undefined ) {
	            table[ ++inx ] = val;
                }
                else {
                    table[ ++inx ] = resp[ row ].value[ key ];
                }
	        table[ ++inx ] = "</td>";
            }
	    table[ ++inx ] = "</tr>";
            
	}
	table[ ++inx ] =  "</tbody></table>";

	container.append( $(table.join("")) );
        container.find('table').dataTable(
            {
                "bAutoWidth": true,
                "bFilter": false,
                "bInfo": false,
                "bLengthChange": false,
                "bPaginate": false,
                "bProcessing": true,
            }
        );
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