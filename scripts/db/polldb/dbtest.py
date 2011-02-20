#!/usr/bin/python

"""
Simple comparative test of reaction of MongoDB and PostgreSQL
Conducted on data non-indexed
"""

import psycopg2
from time import time
from bson.code import Code

# --- PostgreSQL
try:
    conn_postgres = psycopg2.connect("user='postgres' host='localhost' password='marcinbarski' dbname='cclpoll'")
    print "...connected to PostgreSQL database"
except:
    print "Unable to connect to the PostgreSQL database!"

print "...reading data from PostgreSQL database"

tst1= False
try:
    cur = conn_postgres.cursor()
    tst1= True
    #rows = cur.fetchall()
    #for row in rows:
    #    print row
except:
    print "Error while read from PostgreSQL database!"

if tst1 == True:
    tl= time()
    cur.execute("""SELECT * FROM kandydaci_rady""")
    tlap= time()-tl
    print "\nReading from nPostgreSQL db time - plain query:", tlap
    tl= time()
    cur.execute("""
        SELECT k.plec AS "kand_plec", k.typ AS "kand_typ", k.jednostka AS "kand_jednostka", k.szczebel AS "kand_szczebel",
                SUM(k.l_glosow) AS "kand_glosow_total", COUNT(*) as "rec_count"
        FROM kandydaci_rady k
        GROUP BY k.plec, k.typ, k.jednostka, k.szczebel
        ORDER BY kand_glosow_total DESC, k.plec, k.typ, k.jednostka, k.szczebel
    """)
    tlap= time()-tl
    print "Reading from PostgreSQL db time - aggregation:", tlap, "\n"

conn_postgres.close()


# --- mongodb
try:
    conn_mongo = pymongo.Connection("localhost", 27017)['cclpoll']
    print "...connected to mongodb database"
except:
    print "Unable to connect to the mongodb database!"

print "...reading data from mongo database"

tst2= False
try:
    tst2= True
    collection = conn_mongo['kandydaci_rady']
    #rows = cur.fetchall()
    #for row in rows:
    #    print row
except:
    print "Error while read from PostgreSQL database!"

if tst2 == True:
    tl= time()
    collection_data= collection.find()
    tlap= time()-tl
    print "\nExtract from collection in mongodb - time:", tlap
    tl= time()
    map= Code("function() { emit("
               "  { kand_plec: this.plec, kand_typ: this.typ, kand_jednostka: this.jednostka, kand_szczebel: this.szczebel },"
               "  { kand_glosow_sum: this.l_glosow, recs: 1 }"
               ");}")
    reduce= Code("function(key, vals) {"
                 "  var ret= { kand_glosow_sum: 0, recs: 0 };"
                 "  for(var i= 0; i < vals.length; i++) {"
                 "    ret.kand_glosow_sum += vals[i].kand_glosow_sum;"
                 "    ret.recs += vals[i].recs;"
                 "  }"
                 "  return ret;"
                 "}"
        )
    result = collection.map_reduce(map, reduce, query={"l_glosow": {"$ne": "null"}})
    tlap= time()-tl
    print "Map-Reducing collection in mongodb - time:", tlap, "\n"
