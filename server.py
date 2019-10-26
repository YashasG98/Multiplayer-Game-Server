from flask import Flask,render_template,request,redirect, url_for, make_response
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'
# app.config['MYSQL_PASSWORD'] = 'Shashwath@99'
app.config['MYSQL_DB'] = 'Game_server'

mysql = MySQL(app)

GAME_ID_SNAKE = 1
logged_in_users =[]
snakeUsers={}
snakeWaitingSid=[]
snakePartners={}

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
        # if (len(password) < 8):
        #     error = 'Password must be 8 characters long'
        #     return render_template('register.html', error = error)
        if (len(firstName) is 0):
            error = 'First Name cannot be empty'
            return render_template('register.html', error = error)
        
        #Valid input handling
        cur=mysql.connection.cursor()
        _sql = "select * from Login_credentials where PlayerID = '{0}'"
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
        _sql = "select password from Login_credentials where PlayerID = '{0}'"
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
        cur=mysql.connection.cursor()
        _sql = "select GameID from Players_In_Game where GameID = '{0}'"
        cur.execute(_sql.format(GAME_ID_SNAKE))
        stored=cur.fetchall()
        if(len(stored)%2==0):
            _sql = "select No_of_rooms from Mini_Game where GameID = '{0}'"
            cur.execute(_sql.format(GAME_ID_SNAKE))
            stored=cur.fetchall()
            curr_rooms = stored[0][0]
            curr_rooms = curr_rooms + 1
            _sql = "update Mini_Game set No_of_rooms = '{0}' where GameID = '{1}'"
            cur.execute(_sql.format(curr_rooms,GAME_ID_SNAKE))
            _sql = "insert into Players_In_Game values('{0}','{1}','{2}')"
            cur.execute(_sql.format(email, GAME_ID_SNAKE, curr_rooms))
            mysql.connection.commit()
            return render_template('waitingPage.html', email=email)
        else:
            _sql = "select No_of_rooms from Mini_Game where GameID = '{0}'"
            cur.execute(_sql.format(GAME_ID_SNAKE))
            stored=cur.fetchall()
            curr_rooms = stored[0][0]
            _sql = "insert into Players_In_Game values('{0}','{1}','{2}')"
            cur.execute(_sql.format(email, GAME_ID_SNAKE, curr_rooms))
            mysql.connection.commit()
            snakePartners[email]=snakeWaitingSid[0]
            snakePartners[snakeWaitingSid[0]]=email
            return redirect(url_for('SAL'))
    else:
        return redirect(url_for('Login'))


@app.route('/snakegame.html')
def SAL():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('snakegame.html', player2=snakePartners[email])
    else:
        return redirect(url_for('Login'))

@socketio.on('waiting_id', namespace='/private')
def receive_waiting_user(user_email):
    snakeWaitingSid.clear()
    snakeWaitingSid.append(user_email)
    snakeWaitingSid.append(request.sid)
    print((snakeWaitingSid))
    print(user_email," waiting!")        

@socketio.on('user_email', namespace='/private')
def receive_username(user_email):
    snakeUsers[user_email] = request.sid
    print(user_email," added!")

@socketio.on('redirectionSocket', namespace='/private')
def leave_waiting(arr):
    emit('waitingHere',arr,room=snakeWaitingSid[1])

if __name__ == "__main__":
    socketio.run(app)