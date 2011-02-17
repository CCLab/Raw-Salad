from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json
from urllib import urlopen
# to be replaced with Denis' db interface
import pymongo 

json_data = '[{"id": 1, "name": "Janek"},{"id": 2, "name": "Janek"},{"id": 3, "name": "Janek"}]'

def main_page( request ):
    template = loader.get_template( "databrowser.html" )
    context = Context({ })
    return HttpResponse( template.render( context ))

def button_i( request ):
    data = json_data
    return HttpResponse( data );

def button_ii( request ):
    return HttpResponse( "Working II" );

def button_iii( request ):
    return HttpResponse( "Working III" );
