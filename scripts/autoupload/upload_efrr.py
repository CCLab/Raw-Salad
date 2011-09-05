# -*- coding: utf-8 -*-

'''
Created on 05-09-2011
'''

import os
from functools import cmp_to_key

from auto_upload import upload


    
def filter_csv_files(name):
    return '.csv' == name[-4:]


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
    files_dir = os.path.join('data', os.getcwd())
    all_files = os.listdir(files_dir)
    csv_files = filter(filter_csv_files, all_files)

    # sort files so that they are processed in the following order:
    # krajowe -> wojewodzkie > powiatowe > gminne
    csv_files = sorted(csv_files, key=cmp_to_key(compare_names))
    
    for file in csv_files:
        schema_descr = file.rstrip('.csv') + '-schema_descr.json'
        year = file.rstrip('.csv')[-4:]
        persp_type = get_persp_type(file)
        coll = 'dd_effr' + year + '_' + persp_type 
        args = [file, schema_descr, 'hierarchy.json']
        upload(args, coll_name=coll)

    