(function () {
    $('#choose-collections').hide();
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
                $(this).attr( 'src', './collections_over.png' )
                    .css('cursor', 'pointer');                
            },
            function () {
                $(this).attr( 'src', './collections.png' );
            }
        )
        .click( function () {
            $('#choose-collection-name').html('Dostępne kolekcje');
            $('#info-text').html('Wybierz jedną z dostępnych w systemie kolekcji danych.');
            $('#choose-collections').toggle();            
            $('#choose-perspectives').toggle();
        });


    $('.position').hover( 
        function () {
            $(this).css('background-color', '#4abff7').css('cursor', 'pointer');
            $(this).find('.position-title').css('color', '#fff');
            $(this).find('.position-more').css('color', '#fff');
        },
        function () {
            $(this).css('background-color', '#fff');
            $(this).find('.position-title').css('color', '#009fe3');
            $(this).find('.position-more').css('color', '#009fe3');
        }
    );

    $('#choose-collections')
        .find('.position')
        .click( function () {
            $('#choose-collection-name').html('Budżet centralny');
            $('#info-text').html('Każda pozycja na liście udostępnia te same dane, lecz inaczej zorgranizowane.');
            $('#choose-collections').toggle();
            $('#choose-perspectives').toggle();                        
        });

    $('#choose-perspectives')
        .find('.position')
        .click( function () {
            $('#choose-panel').slideUp(400);
            $('#application').fadeIn(400).animate({ opacity: 1 }, 300 );
            $('#open-close-choose-panel').show().html('zmień dane');
        });
})();