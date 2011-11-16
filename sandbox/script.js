$('#pl-sr-more')
.click( function () {
    if( $('#pl-sr-full').is(':visible') ) {
        $('#pl-sr-full').slideUp( 200 );
        $(this).html( 'Pokaż zaawansowane' );
    }else {
        $('#pl-sr-unselect').trigger( $.Event( 'click' ));
        $('#pl-sr-full').slideDown( 200 );
        $(this).html( 'Zamknij zaawansowane' );
    }
});
$('.search-arrow')
.click( show_search_collection );

$('#pl-sr-full > ul > li > input').change( function(){
    if ( $(this).is( ':checked' ) ){
        $(this).next().find( ':checkbox' )
        .prop( 'checked', true );
    }
    else{
        $(this).next().find( ':checkbox' )
        .prop( 'checked', false );    
    }
});


function show_search_collection(){   
	$(this).parent('.pl-sr-fl-det').addClass('col-details');
	$(this).parent('.pl-sr-fl-deepdet').addClass('col-deepdet');
	$(this).prev().show();
	$(this).siblings('.pl-sr-fl-col-det').css({ display: "inline-block" });
	$(this).attr('src', 'img/triangle-down.png' );	
	$(this).unbind()
	.click( hide_search_collection );
}

function hide_search_collection(){
	$(this).parent('.pl-sr-fl-det').removeClass('col-details');
	$(this).parent('.pl-sr-fl-deepdet').removeClass('col-deepdet');

	$(this).prev().hide();
	$(this).siblings('.pl-sr-fl-col-det').css({ display: 'none' });
	$(this).attr('src', 'img/triangle.png' );
	$(this)
	.click( show_search_collection );	
}
