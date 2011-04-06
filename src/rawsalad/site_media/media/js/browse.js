(function () {

    var nav_01 = $('#nav-01');

    nav_01.hover( 
        function () {
           nav_01.attr('src', '/site_media/media/img/navigation/02_01_over.png' ); 
        },                     
        function () {
           nav_01.attr('src', '/site_media/media/img/navigation/02_01.png' );
        });

    $('#selected-items').hide();  
    $('#selected-items-list').hide();        
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
    
    $('#selected-items-list').mouseover( function () {
        $('#selected-items-list').show();            
    });
    $('#selected-items-list').mouseout( function () {
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
