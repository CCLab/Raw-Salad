(function () {

    //  BUTTON I
    $('#i').click( function () {
	$.ajax({
	    url: "/button_i/",
	    type: "POST",
	    data: {},
	    complete: button_i_loaded
	});
    });
    
    function button_i_loaded( response, status ) {

	var table = "<table>",
	    json_object = JSON.parse( response.responseText );

	for( var i = 0; i < json_object.length; i += 1 ) {
	    table += '<tr><td>' + json_object[i]['id'] + '</td><td>' + json_object[i]['name'] + '</td></tr>';
	}
	table += '</table>';

	$("#table-container").append( $(table) )
	$('tr:even').css( 'background', '#ccc' );
    };


    //  BUTTON II
    $('#ii').click( function () {
	$.ajax({
	    url: "/button_ii/",
	    type: "POST",
	    data: {},
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
	    type: "POST",
	    data: {},
	    complete: button_iii_loaded
	});
    });
    
    function button_iii_loaded( response, status ) {
	alert( response.responseText );
    };
})();