from flask_mysqldb import MySQL
from server import mysql

#get a user full name by their id
def GetFullName(id):
	 #get opponent full name
    cur=mysql.connection.cursor()
    cur.callproc("fullName", (id,))
    res=cur.fetchone()
    fullName = res[0]
    cur.close
    return fullName