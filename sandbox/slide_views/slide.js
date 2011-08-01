(function () {
    var datasets_height = $("#pl-ch-datasets").height(); 
    var views_height =$("#pl-ch-views").height();
    
    if ( views_height > datasets_height ){
        $("#pl-ch-views").height( datasets_height );
    }
    
    
    $("#pl-ch-get-views-button").click(function (){


    
        $("#pl-ch-area").animate( {"left": "-=960px"}, 800, function(){
        
            if ( datasets_height > views_height ){
                    
                   $("#pl-ch-datasets").animate ( {"height": "" + views_height + "px"}, 200 );
                   
            }else if ( views_height > datasets_height ){
            
                   $("#pl-ch-views").animate ( {"height": ""+ views_height +"px"}, 200 );
            }


        
        });
        
                   
    });
    
    $("#pl-ch-get-datasets-button").click(function (){
    
        $("#pl-ch-area").animate( {"left": "+=960px"}, 800, function(){
            var views_height = $("#pl-ch-views").height();
            //var datasets_height = $("#pl-ch-datasets").height(); 
            if ( datasets_height > views_height ){
//                   $("#pl-ch-datasets").height( datasets_height );
                   $("#pl-ch-datasets").animate ( {"height": "" + datasets_height + "px"}, 200 );            
            }else if ( views_height > datasets_height ){
                   $("#pl-ch-views").animate ( {"height": "" + datasets_height + "px"}, 200 );
            }            
        });
    })
})();
