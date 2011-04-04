(function () {
 
    $('.radio-button').click( function () {
        $('.radio-inside')
            .addClass('unselected')
            .removeClass('selected');
                    
        $(this).find('.radio-inside')
            .addClass('selected')
            .removeClass('unselected');
    });

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
        $('#big-one').toggle();
    });
    $('#help-button').click( function () {
        $('#more-help').toggle();
        $('#big-one').toggle();
    });

    
})();
