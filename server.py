from flask import Flask,render_template,request,redirect, url_for, make_response
#from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send, emit
from tools import *
from functools import wraps
import random
import database

app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'     #change this password to your MySQL password for root@localhost 
app.config['MYSQL_DB'] = 'Game_server'

GAME_ID_SNAKE = 1
GAME_ID_CONNECT4 = 2

logged_in_users =[]

snakeUsers={}
snakeWaitingSid=[]
snakePartners={}

c4users = {}
c4WaitingSid = []
c4pairs = {}

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.cookies.get('email') != None:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('Login', needLogin=True))
    return wrap

# App functionality
@app.route('/')
def Home():
    resp = make_response(render_template('login.html'))
    email = request.args.get('email')
    if email in logged_in_users:
        logged_in_users.remove(email)
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
        data = database._DB.select("SELECT PlayerID FROM Login_Credentials WHERE PlayerID = %s;", (email,), "all")
        if (data == -1):
            return errorDB, 500
        if(len(data) is 0):
            error = None
            res = database._DB.insert("INSERT INTO Player_Profile(PlayerID,firstName,lastName) VALUES (%s,%s,%s);", (email, firstName, lastName))
            if (res == -1):
                return errorDB, 500
            res = database._DB.insert("INSERT INTO Login_Credentials VALUES(%s,MD5(%s));", (email, password))
            if (res == -1):
                return errorDB, 500
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
        enc_string = database._DB.select("SELECT MD5(%s);", (password,), "all")
        if (enc_string == -1):
            return errorDB, 500
        stored = database._DB.select("SELECT password FROM Login_Credentials WHERE PlayerID = %s;", (email,), "all")
        if (stored == -1):
            return errorDB, 500
        if(len(stored) is 0):
            error = 'Email not found!'
        else:
            if(enc_string==stored):
                logged_in_users.append(email)
                #get the playerID
                res = database._DB.callproc("fullName", (email,))
                if res == -1:
                   return errorDB, 500
                resp = make_response(redirect(url_for('Index')))
                resp.set_cookie('email',email)
                resp.set_cookie('fullName', res[0])
                return resp
            else:
                error = 'Invalid password'
    return render_template('login.html', error = error)

@app.route('/logout')
def Logout():
    resp = make_response(redirect(url_for('Login')))
    email = request.args.get('email')
    resp.set_cookie('email', expires=0)
    resp.set_cookie('fullName', expires=0)
    if email in logged_in_users:
        logged_in_users.remove(email)
    return resp

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def Profile():
    error = None
    email = request.cookies.get('email')
    if request.method=='POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        res = database._DB.update("UPDATE Player_Profile SET firstName = %s, lastName = %s WHERE PlayerID = %s;", (firstName,lastName,email))
        if (res == -1):
            return errorDB, 500
    res = database._DB.select("SELECT PlayerID, firstName, lastName, Cash, Gold FROM Player_Profile WHERE PlayerID = %s;", (email,))        
    if (res == -1):
        return errorDB, 500
    (user_email,firstName,lastName,cash,gold) = res
    name = firstName+" "+lastName
    resp = make_response(render_template('profile.html', email=user_email, name=name, cash=cash, gold=gold))
    #reset the fullName cookie if it has been updated
    if name != request.cookies.get('fullName'):
        resp.set_cookie('fullName', name)
    return resp

@app.route('/leaderboard')
@login_required
def Leaderboard():
    _sql = "SELECT @rank:=@rank+1 as _rank, firstName, lastName, Cash FROM Player_Profile p, (select @rank := 0) r ORDER BY Cash DESC;"
    values = database._DB.select(_sql, None, "all")
    if (values == -1):
        return errorDB, 500
    cash_leaderboard = [list(x) for x in values]
    _sql = "SELECT @rank:=@rank+1 as _rank, firstName, lastName, Gold FROM Player_Profile p, (select @rank := 0) r ORDER BY Gold DESC;"
    gold_leaderboard = database._DB.select(_sql, None, "all")
    if (gold_leaderboard == -1):
        return errorDB, 500
    gold_leaderboard = [list(x) for x in values]
    return render_template('leaderboard.html',cash_leaderboard=cash_leaderboard, gold_leaderboard=gold_leaderboard)

