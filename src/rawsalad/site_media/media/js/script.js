(function () {
    $('#choose-perspectives').hide();
    $('#application').hide();

    $('#open-close-choose-panel')
        .hide()
        .click( function () {
            if( $('#open-close-choose-panel').html() === 'zmień dane') {
                $('#application').animate({ opacity: 0.25 }, 300 );
            }
            else {
                $('#application').animate({ opacity: 1 }, 300 );
            }

            $('#choose-panel').slideToggle( 300, function () {
                if( $('#choose-panel:visible').length > 0 ) {
                    $('#open-close-choose-panel').html('zwiń');
                }
                else {
                    $('#open-close-choose-panel').html('zmień dane');
                }
            });
        });

    $('#back-to-collections')
        .hover(
            function () {
                $(this).attr( 'src', '/site_media/media/img/collections_over.png' )
                    .css('cursor', 'pointer');                
            },
            function () {
                $(this).attr( 'src', '/site_media/media/img/collections.png' );
            }
        )
        .click( function () {
            $('#choose-collection-name').html('Dostępne kolekcje');
            $('#info-text').html('Wybierz jedną z dostępnych w systemie kolekcji danych.');
            $('#choose-collections').toggle();            
            $('#choose-perspectives').toggle();
            $('#choose-perspectives-list').html('');
        });

})();
