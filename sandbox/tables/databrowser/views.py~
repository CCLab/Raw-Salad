from django.http import HttpResponse
from django.template import Context, loader
from django.utils import simplejson as json

# to be replaced with Denis' db interface
import pymongo 

def main_page( request ):
    template = loader.get_template( "databrowser.html" )
    context = Context({ 'text': 'Working!' })
    return HttpResponse( template.render( context ))

