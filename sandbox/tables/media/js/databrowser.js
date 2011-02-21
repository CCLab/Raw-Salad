(function () {
    $.each( [{ url: "/first/", complete: first_loaded }, 
	     { url: "/second/", complete: second_loaded }],
            function ( i, v ) {
                $.ajax( v );
            }
          );
    
    
    function first_loaded( response, status ) {
        create_table( response.responseText, "table-container-i" );
    }


    function second_loaded( response, status ) {
        create_table( response.responseText, "table-container-ii" );
    };
    

    function create_table( json_response, container_id ) {
   	var resp = JSON.parse( json_response );
	var resp_len = resp.length;
        var keys = get_keys( [resp[0]._id, resp[0].value] );
        var keys_len = keys.length;
	var table = [ "<table><thead>" ];
	var inx = 0;
        var i, row, col, key, val;
        var container = $("#"+container_id);

        for( i = 0; i < keys_len; i += 1 ) {
            if( keys[i] === 'kand_plec' ) {
                table[ ++inx ] = "<td class='plec'>";
            }
            else if( keys[i] === 'kand_szczebel' ) {
	        table[ ++inx ] = "<td class='szczebel'>";
            }
            else { 
                table[ ++inx ] = "<td>";
            }                
            table[ ++inx ] = keys[i].toUpperCase();
            table[ ++inx ] = "</td>";
        }
        table[ ++inx ] =  "</thead><tbody>";

	for( row = 0; row < resp_len; row += 1 ) {
	    table[ ++inx ] = "<tr>";
            for( col = 0; col < keys_len; col += 1 ) {
                key = keys[ col ];
                val = resp[ row ]._id[ key ];

                if( key === 'kand_plec' ) {
	            table[ ++inx ] = "<td class='plec'>";
                }
                else if( key === 'kand_szczebel' ) {
	            table[ ++inx ] = "<td class='szczebel'>";
                }
                else {
	            table[ ++inx ] = "<td>";
                }                
                
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

        container.find('table').remove();
	container.append( $(table.join("")) );
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