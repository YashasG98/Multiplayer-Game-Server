from flask_mysqldb import MySQL
#from server import mysql
import database

#default error message in case an error occurs with the database
errorDB = "Database unreachable"

#get a user full name by their id
def GetFullName(id):
	 #get opponent full name
	res = database._DB.callproc("fullName", (id,))
	if (res == -1):
		return "ERROR DATABASE"
	fullName = res[0]
	return fullName