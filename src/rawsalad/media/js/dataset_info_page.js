(function () {
    $(".perspective").each( function() {
        var perspective = $(this);
        var icon = perspective.find(".perspective-icon");
        var label = perspective.find(".perspective-icon-label");
        var info = perspective.find(".perspective-info");
        var label_padding = label.css( "padding-top" ).replace('px', '') * 2;
        var label_height = label.height() + label_padding;
        var max_height = Math.max( label_height, info.height() ) + 10;

        perspective.height( max_height );
        icon.height( max_height - 6 );
        label.height( max_height );
        info.height( max_height );
    });
})();