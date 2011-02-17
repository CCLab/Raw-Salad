from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.utils import simplejson as json


def main_page( request ):
    return render_to_response( "databrowser.html" )

def button_i( request ):
    data = [{ "id": 1, "name": "Janek" },
            { "id": 2, "name": "Staszek" },
            { "id": 3, "name": "Hanka" }]

    return HttpResponse( json.dumps( data ));

def button_ii( request ):
    return HttpResponse( "Working II" );

def button_iii( request ):
    return HttpResponse( "Working III" );
