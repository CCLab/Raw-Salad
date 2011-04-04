(function () {
 
    $('.radio-button').click( function () {
        var navigation_img = $('#nav-02').attr('src');
        if( navigation_img === '/site_media/media/img/navigation/01_02.png' )
        {
            $('#nav-02').attr('src', '/site_media/media/img/navigation/01_02_active.png' )
                        .hover( 
                            function () {
                                $('#nav-02').attr('src', '/site_media/media/img/navigation/01_02_over.png' ); 
                                $('#nav-02').css('cursor', 'pointer');
                            },                     
                            function () {
                                $('#nav-02').attr('src', '/site_media/media/img/navigation/01_02_active.png' );                            
                            });
            
        }
        
        $('.radio-inside')
            .addClass('unselected')
            .removeClass('selected');
                    
        $(this).find('.radio-inside')
            .addClass('selected')
            .removeClass('unselected');
    });
    
    $('#selected-items').hide();    

    $('#collection-list').hide();
    
    $('#change-dataset').click( function () {
            $('#collection-list').show();            
    });
    
    $('#collection-list').mouseover( function () {
            $('#collection-list').show();            
    });
    
    $('#collection-list').mouseout( function () {
            $(this).hide();            
    });
    
    $('#more-help').hide();
    $('#big-one').hide();
    $('#help-line').click( function () {
        $('#more-help').toggle();

        if( $('body').css('background-position') === '0% 0%' )
            $('body').css('background-position', '0px '+(10+$('#more-help').height())+'px' );
        else
            $('body').css('background-position', '0% 0%' );        
    });
    $('#help-button').click( function () {
        $('#more-help').toggle();
    });

    
})();
