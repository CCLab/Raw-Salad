import getpass
import pymongo
import simplejson as json

if __name__ == "__main__":
    conn_host= 'localhost'
    conn_port= 27017
    conn_usrname= 'readonly'
    conn_db= 'rawsdoc00'
    conn_coll= 'dd_budg2011_go'
    conn_coll_meta= 'md_budg_scheme'
    conn_schema= 'md_budg_scheme'
    conn_user= 'readonly'
    conn_passwd= ''
    filename_json= 'budggofill.json'

    try:
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[conn_db]
        print '...connected to the database', db
    except:
        print "Unable to connect to the mongodb database!"
        exit()

    db.authenticate(conn_user, conn_passwd)

    print '...extracting data'
    #extracting only node 1 from Budget Zadaniowy
    cursor_data= db[conn_coll].find({'node':{'$in':[None, 1]}},{'_id':0, 'node':0}).batch_size(100) # mongodb query (batch_size 100Kb works the best in this case, but should be optimized for the other ones)
    rows= []
    for row in cursor_data:
        rows.append(row)

    cursor_data= db[conn_coll_meta].find_one({'idef':1},{'_id':0})
    full_data= cursor_data.copy()
    full_data['rows']= rows

    print '...saving to file'
    json_write= open(filename_json, 'w')
    print >>json_write, json.dumps(full_data, indent=4)
    print '...file saved', filename_json
    json_write.close()
    print 'Done'
