from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.utils import simplejson as json
from simple_main.settings import MEDIA_URL

def main_page( request ):
    data = { 'MEDIA_URL': MEDIA_URL }
    template = loader.get_template( "index.html" )
    context = Context( data )
    return HttpResponse( template.render( context ) )
	
def choose_view( request ):
    data = { 'MEDIA_URL': MEDIA_URL }
    template = loader.get_template( "budget.html" )
    context = Context( data )
    return HttpResponse( template.render( context ) )

