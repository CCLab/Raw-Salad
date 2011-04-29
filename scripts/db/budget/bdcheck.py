import getpass
import pymongo
import simplejson as json

#-----------------------------
def save2json(filename, data_bulk):
    print '...saving to file', filename
    json_write= open(filename, 'w')
    print >>json_write, json.dumps(data_bulk, indent=4)
    print '...file saved', filename
    json_write.close()


#-----------------------------
if __name__ == "__main__":
    conn_host= 'localhost'
    conn_port= 27017
    conn_usrname= 'readonly'
    conn_db= 'rawsdoc00'
    conn_user= 'readonly'
    conn_passwd= ''

    try:
        conn= pymongo.Connection(conn_host, conn_port)
        db= conn[conn_db]
        print '...connected to the database', db
    except:
        print "Unable to connect to the mongodb database!"
        exit()

    db.authenticate(conn_user, conn_passwd)

    print '\n...extracting data - Budget Zadaniowy'
    conn_coll= 'dd_budg2011_go' #data
    conn_schema= 'md_budg_scheme' #metadata
    #extracting only node 1 from Budget Zadaniowy
    cursor_data= db[conn_coll].find({'node':{'$in':[None, 1]}},{'_id':0, 'node':0}).batch_size(100) # mongodb query (batch_size 100Kb works the best in this case, but should be optimized for the other ones)
    rows= []
    for row in cursor_data:
        rows.append(row)

    cursor_data= db[conn_schema].find_one({'idef':1},{'_id':0})
    full_data= cursor_data.copy()
    full_data['rows']= rows

    save2json(conn_coll+'.json',full_data)


    print '\n...extracting data - Budget Ksegowy'
    #extracting data from Budget Ksegowy
    conn_coll= 'dd_budg2011_tr' #data
    conn_schema= 'md_budg_scheme' #metadata
    cursor_data= db[conn_coll].find({},{'_id':0}).batch_size(100)
    rows= []
    for row in cursor_data:
        rows.append(row)

    cursor_data= db[conn_schema].find_one({'idef':3},{'_id':0})
    full_data= {}
    full_data= cursor_data.copy()
    full_data['rows']= rows

    save2json(conn_coll+'.json',full_data)


    print '\n...extracting data - Funduszy Celowe'
    #extracting data from Funduszy Celowe
    conn_coll= 'dd_fund2011_tr' #data
    conn_schema= 'md_fund_scheme' #metadata
    cursor_data= db[conn_coll].find({},{'_id':0}).batch_size(100)
    rows= []
    for row in cursor_data:
        rows.append(row)

    cursor_data= db[conn_schema].find_one({'idef':10},{'_id':0})
    full_data= {}
    full_data= cursor_data.copy()
    full_data['rows']= rows

    save2json(conn_coll+'.json',full_data)

    print '\n...extracting data - Funduszy Celowe w ukladzie zadaniowym'
    #extracting data from Funduszy Celowe - zadaniowy
    conn_coll= 'dd_fund2011_go' #data
    conn_schema= 'md_fund_scheme' #metadata

    cursor_data= db[conn_schema].find_one({'idef':11},{'_id':0})
    full_data= {}
    full_data= cursor_data.copy()
    if 'batchsize' in full_data:
        batch= full_data.pop('batchsize')
    if 'query' in full_data:
        query= full_data.pop('query')
    if 'sort' in full_data:
        del full_data['sort']
    if 'aux' in full_data:
        del full_data['aux']

    cursor_data= db[conn_coll].find(query,{'_id':0}, sort=[('idef_sort',1), ('parent_sort',1), ('level',1)]).batch_size(100)
    rows= []
    for row in cursor_data:
        rows.append(row)

    full_data['rows']= rows

    save2json(conn_coll+'.json',full_data)

    print '\n Done'
    # pa pa
