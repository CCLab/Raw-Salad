(function () {
    
    $('#nav-01').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/navigation/02_01_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/navigation/02_01.png');
        }
    );

    $('#nav-03').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/navigation/02_03_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/navigation/02_03.png');
        }
    );


    $('#base-button').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/base_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/base.png');
        }
    );

    $('#download-button').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/download_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/download.png');
        }
    );

    $('#sessions-button').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/sessions_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/sessions.png');
        }
    );

    $('#snapshots-button').hover( 
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/snapshots_over.png');
        },
        function () {
            $(this).attr('src', '/site_media/media/img/buttons/snapshots.png');
        }
    );


    $('.angle-radio').click( function () {
        $('.angle-radio')
            .addClass('unselected')
            .removeClass('selected');
                    
        $(this)
            .addClass('selected')
            .removeClass('unselected');
    });

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
    $('#big-one').hide();
    $('#help-line-info').click( function () {
        $('#more-help').toggle();
        $('#big-one').toggle();
    });
    
})();
