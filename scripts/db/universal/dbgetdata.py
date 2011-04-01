import getpass
import pymongo
import json

from time import time

#-----------------------------
if __name__ == "__main__":
    # read connection from rawsdoc conf file
    conn_host= 'localhost'
    conn_port= 27017
    conn_usrname= 'readonly'
    conn_db= 'rawsdoc00'
    conn_coll= 'dd_budg2011_go'
    conn_schema= 'md_budg_scheme'
    # django should give me this parameters
    cond_node= 1 # there can be several nodes (in addition to 'null' - root levels)
    cond_columns_aux= ['parent', 'level'] # 'technical' columns

    try:
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[conn_db]
        print '...connected to the database', db
    except:
        print "Unable to connect to the mongodb database!"
        exit()

    db.authenticate(conn_usrname, "")

    full_data= {}

    # EXTRACT metadata
    cursor_metadata= db[conn_schema].find_one({ 'collection' : conn_coll }, { '_id' : 0 })
    full_data= cursor_metadata.copy()
    md_leaf= cursor_metadata['leaf'] # the deepest level in the collection
    for curr_leaf in md_leaf:
        if curr_leaf['node'] == cond_node:
            full_data['leaf']= curr_leaf['level']
            break

    # EXTRACT data (rows)
    cond_node= {}
    cond_node['node']= {'$in': [None, 1]} # specify the node

    md_columns= cursor_metadata['columns']
    md_select_columns= {'_id':0}
    for clm in md_columns: # list of basic columns - for find()
        md_select_columns[clm['key']]= 1

    for clm in cond_columns_aux: # plus some info for JS
        md_select_columns[clm]= 1

    cursor_data= db[conn_coll].find(cond_node, md_select_columns) # default batchsize is enough here
    dt_rows= []
    for row in cursor_data:
        dt_rows.append(row)
    full_data['rows']= dt_rows

    filename_json= 'budggofill.json'
    json_write= open(filename_json, 'w')
    print '...writing data to JSON file', filename_json
    print >>json_write, json.dumps(full_data, indent=4, ensure_ascii= False)
    json_write.close()
    print 'Done'
