from urllib import urlopen
import simplejson as json
import xml.etree.ElementTree as et

host = 'http://cecyf.megivps.pl/api/json/'
col = 'http://cecyf.megivps.pl/api/json/dataset/0/view/1/issue/2011/'
urls = [
    host+'dataset/',
    host+'dataset/0/',
    host+'dataset/0/view/',
    host+'dataset/0/view/1/',
    host+'dataset/0/view/1/issue/',
    host+'dataset/0/view/1/issue/2011/',
    host+'dataset/0/view/1/',
    col+'meta/',
    col+'tree/',
    col+'a/',
    col+'a/1/',
    col+'a/1/?fields=[v_total, name]',
    col+'a/[1+AND+4]/',
    col+'a/[1+AND+4]/?fields=[v_total, name]',
    col+'a/[1+TO+4]/',
    col+'a/[1+TO+4]/?fields=[v_total, name]',
    col+'a/[1+AND+4+TO+6]/',
    col+'a/[1+AND+4+TO+6]/?fields=[v_total, name]',
    col+'a/[1+AND+4+TO+6+AND+8]/',
    col+'a/[1+AND+4+TO+6+AND+8]/?fields=[v_total, name]',
    col+'a/1/[1-1+AND+1-3]/',
    col+'a/1/[1-1+AND+1-3]/?fields=[v_total, name]',
    col+'a/1/[1-1+TO+1-3]/',
    col+'a/1/[1-1+TO+1-3]/?fields=[v_total, name]',
    col+'a/1/[1-1+AND+1-3+TO+1-6]/',
    col+'a/1/[1-1+AND+1-3+TO+1-6]/?fields=[v_total, name]',
    col+'a/1/[1-1+AND+1-3+TO+1-6+AND+1-8]/',
    col+'a/1/[1-1+AND+1-3+TO+1-6+AND+1-8]/?fields=[v_total, name]'
]


for url in urls:
    # try json
    try:
        data = json.loads( urlopen( url ).read() )
        if 'ERROR' in data['response']:
            print url

    except simplejson.decoder.JSONDecodeErroras as detail:
        print "JSON decoder error: " + detail
        print "ON URL: " + url

    # try xml
    try:
        data = et.XML( urlopen( url.replace('json', 'xml' )).read() )
        if 'ERROR' in data.find('response').text:
            print url.replace( 'json', 'xml' )

    except xml.etree.ElementTree.ParseError as detail:
        print "XML parser error: " + detail
        print "ON URL: " + url



