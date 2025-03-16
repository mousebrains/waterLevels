#! /usr/bin/env python3

import mysql.connector as mysql

with mysql.connect(host="mysql.wkcc.org",
                   user="levels",
		   password="Deschutes", 
		   database="wkcclevels") as db:
    with db.cursor() as cur:
        cur.execute("SHOW TABLES;")
        for row in cur:
            print(row)
