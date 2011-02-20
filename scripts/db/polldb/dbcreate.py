#!/usr/bin/python

"""
Create and fill the test version of Poll data
Required:
1. PosgreSQL 8.4 or higher
2. The db dump - file dbdump.backup
How to use: >>python dbcreate.py -h
"""

import psycopg2
import getpass
import optparse
import os
from time import gmtime, strftime


#-----------------------------
if __name__ == "__main__":

    cmdparser = optparse.OptionParser() 
    cmdparser.add_option("-s", "--host", action="store", default="localhost", help="database server host [default: %default]")
    cmdparser.add_option("-p", "--port", action="store", default="5432", help="database server - port [default: %default]")
    cmdparser.add_option("-u", "--user", action="store", default="postgres", help="database server - user [default: %default]")
    cmdparser.add_option("-d", "--dbname", action="store", help="database name (will be created) [default: test<datetime>]")
    cmdparser.add_option("-b", "--backup", action="store", help="backup file [default: dbdump.backup]")

    print "... connecting to PostgreSQL server"
    opts, args = cmdparser.parse_args()

    pprompt = getpass.getpass()
    try:
        connect_postgres = psycopg2.connect(host= opts.host, port= opts.port, user= opts.user, password= pprompt)
        print "... connected"
    except Exception, e:
        print 'Unable to connect to the PostgreSQL database:\n %s\n' % e
        exit() #no connection to the database - no data processing

    connect_postgres.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # not to do COMMIT after every insert/update
    cur = connect_postgres.cursor()
    print strftime("%d%m%y_%H%M%S", gmtime())
    dbname= opts.dbname
    if dbname is None:
        dbname= 'test' + strftime("%d%m%Y_%H%M%S", gmtime())
    #create database

    print "... creating database"
    try:
        cur.execute("CREATE DATABASE " + dbname + """
                WITH OWNER = postgres
                ENCODING = 'UTF8'
                TABLESPACE = pg_default
                LC_COLLATE = 'C'
                LC_CTYPE = 'C'
                CONNECTION LIMIT = -1;
        """)
        print "... database", dbname, "successfully created"
    except Exception, e:
        print 'Cannot create database!:\n %s\n' % e
        exit()

    bkfile= opts.backup
    if bkfile is None:
        bkfile= 'dbdump.backup'

    print "... restoring data"

    #restore the db dump
    cmdline= "psql -d " + dbname + " -U " + opts.user + " -f " + bkfile
    try:
        os.system(cmdline)
    except Exception, e:
        print 'Unable to restore database:\n %s\n' % e
        exit()

    print "Done!"
    connect_postgres.close()

    connect_postgres = psycopg2.connect(host= opts.host, port= opts.port, user= opts.user, password= pprompt, database= dbname)
    cur = connect_postgres.cursor()

    print "\nExample of imported data:"
    cur.execute("""
        SELECT k.plec AS "kand_plec", k.typ AS "kand_typ", k.jednostka AS "kand_jednostka", k.szczebel AS "kand_szczebel", mm.typ AS "kom_typ", 
        SUM(k.l_glosow) AS "kand_glosow_total"
        FROM kandydaci_rady k, komitety mm
        WHERE k.sygnatura = mm.sygnatura
        GROUP BY k.plec, k.typ, k.jednostka, k.szczebel, mm.typ
        ORDER BY k.plec, k.typ, k.jednostka, k.szczebel, mm.typ
        LIMIT 10
    """)
    for record in cur:
        print record

    connect_postgres.close()
