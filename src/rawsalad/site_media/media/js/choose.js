(function () {
 
    $('.radio-button').click( function () {
        var nav_plain = '/site_media/media/img/navigation/01_02.png';
        var nav_active = '/site_media/media/img/navigation/01_02_active.png';
        var nav_over = '/site_media/media/img/navigation/01_02_over.png';

        var nav_img = $('#nav-02');                    
        var nav_current = nav_img.attr('src');

        if( nav_current === nav_plain )
        {
            nav_img.attr('src', nav_active )
                   .hover( 
                       function () {
                           nav_img.attr('src', nav_over ); 
                           nav_img.css('cursor', 'pointer');
                           $('#nav-02-anchor').attr('href', '/browse/');
                       },                     
                       function () {
                           nav_img.attr('src', nav_active );                            
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
    $('#help-line, #help-button').click( function () {
        $('#more-help').toggle();

        if( $('body').css('background-position') === '0% 0%' )
            $('body').css('background-position', '0px '+(10+$('#more-help').height())+'px' );
        else
            $('body').css('background-position', '0% 0%' );        
    });
    
})();
