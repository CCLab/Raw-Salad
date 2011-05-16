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

    var offset = $('#choose-main-panel').height() / 2 - 28;

    $('#back-to-collections')
        .css( 'margin-top', offset+'px' )
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

            

    $('#snap-1').hide();
    $('#snap-2').hide();
    $('#save-snapshot').click( function () {
        if( $('#snap-1:hidden').length > 0 ) {
            $('#snap-1').show();
        }
        else {
            $('#snap-2').show();
        }
    });
})();
