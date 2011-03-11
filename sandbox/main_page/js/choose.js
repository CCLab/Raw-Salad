(function () {
    
    $('#navigation-img').hover( 
        function () {
            $(this).attr('src', './img/choose/navigation_01_over.png');
        },
        function () {
            $(this).attr('src', './img/choose/navigation_01.png');        
        }
    );

    $('#collection-list').hide();
    
    $('#collection-change').click( function () {
            $('#collection-list').show();            
    });
    
    
    $('#collection-list').mouseover( function () {
            $('#collection-list').show();            
    });
    
    $('#collection-list').mouseout( function () {
            $(this).hide();            
    });
    
    $('#more-help').hide();
    $('#help-line-info').click( function () {
        $('#more-help').toggle();
    });
    
})();