@app.route('/history')
@login_required
def PlayerHistory():
    email = request.cookies.get('email')
    _sql = "SELECT @rank:=@rank+1 AS _rank, Cash, Gold FROM Player_History p, (SELECT @rank := 0) r WHERE PlayerID=%s AND GameID=%s ORDER BY Cash DESC;"
    values = database._DB.select(_sql, (email, GAME_ID_SNAKE), "all")
    if (values == -1):
        return errorDB, 500
    snake_history = [list(x) for x in values]
    _sql = "SELECT @rank:=@rank+1 AS _rank, Cash, Gold FROM Player_History p, (SELECT @rank := 0) r WHERE PlayerID=%s AND GameID=%s ORDER BY Cash DESC;"
    values = database._DB.select(_sql, (email, GAME_ID_CONNECT4), "all")
    connect4_history = [list(x) for x in values]
    return render_template('playerHistory.html',snake_history=snake_history, connect4_history=connect4_history)

@app.route('/shop')
@login_required
def Shop():
    _sql = "SELECT * from Perks_Available;"
    values = database._DB.select(_sql, None, "all")
    if (values == -1):
        return errorDB, 500
    perks = [list(x) for x in values]
    return render_template('store.html', perks = perks)

@app.route('/index.html')
@login_required
def Index():
    email = request.cookies.get('email')
    return render_template('index.html', email=email)

@app.route('/miniGames.html')
@login_required
def MiniGames():
    email = request.cookies.get('email')
    fullName = request.cookies.get('fullName')
    return render_template('miniGames.html', email=email, fullName=fullName)

@app.route('/waitingPage.html')
@login_required
def Waiting():
    email = request.cookies.get('email')
    game_id = int(request.args.get('game_id'))
    _sql = "SELECT GameID FROM Players_in_Game WHERE GameID = %s;"
    stored = database._DB.select(_sql, (game_id,), "all")
    if (stored == -1):
        return errorDB, 500
    if(len(stored)%2==0):
        _sql = "SELECT No_of_rooms FROM Mini_Game WHERE GameID = %s;"
        stored = database._DB.select(_sql, (game_id,))
        if (stored == -1):
            return errorDB, 500
        curr_rooms = stored[0]
        curr_rooms = curr_rooms + 1
        _sql = "UPDATE Mini_Game SET No_of_rooms = %s WHERE GameID = %s;"
        res = database._DB.update(_sql, (curr_rooms, game_id))
        if (res == -1):
            return errorDB, 500
        _sql = "INSERT INTO Players_in_Game VALUES(%s,%s,%s);"
        res = database._DB.insert(_sql, (email, game_id, curr_rooms))
        return render_template('waitingPage.html', email=email, game_id=game_id)
    else:
        _sql = "SELECT No_of_rooms FROM Mini_Game WHERE GameID = %s;"
        stored = database._DB.select(_sql, (game_id,))
        if (stored == -1):
            return errorDB, 500
        curr_rooms = stored[0]
        _sql = "INSERT INTO Players_in_Game VALUES(%s,%s,%s);"
        res = database._DB.insert(_sql, (email, game_id, curr_rooms))
        if (res == -1):
            return errorDB, 500
        if game_id == GAME_ID_SNAKE:
            snakePartners[email]=snakeWaitingSid[0]
            snakePartners[snakeWaitingSid[0]]=email
            return redirect(url_for('SAL'))
        elif game_id == GAME_ID_CONNECT4:
            c4pairs[email] = c4WaitingSid[0]
            c4pairs[c4WaitingSid[0]] = email 
            return redirect(url_for('Connect4'))

