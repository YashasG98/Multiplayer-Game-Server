from flask import Flask,render_template,request,redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'
app.config['MYSQL_DB'] = 'Game_server'

mysql = MySQL(app)

@app.route('/')
def Home():
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM users where name like '%o%';")
    # fetchdata = cur.fetchall()
    # cur.close()
    return render_template('login.html')

@app.route('/index.html')
def Login():
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM users where name like '%o%';")
    # fetchdata = cur.fetchall()
    # cur.close()
    return render_template('login.html')

@app.route('/register.html',methods = ['GET','POST'])
def Register():
    if request.method=='POST':
        email=request.form['registerEmail']
        password=request.form['registerPassword']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO Login_credentials VALUES(%s,%s)",(email,password))
        mysql.connection.commit()
        cur.close()
        return redirect('/index.html', code=302)
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
