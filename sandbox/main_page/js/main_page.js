(function () {
    $('.accordeon').hide();
    $('.expert_blog').hide();    
    $('.dataset-name').click( function () {
        $(this).next().toggle();
        $(this).parent().next().toggle();
        $(this).parent().parent().siblings().find('.accordeon').hide();
        $(this).parent().parent().siblings().find('.expert_blog').hide();        
    });
})();
