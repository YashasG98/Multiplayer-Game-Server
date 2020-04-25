from flask_mysqldb import MySQL

class DB(object):
	"""docstring for DB"""
	def __init__(self, app):
		super (DB, self).__init__()
		try:
			self.mysql = MySQL(app)
			self.cursor = None
			self.connected = True
		except:
			self.connected = False

	def select(self, sql_string, args = None, quantity = "one"):
		try:
			self.cursor = self.mysql.connection.cursor()
			self.cursor.execute(sql_string, args)
			retult = 0
			if (quantity == "one"):
				result = self.cursor.fetchone()
			else:
				result = self.cursor.fetchall()
			self.cursor.close()
			return (result)
		except Exception as e:
			print(e)
			return -1

	#used to call a database stored procedure
	def callproc(self, procName, args, quantity = "one"):
		try:
			self.cursor = self.mysql.connection.cursor()
			self.cursor.callproc(procName, args)
			if (quantity == "one"):
				result = self.cursor.fetchone()
			else:
				result = self.cursor.fetchall()
			self.cursor.close()
			return (result)
		except Exception as e:
			print(e)
			return -1

	#insert and update are duplicated methods for the sake of readability and in case we want to add specific behaviour to one of the operations
	#they return the number of affected rows
	def insert(self, sql_string, args = None):
		try:
			self.cursor = self.mysql.connection.cursor()
			self.cursor.execute(sql_string, args)
			result = self.cursor.rowcount
			self.mysql.connection.commit()
			self.cursor.close()
			return (result)
		except Exception as e:
			print(e)
			return -1

	def update(self, sql_string, args = None):
		try:
			self.cursor = self.mysql.connection.cursor()
			self.cursor.execute(sql_string, args)
			result = self.cursor.rowcount
			self.mysql.connection.commit()
			self.cursor.close()
			return (result)
		except Exception as e:
			print(e)
			return -1

	def close(self):
		self.mysql.connection.close()
		return (None)

#implement the singleton logic for the database class
_DB = None

def NewConexion(app):
	global _DB
	_DB = DB(app)