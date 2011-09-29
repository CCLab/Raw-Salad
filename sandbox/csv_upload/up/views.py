# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from csv_upload.up.forms import *

from csv import DictReader
import re
import simplejson as json

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

    # actual csv processing goes here
    meta_data_draft= {
        'dataset': 99, # to obtain from db or to increment
        'idef': 99, # to obtain from db or to increment in scope of dataset
        'issue': req.POST.get( 'issue', 'issX' ),
        'name': req.POST.get( 'abbr', 'xxxx' ),
        'perspective': req.POST.get( 'desc', '' ),
        'ns': None,
        'explorable': '',
        'max_level': ''
        }
    delim = str( req.POST.get( 'delim', ';' ) )

    columns= process_csv( upl_file, delim )
    meta_data_draft.update( { 'columns': columns } )

    return render_to_response( 'wait.html', { 'file_name': upl_file.name, 'data': meta_data_draft } )


@csrf_exempt
def save_metadata( req ):
    print json.loads( req.POST.get( 'metadata', [] ) )

    return HttpResponseRedirect( '/' )


def process_csv( src_file, delim ):
    """
    process user uploaded CSV file
    and create a proposed meta-data dict
    """

    csv_delim= delim
    csv_quote= '"'

    csv_dict= DictReader(src_file, skipinitialspace= True, delimiter= csv_delim, quotechar= csv_quote)

    columns_list= fill_column_names( csv_dict.fieldnames )
    columns_list= fill_column_types( columns_list, csv_dict )

    return columns_list

def fill_column_types(columns, csvdict):
    out= columns[:]

    for row in csvdict.reader: # checking rows to guess types
        i= 0 # field index   # !!! WARNING !!! don't miss restval param of DictReader! (number of values if bigger than in the header)
        for clm in csvdict.fieldnames:
            if len(str(row[i])) > 0: # not enough for analysis
                currval= replace_locale_symbols( row[i].strip() )
                if not re.match(r'^[-+]?[0-9\,]*\.?[0-9]+([eE][-+]?[0-9]+)?$', currval): # this id NOT float or int
                    new_type= 'string'
                else: # float or int
                    # checking different formats
                    comma_sepr_whole= currval.split(',')
                    space_sepr_whole= currval.split(' ')
                    if len(comma_sepr_whole) > 1:
                        if len(comma_sepr_whole) == 2: # #####0,00
                            if '.' in comma_sepr_whole[-1]: # situation 156,150.77 -> [156, 150.77]
                                currval= currval.replace(',', '')
                            else: # situation 156,15 -> [156, 15]
                                currval= currval.replace(',', '.')
                        else: # ###,##0.00 or ###,##0
                            currval= currval.replace(',', '')
                    elif len(space_sepr_whole) > 1: # ### ##0.00 or # ### ##0
                        currval= currval.replace(' ', '')

                    new_type= check_type(currval)

                out[i]['type_tmp']= new_type
                if new_type == 'float':
                    new_prec= len(str(row[i]).split(".")[-1])
                    try:
                        cur_prec= columns[i]['type_precision']
                    except:
                        cur_prec= 0
                    out[i]['type_precision']= max( new_prec, cur_prec )
            i += 1

    for out_doc in out:
        if out_doc['type_tmp'] in ['int', 'float']:

            # filling type
            out_doc['type']= 'number'
            out_doc['checkable']= True
            out_doc['format']= '# ##0'

            # filling format
            if 'type_precision' in out_doc:
                if out_doc['type_precision'] > 0:
                    out_doc['format'] += '.'
                    j= 0
                    while j < out_doc['type_precision']:
                        j += 1
                        out_doc['format'] += '0'

                    no_red_format= out_doc['format']
                    out_doc['format'] += ';[RED]-' + no_red_format

                del out_doc['type_precision']

        del out_doc['type_tmp']

    return out

def check_type(val):
    try:
        val= float(val)
        tp= 'float'
        if val.is_integer():
            tp= 'int'
    except:
        tp= 'string'

    return tp


def fill_column_names(field_names):
    """
    cleaning the header:
    - everything to lowercase
    - empty column name -> column_N (N is a number)
    - delete dots (.) in the end of a name
    - \n, /, \, +, -, *, ' ', etc. -> _
    - [ą, ć, ę, ł, ń, ó, ś, ź, ż, Ą, Ć, Ę, Ł, Ń, Ó, Ś, Ź, Ż] ->
      [a, c, e, l, n, o, s, z, z, A, C, E, L, N, O, S, Z, Z]
    """

    basic_keywords= ['id', 'idef', 'numer', 'number', 'typ', 'type', 'name', 'nazwa', 'total', 'ogolem']

    out= []
    i= 0

    for field in field_names:
        i += 1
        label= field.strip().replace('\n', ' ')
        if len(label) == 0: # field with no name
            label= 'Pole %s' % i
        key= re.sub(r'[\W\s]+', '_', replace_locale_symbols(label.lower()), re.U)
        key= re.sub(r'_$', '', key)

        basic, processable= False, True
        # WARNING! should actually be sthn like: if ['id', 'idef', 'typ', 'type', 'name', 'nazwa', 'total', 'ogolem'] in key:
        for kw in basic_keywords:
            if kw in key:
                basic= True
                break

        out.append({
            'label': label,
            'key': key,
            'type': 'string', # will be updated later
            'format': r'@', # text as default, but will be updated later
            'basic': basic,
            'processable': processable,
            'checkable': False # will turn True, if it is a number
            })

    return out


def replace_locale_symbols(src): # find smarter way to do it!
    return src.replace(r'ą', 'a').replace(r'ć', 'c').replace(r'ę', 'e').replace(r'ł', 'l')\
           .replace(r'ń', 'n').replace(r'ó', 'o').replace(r'ś', 's').replace(r'ź', 'z')\
           .replace(r'ż', 'z').replace(r'Ą', 'A').replace(r'Ć', 'C').replace(r'Ę', 'E')\
           .replace(r'Ł', 'L').replace(r'Ń', 'N').replace(r'Ó', 'O').replace(r'Ś', 'S')\
           .replace(r'Ź', 'Z').replace(r'Ż', 'Z')
