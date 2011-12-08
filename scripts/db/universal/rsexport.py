#!/usr/bin/python

"""
export Raw-Salad data to CSV file(s)
Please, type $python rsexport.py --help
"""

import csv, codecs, cStringIO
import urllib2
import simplejson as json
import optparse
from ConfigParser import ConfigParser

class DataContainer:
    """ Getting data using Public API """

    def __init__(self, url):
        self.base_url = url

    def build_url(self, dataset_id= -1, view_id= -1, issue_id= -1):
        """ Builds URL determined by parameters """
        url = self.base_url + 'dataset/'
        if dataset_id >= 0:
            url += str(dataset_id) + '/view/'
            if view_id >= 0:
                url += str(view_id) + '/issue/'
                if issue_id >= 0:
                    url += str(issue_id) + '/'
                    
        return url

    def fetch(self, url):
        """ Getting data using specified url """
        urldata = urllib2.urlopen(url)
        return urldata.read()

    def get_datasets(self):
        """ Get list of datasets """
        datasets_url = self.build_url()
        str_result = self.fetch(datasets_url)
        json_result = json.loads(str_result)
        return json_result['data']

    def get_views(self, dataset_id):
        """ Get list of views of a given dataset """
        views_url = self.build_url(dataset_id)
        str_result = self.fetch(views_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_issues(self, dataset_id, view_id):
        """ Get list of issues based on given dataset and view """
        issue_url = self.build_url(dataset_id, view_id)
        str_result = self.fetch(issue_url)
        json_result = json.loads(str_result)
        return json_result['data']
        
    def get_collection(self, dataset_id, view_id, issue_id):
        """ Get data from collection specified by dataset, view, issue """
        collection_url = self.build_url(dataset_id, view_id, issue_id)
        str_result = self.fetch(collection_url)
        json_result = json.loads(str_result)
        return json_result['data']

    def get_metadata(self, dataset_id, view_id, issue_id):
        """ Get metadata for the collection specified by dataset, view, issue """
        collection_meta_url = self.build_url(dataset_id, view_id, issue_id) + 'meta/'
        str_result = self.fetch(collection_meta_url)
        json_result = json.loads(str_result)
        return json_result['metadata']


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file 'f',
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter=';', **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        new_row= []
        for s in row:
            if type(s) in [str, unicode]:
                new_row.append(s.encode("utf-8"))
            elif type(s) == bool:
                if s:
                    new_row.append('true')
                else:
                    new_row.append('false')
            else:
                new_row.append(s)
        self.writer.writerow(new_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def csv_save(id_tuple, collection_list, collection_fields, curr_filename= None):
    curr_filename_postfix= "-".join( [str(id_tuple[0]), str(id_tuple[1]), id_tuple[2]] )
    if curr_filename is None:
        curr_filename= curr_filename_postfix + ".csv"
    else:
        curr_filename += "_" + curr_filename_postfix + ".csv"
        
    coll_writer = UnicodeWriter(open(curr_filename, 'wb'))

    header= []
    for k in collection_fields: # create header
        header.append(k[1])
    coll_writer.writerow(header)

    for coll_elt in collection_list: # any elt - data row
        data_row= []
        for k in collection_fields:
            val= coll_elt[ k[0] ]
            if val is None:
                val= ''
            data_row.append(val)
                
        coll_writer.writerow(data_row)

    return "...file %s is saved" % curr_filename


def fill_collections_list(coll_list_str= None):
    """ parsing user parameters and building list of tuples with collections to process """

    out= []
    err= 0

    if coll_list_str is None: # we have to fulfill collections ourselves
        datasets = data_container.get_datasets()
        for dataset in datasets:
            views = data_container.get_views(dataset['idef'])
            for view in views:
                issues = data_container.get_issues(dataset['idef'], view['idef'])
                for issue in issues:
                    t = dataset['idef'], view['idef'], issue
                    out.append(t)
    else: # user defined collections
        test_presence= '[' and ']' in coll_list_str
        test_order= coll_list_str.find('[') < coll_list_str.find(']')
        test_count= (coll_list_str.count('[') + coll_list_str.count(']') == 2)

        if test_presence and test_order and test_count:
            coll_list= coll_list_str[coll_list_str.index('[')+1:-1].split(',')
            for coll in coll_list:
                t= coll.split('-')
                if len(t) != 3: # syntax error
                    err= 41
                    break
                out.append( tuple([t[0], t[1], t[2]]) )
        elif (not test_presence) and (not test_order) and (not test_count):
            t= coll_list_str.split('-')
            if len(t) != 3: # syntax error
                err= 41
            else:
                out= [ tuple([t[0], t[1], t[2]]) ]
        else: # syntax error
            err= 40

    return out, err


if __name__ == "__main__":
    # some globals
    error_dict= {
        "0": "OK",
        "40": "ERROR! Wrong format of the list of collections!",
        "41": "ERROR! Wrong format of a collection! Please, use D-V-IIII, where D is dataset, V is view, IIII is issue",
        "44": "ERROR! Data not found"
        }

    # process command line options
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] filename_pattern")
    cmdparser.add_option("-l", "--collection", action="store", dest="coll_list", help="list of collections [x-y-zzzz, n-m-llll, ...] (omitting the parameter means all collections)")
    cmdparser.add_option("-u", "--url", action="store", dest="base_url", default= "http://localhost:8000/api/json/", help="base URL [default: %default]")

    opts, args = cmdparser.parse_args()

    base_url= opts.base_url

    filename_pattern= ''
    if len(args) > 0:
        filename_pattern= args[0]

    data_container = DataContainer(base_url)

    collection_list, err= fill_collections_list(opts.coll_list)
    if err != 0:
        print error_dict[str(err)]
        exit()

    for coll_id in collection_list:
        coll_list= []
        try:
            coll_list= data_container.get_collection(int(coll_id[0]), int(coll_id[1]), str(coll_id[2]))
        except Exception as e:
            print "%s %s %s\n" % (error_dict['44'], str(coll_id), e)

        if len(coll_list) > 0:
            exclude_fields= ['info']
            coll_meta= data_container.get_metadata(int(coll_id[0]), int(coll_id[1]), str(coll_id[2]))
            coll_fields= []
            for clm in coll_meta['fields']:
                if clm['key'] not in exclude_fields:
                    coll_fields.append([ clm['key'], clm['label'] ])
            try:
                response= csv_save(coll_id, coll_list, coll_fields, filename_pattern)
            except Exception as e:
                response= 'ERROR: %s' % e

            print response

    print 'Done'
