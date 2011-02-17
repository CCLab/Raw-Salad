(function () {

    //  BUTTON I
    $('#i').click( function () {
	$.ajax({
	    url: "/button_i/",
	    complete: button_i_loaded
	});
    });
    
    function button_i_loaded( response, status ) {

   	var resp = JSON.parse( response.responseText );
	var resp_len = resp.length;
	var table = [ "<table>" ];
	var inx = 0;

	for( var i = 0; i < resp_len; i += 1 ) {
	    table[ ++inx ] = "<tr><td>";
	    table[ ++inx ] = resp[i]["id"];
	    table[ ++inx ] = "</td><td>";
	    table[ ++inx ] = resp[i]["name"];
	    table[ ++inx ] = "</td></tr>";
	}
	table[ ++inx ] =  "</table>";

	$("#table-container").append( $(table.join("")) )
	$("tr:even").css( "background", "#ccc" );
    };


    //  BUTTON II
    $('#ii').click( function () {
	$.ajax({
	    url: "/button_ii/",
	    complete: button_ii_loaded
	});
    });
    
    function button_ii_loaded( response, status ) {
	alert( response.responseText );
    };


    //  BUTTON III
    $('#iii').click( function () {
	$.ajax({
	    url: "/button_iii/",
	    complete: button_iii_loaded
	});
    });
    
    function button_iii_loaded( response, status ) {
	alert( response.responseText );
    };
})();