@app.route('/snakegame.html')
@login_required
def SAL():
    email = request.cookies.get('email')
    #redirect to index if the email is not in snakePartners
    if email not in snakePartners:
        return redirect(url_for("Logout"))
    player2 = GetFullName(snakePartners[email])
    player1 = request.cookies.get("fullName")
    return render_template('snakegame.html', player1=player1, player2=player2)

@app.route('/connect4')
@login_required
def Connect4():
    email = request.cookies.get('email')
    #redirect to index if the email is not in the dictionnary
    if email not in c4pairs:
        return redirect(url_for("Logout"))
    paired_email = GetFullName(c4pairs[email])
    fullName = request.cookies.get("fullName")
    if email in c4WaitingSid:
        return render_template('connect4.html', fullName=fullName, email=email, paired_email=paired_email, color="red")
    else:
        return render_template('connect4.html', fullName=fullName,email=email, paired_email=paired_email, color="black")

# Socket IO functionality
@socketio.on('waiting_id', namespace='/private')
def receive_waiting_user(data):
    if int(data['game_id']) == GAME_ID_SNAKE:
        snakeWaitingSid.clear()
        snakeWaitingSid.append(data['player'])
        snakeWaitingSid.append(request.sid)
    elif int(data['game_id']) == GAME_ID_CONNECT4:
        c4WaitingSid.clear()
        c4WaitingSid.append(data['player'])
        c4WaitingSid.append(request.sid)        

@socketio.on('user_email', namespace='/private')
def receive_username(data):
    if int(data['game_id']) == GAME_ID_SNAKE:
        snakeUsers[data['player']] = request.sid
    elif int(data['game_id']) == GAME_ID_CONNECT4:
        c4users[data['player']] = request.sid

@socketio.on('redirectionSocket', namespace='/private')
def leave_waiting(arr):
    if int(arr['game_id']) == GAME_ID_SNAKE:
        emit('waitingHere',arr,room=snakeWaitingSid[1])
    elif int(arr['game_id']) == GAME_ID_CONNECT4:
        emit('waitingHere',arr,room=c4WaitingSid[1])

@socketio.on('moveSender', namespace='/private')
def send_move(arr):
    email = request.cookies.get('email')
    if(arr[0] == 'check2x'):
        arr.clear()
        _sql = "SELECT Quantity FROM Owned_Perk WHERE PlayerID = %s AND PerkID = %s;"
        stored = database._DB.select(_sql, (email, 1), "all")
        if (stored == -1):
            return errorDB, 500
        if(len(stored)==0 or stored[0][0]==0):
            arr.append('twoxFailed')
        else:
            newVal = stored[0][0] - 1
            _sql = "UPDATE Owned_Perk SET Quantity=%s WHERE PlayerID = %s AND PerkID = %s;"
            res = database._DB(_sql, (newVal, email, 1))
            if (res == -1):
                return errorDB, 500
            arr.append('twoxPassed')
        emit('getMove',arr,room=snakeUsers[email])
    elif(arr[0] == 'checkHeadStart'):
        player1 = True
        if(arr[1]=='p2'):
            player1 = False
        arr.clear()
        arr.append(player1)
        _sql = "SELECT Quantity FROM Owned_Perk WHERE PlayerID = %s AND PerkID = %s;"
        stored = database._DB.select(_sql, (email, 2), "all")
        if (stored == -1):
            return errorDB, 500
        if(len(stored)==0 or stored[0][0]==0):
            arr.append('headStartFailed')
        else:
            newVal = stored[0][0] - 1
            print(newVal)
            _sql = "UPDATE Owned_Perk SET Quantity= %s WHERE PlayerID = %s AND PerkID = %s;"
            res = database._DB.update(_sql, (newVal, email, 2))
            if (res == -1):
                return errorDB, 500
            arr.append('headStartPassed')
            arr.append(random.randint(1,11))
        emit('getMove',arr,room=snakeUsers[email])
        emit('getMove',arr,room=snakeUsers[snakePartners[email]])
    else:
        partner = snakePartners[email]
        emit('getMove',arr,room=snakeUsers[partner])

