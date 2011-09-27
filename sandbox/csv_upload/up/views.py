from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render_to_response
from csv_upload.up.forms import *

def home( req ):
    f = FirstStepForm()

    return render_to_response( 'home.html', { 'form': f } )


@csrf_exempt
def upload( req ):
    # treat form as a multipart one
    form = FirstStepForm( req.POST, req.FILES )
    # server-side validation (to be changed to client-side on deploy)
    if not form.is_valid():
        return render_to_response( 'home.html', { 'form': form } )

    tmp_name = 'tmp/' + req.POST['abbr'] + '.csv'
    tmp_file = open( tmp_name, 'w' )
    upl_file = req.FILES.get( 'file', '' )

    for chunk in upl_file.chunks():
        tmp_file.write( chunk );
    tmp_file.close()

    upl_file.seek( 0 )
    # do the csv processing as upl_file inherits from a File class
    # and though you can treat it as a normal CSV file

    return render_to_response( 'wait.html', { 'file_name': upl_file.name } )
