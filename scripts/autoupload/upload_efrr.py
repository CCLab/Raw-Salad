# -*- coding: utf-8 -*-

'''
Created on 05-09-2011
'''

import os
import optparse
from functools import cmp_to_key

from auto_upload import upload


    
def filter_csv_files(name):
    return '.csv' == name[-4:] and 'upload' not in name and 'TERYT' not in name


def get_persp_type(name):
    if 'kraj' in name:
        return 'kr'
    if 'wojewodztwo' in name:
        return 'wo'
    if 'powiat' in name:
        return 'po'
    if 'gmina' in name:
        return 'gm'

    
def compare_names(name1, name2): 
    values = {'kr': 0, 'wo': 1, 'po': 2, 'gm': 3}
    val1 = values[get_persp_type(name1)]
    val2 = values[get_persp_type(name2)]
    if val1 < val2 or (val1 == val2 and name1 < name2):
        return -1
    elif val1 == val2 and name1 == name2:
        return 0
    else:
        return 1
    

if __name__ == '__main__':
    cmdparser = optparse.OptionParser(usage="usage: python %prog [Options] source_file.csv source_schema.json") 
    cmdparser.add_option("-f", "--conf", action="store", dest="conf_filename", help="configuration file")
    opts, args = cmdparser.parse_args()
    
    files_dir = os.path.join(os.getcwd(), 'data')
    all_files = os.listdir(files_dir)
    csv_files = filter(filter_csv_files, all_files)
    
    # sort files so that they are processed in the following order:
    # krajowe -> wojewodzkie > powiatowe > gminne
    csv_files = sorted(csv_files, key=cmp_to_key(compare_names))
    db = None
    create_new_nav = True
    
    for file in csv_files:
        full_path = os.path.join(files_dir, file)
        schema_descr = file.rstrip('.csv') + '-schema_descr.json'
        schema_path = os.path.join(files_dir, schema_descr)
        hierarchy_path = os.path.join(files_dir, 'hierarchy.json')
        teryt_path = os.path.join(files_dir, 'TERYT.csv')
        year = file.rstrip('.csv')[-4:]
        persp_type = get_persp_type(file)
        coll = 'dd_effr' + year + '_' + persp_type 
        args = [full_path, schema_path, hierarchy_path]
        print 'Processing file %s' % file
        db = upload(args, conf_filename=opts.conf_filename, coll_name=coll,
                    teryt_filename=teryt_path, db=db, new_nav=create_new_nav)
        create_new_nav = False

    