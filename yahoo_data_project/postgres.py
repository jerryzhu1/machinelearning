#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import sys

cars = (
    (1, 'Audi', 52642),
    (2, 'Mercedes', 57127),
    (3, 'Skoda', 9000),
    (4, 'Volvo', 29000),
    (5, 'Bentley', 350000),
    (6, 'Citroen', 21000),
    (7, 'Hummer', 41400),
    (8, 'Volkswagen', 21600)
)

con = None

try:
     
    con = psycopg2.connect(database='calogica', user='calogica') 
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("DROP TABLE IF EXISTS cars")
    cur.execute("CREATE TABLE cars(id INT PRIMARY KEY, name TEXT, price INT)")
    query = "INSERT INTO cars (id, name, price) VALUES (%s, %s, %s)"
    cur.executemany(query, cars)

    
    con.commit()
    
    cur.execute("SELECT * FROM cars")

    rows = cur.fetchall()

    for row in rows:
        print "%s %s %s" % (row["id"], row["name"], row["price"])
        
except psycopg2.DatabaseError, e:
    
    if con:
        con.rollback()
           
    print 'Error %s' % e     
    sys.exit(1)
    
    
finally:
    
    if con:
        con.close()