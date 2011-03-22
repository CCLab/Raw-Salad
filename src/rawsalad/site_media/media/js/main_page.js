(function () {

    $('#knowladge-base-full').hide();
    $('#help-full').hide();
    $('#restore_session').hide();

    $('#knowladge-base').click( function () {
        $(this).hide();
        $('#knowladge-base-full').show();
    });

    $('#help').click( function () {
        $(this).hide();
        $('#help-full').show();
    });

    $('#saved_sessions').mouseover( function () {
            $('#restore_session').show();            
    });
    
    $('#restore_session').mouseover( function () {
            $('#restore_session').show();            
    });
    
    $('#restore_session').mouseout( function () {
            $(this).hide();            
    });
})();