@socketio.on('board', namespace='/private')
def running_game(data):
    if data == "twoXMultiplier":
        email = request.cookies.get('email')
        _sql = "SELECT Quantity FROM Owned_Perk WHERE PlayerID = %s AND PerkID = %s;"
        stored = database._DB.select(_sql, (email, 1), "all")
        if (stored == -1):
            return errorDB, 500
        if(len(stored)==0 or stored[0][0]==0):
            emit('game_state',"fail",room=c4users[email])
        else:
            newVal = stored[0][0] - 1
            print(newVal)
            _sql = "UPDATE Owned_Perk SET Quantity='{0}' WHERE PlayerID = %s AND PerkID = %s;"
            res = database._DB.update(_sql, (newVal, email, 1))
            if (res == -1):
                return errorDB, 500
            emit('game_state',"passed",room=c4users[email])
    else:
        email = data['user']
        paired_email = c4pairs[email]
        emit('game_state',data,room=c4users[paired_email])

@socketio.on('update_database', namespace='/private')
def update_db(arr):
    email = request.cookies.get('email')
    _sql = "SELECT GameID,RoomID FROM Players_in_Game WHERE PlayerID = %s;"
    stored = database._DB.select(_sql, (email,))
    cur.execute(_sql.format(email))
    stored=cur.fetchall()
    gameID = stored[0]
    roomID = stored[1]
    _sql = "INSERT INTO Player_History VALUES (%s,%s,%s,%s,%s);"
    args = (email, gameID, roomID, arr[0], arr[1])
    res = database._DB.insert(_sql, args)
    if (res == -1):
        return errorDB, 500
    _sql = "DELETE FROM Players_in_Game WHERE PlayerID = %s;"
    res = database._DB.delete(_sql, (email,))
    if (res == -1):
        return errorDB, 500
    _sql = "SELECT Cash,Gold FROM Player_Profile WHERE PlayerID = %s;"
    stored = database._DB.select(_sql, (email,))
    cash = stored[0]
    gold = stored[1]
    cash += arr[0]
    gold += arr[1]
    _sql = "UPDATE Player_Profile SET Cash=%s, Gold=%s WHERE PlayerID=%s;"
    res = database._DB.update(_sql, (cash, gold, email))
    if (res == -1):
        return errorDB, 500

@socketio.on('buyPerk', namespace='/private')
def buyPerk(arr):
    email = request.cookies.get('email')
    if(arr[0]=='getAvailableGold'):
        _sql = "SELECT Gold FROM Player_Profile WHERE PlayerID = %s;"
        stored = database._DB.select(_sql, (email,))
        if (stored == -1):
            return errorDB, 500
        gold = stored[0]
        arr.clear()
        arr.append('goldAvailable')
        arr.append(gold)
        emit('perkResult',arr,room=request.sid)
    else:
        _sql = "SELECT Quantity FROM Owned_Perk WHERE PlayerID = %s AND PerkID = %s;"
        stored = database._DB.select(_sql, (email, arr[1]))
        if(len(stored) is 0):
            quantity = 1
            _sql = "INSERT INTO Owned_Perk VALUES(%s,%s,%s);"
            args = (email, arr[1], quantity)
            res = database.db.insert(_sql, args)
            if (res == -1):
                return errorDB, 500
        else:
            quantity = stored[0]
            quantity = quantity + 1
            _sql = "UPDATE Owned_Perk SET Quantity = %s WHERE PlayerID = %s AND PerkID = %s;"
            res = database._DB.update(_sql, (quantity, email, arr[1]))
            if (res == -1):
                return errorDB, 500
        _sql = "UPDATE Player_Profile SET Gold = %s WHERE PlayerID = %s;"
        res = database._DB.update(_sql, (arr[2], email))
        if (res == -1):
            return errorDB, 500

if __name__ == "__main__":
    #initiate database connexion
    database.NewConexion(app)
    socketio.run(app)