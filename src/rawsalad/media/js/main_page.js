(function () {

    $('#blog-extra').hide();

    $('#collections-list').hover(
        function () {
            $('#head-img').attr('src', '/media/img/head_1.png');
        },
        function () {
            $('#head-img').attr('src', '/media/img/head_0.png');
        }
    );

    $('#more').click( function () {
        $(this).css('color', '#fff');
        $('#blog-extra').slideDown( 500 );
    });
 
    $('#less').click( function () {
        $('#blog-extra').slideUp( 500, function () {
            $('#more').css('color', '#333');
        });
    });     

})();
