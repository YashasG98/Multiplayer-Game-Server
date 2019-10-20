from flask import Flask,render_template,request,redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'
# app.config['MYSQL_PASSWORD'] = 'Shashwath@99'
app.config['MYSQL_DB'] = 'Game_server'

mysql = MySQL(app)

@app.route('/')
def Home():
    return render_template('login.html')


@app.route('/register.html',methods = ['GET','POST'])
def Register():
    error = None

    if request.method=='POST':
        email=request.form['registerEmail']
        password=request.form['registerPassword']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        cur=mysql.connection.cursor()
        _sql = "select * from Login_credentials where email = '{0}'"
        cur.execute(_sql.format(email))
        data=cur.fetchall()
        if(len(data) is 0):
            error = None
            cur.execute("INSERT INTO Login_credentials VALUES(%s,MD5(%s))",(email,password))
            cur.execute("INSERT INTO Player_profile(email,firstName,lastName) VALUES(%s,%s,%s)",(email,firstName,lastName))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('Login'))
        else:
            error = 'Email already registered!'
    return render_template('register.html', error = error)

@app.route('/login.html', methods = ['GET', 'POST'])
def Login():
    error = None

    if request.method=='POST':
        email=request.form['loginEmail']
        password=request.form['loginPassword']
        cur=mysql.connection.cursor()
        _sql = "select md5('{0}')"
        cur.execute(_sql.format(password))
        enc_string=cur.fetchall()
        _sql = "select password from Login_credentials where email = '{0}'"
        cur.execute(_sql.format(email))
        stored=cur.fetchall()
        if(len(stored) is 0):
            error = 'Email not found!'
        else:
            if(enc_string==stored):
                return redirect('/index.html', code=302)
                cur.close()
            else:
                error = 'Invalid password'

    return render_template('login.html', error = error)

@app.route('/index.html')
def Index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
