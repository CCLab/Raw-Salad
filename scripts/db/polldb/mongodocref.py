#!/usr/bin/python

"""
mongodb collections autoreferencing
analog of RDB foreign key
Not universal!! Works for db 'cclpolls' on the collections 'db.kandydaci_rady' -> 'db.komitety' (one to many)
"""

from pymongo.connection import Connection
from pymongo.son_manipulator import AutoReference, NamespaceInjector

try:
    connection = Connection("localhost", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = connection["cclpoll"]


db.add_son_manipulator(NamespaceInjector())
db.add_son_manipulator(AutoReference(db))

# in 'kandydaci_rady' (collection_dataset) should be ref to 'komitety' (collection_reference)
dataset_name= 'kandydaci_rady'
reference_name= 'komitety'
foreign_key_name= 'sygnatura'

collection_dataset= db[dataset_name]
collection_reference= db[reference_name]

dict_updated=[]

i= 0
for row_ds in collection_dataset.find():
    i += 1
    row_ds_upd= row_ds # the copy of the document for update
    ds_foreign_key= row_ds[foreign_key_name] # getting the value of a foreign key
    row_ds_id= row_ds['_id']
    row_rf= collection_reference.find_one({foreign_key_name:ds_foreign_key}) # getting the document in the reference (ideally should be only one)
    row_ds_upd['ref_'+reference_name]= row_rf
    dict_updated.append(row_ds_upd)
    print i, row_ds_id

print "...removing old data"
collection_dataset.remove()
print "...inserting new data"
collection_dataset.insert(dict_updated)

# query through references
# db.kandydaci_rady.findOne({"ref_komitety.$id":ObjectId("4d5718d4728b020789000074")})
