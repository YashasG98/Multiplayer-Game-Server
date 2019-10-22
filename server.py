from flask import Flask,render_template,request,redirect, url_for, make_response
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'
# app.config['MYSQL_PASSWORD'] = 'Shashwath@99'
app.config['MYSQL_DB'] = 'Game_server'

mysql = MySQL(app)

logged_in_users =[]



@app.route('/')
def Home():
    resp = make_response(render_template('login.html'))
    email = request.args.get('email')
    if email in logged_in_users:
        logged_in_users.remove(email)
        # cannot delete cookie, but works even without deleting
        # resp.delete_cookie('email')
    return resp        

@app.route('/register.html',methods = ['GET','POST'])
def Register():
    error = None

    if request.method=='POST':
        email=request.form['registerEmail']
        password=request.form['registerPassword']
        firstName = request.form['firstName']
        lastName = request.form['lastName']

        #Valid input check
        if(len(email) is 0):
            error = 'Email cannot be empty'
            return render_template('register.html', error = error)
        if (len(password) < 8):
            error = 'Password must be 8 characters long'
            return render_template('register.html', error = error)
        if (len(firstName) is 0):
            error = 'First Name cannot be empty'
            return render_template('register.html', error = error)
        
        #Valid input handling
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
                logged_in_users.append(email)
                resp = make_response(redirect(url_for('Index')))
                resp.set_cookie('email',email)
                cur.close()
                return resp
            else:
                error = 'Invalid password'

    return render_template('login.html', error = error)

@app.route('/index.html')
def Index():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('index.html', email=email)
    else:
        return redirect(url_for('Login'))

@app.route('/miniGames.html')
def MiniGames():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('miniGames.html', email=email)
    else:
        return redirect(url_for('Login'))

@app.route('/waitingPage.html')
def Waiting():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('waitingPage.html', email=email)
    else:
        return redirect(url_for('Login'))


@app.route('/snakegame.html')
def SAL():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('snakegame.html', email=email)
    else:
        return redirect(url_for('Login'))

if __name__ == "__main__":
    app.run(debug=True)