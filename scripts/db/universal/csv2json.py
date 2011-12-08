#!/usr/bin/python

#
# simple JSON file export from CSV dumps (universal)
#
# what should be taken into consideration, and what this script doesn't do:
# - the header should consist of ascii symbols only
# - the header shoudn't contain any special symbol like \", ",", ":", "|" etc. (except "_" and "-")
# - there should be no spaces in the header
# - decimal separator should be dot ".", not comma ","
# - all changes should be done manually in csv before convert
#

import optparse
import csv
import json
import itertools

#-----------------------------------------------
# parse CSV, convert it to JSON and save to file
def csv_parse(filename_csv, filename_json, delimit, quote, jsindent):
    try:
        csv_src= open(filename_csv, 'rb')
    except IOError as e:
        print 'Unable to open src_file:\n %s\n' % e
    else:
        csv_read= csv.reader(csv_src, delimiter= delimit, quotechar= quote)
        json_write= open(filename_json, 'w')

        out= []
        for row in csv_read:
            keys= tuple(row)
            keys_len= len(keys)
            row= iter(row)
            out= [ dict(zip( keys, row )) for row in csv_read ]

        try:
            print >>json_write, json.dumps(out, indent=jsindent, ensure_ascii=False)
        except IOError as writerr:
            print 'Unable to save out_file:\n %s\n' % writerr
        finally:
            csv_src.close()
            json_write.close()
            print "File saved: " + filename_json


#-----------------------------
# process command line options
cmdparser = optparse.OptionParser() 
cmdparser.add_option("--src_file",action="store",help="input CSV file (required)")
cmdparser.add_option("--out_file",action="store",help="output JSON file (optional, SRC_FILE.JSON if not specified)")
cmdparser.add_option("--i",action="store",dest='indent',help="indent in JSON file")
opts, args = cmdparser.parse_args()

if opts.src_file is not None:
    filename_csv= opts.src_file
    if opts.out_file is None:
        filename_json= filename_csv.rstrip('.csv')+'.json'
    else:
        filename_json= opts.out_file

    indt= opts.indent
    if indt is not None:
        indt= int(indt)

    csv_delim= ';'
    csv_quote= '"'

    csv_parse(filename_csv, filename_json, csv_delim, csv_quote, indt) #call a function that process the whole thing
