from flask import Flask,render_template,request,redirect, url_for, make_response
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Game_server'
# app.config['MYSQL_PASSWORD'] = 'Game_server1234'
app.config['MYSQL_DB'] = 'Game_server'

mysql = MySQL(app)

GAME_ID_SNAKE = 1
GAME_ID_CONNECT4 = 2

logged_in_users =[]

snakeUsers={}
snakeWaitingSid=[]
snakePartners={}

c4users = {}
c4WaitingSid = []
c4pairs = {}

# App functionality
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
            cur.execute("INSERT INTO Player_Profile(email,firstName,lastName) VALUES(%s,%s,%s)",(email,firstName,lastName))
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

@app.route('/profile', methods = ['GET','POST'])
def Profile():
    error = None
    email = request.cookies.get('email')
    if email in  logged_in_users:        
        cur=mysql.connection.cursor()
        if request.method=='POST':
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            _sql = "update Player_Profile set firstName='{0}', lastName='{1}' where PlayerID = '{2}'"
            cur.execute(_sql.format(firstName,lastName,email))
            mysql.connection.commit()
                
        _sql = "select * from Player_Profile where PlayerID = '{0}'"
        cur.execute(_sql.format(email))
        values = cur.fetchall()
        cur.close()
        (user_email,firstName,lastName,cash,gold) = values[0]
        name = firstName+" "+lastName
        return render_template('profile.html', email=user_email, name=name, cash=cash, gold=gold)
    else:
        return redirect(url_for('Login'))

@app.route('/leaderboard')
def Leaderboard():
    email = request.cookies.get('email')
    if email in logged_in_users:
        cur = mysql.connect.cursor()
        _sql = "select @rank:=@rank+1 as rank, firstName, lastName, Cash from Player_Profile p, (select @rank := 0) r order by Cash desc"
        cur.execute(_sql)
        values = cur.fetchall()
        cash_leaderboard = [list(x) for x in values]
        _sql = "select @rank:=@rank+1 as rank, firstName, lastName, Gold from Player_Profile p, (select @rank := 0) r order by Gold desc"
        cur.execute(_sql)
        values = cur.fetchall()
        gold_leaderboard = [list(x) for x in values]
        cur.close()
        return render_template('leaderboard.html',cash_leaderboard=cash_leaderboard, gold_leaderboard=gold_leaderboard)
    else:
        return redirect(url_for('Login'))

@app.route('/shop')
def Shop():
    email = request.cookies.get('email')
    if email in logged_in_users:
        cur = mysql.connect.cursor()
        _sql = "select * from Perks_Available"
        cur.execute(_sql)
        values = cur.fetchall()
        perks = [list(x) for x in values]
        cur.close()
        return render_template('store.html', perks = perks)
    else:
        return redirect(url_for('Login'))

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
    game_id = int(request.args.get('game_id'))
    
    if email in logged_in_users:
    
        cur=mysql.connection.cursor()
        _sql = "select GameID from Players_In_Game where GameID = '{0}'"
        cur.execute(_sql.format(game_id))
        stored=cur.fetchall()
    
        if(len(stored)%2==0):
    
            _sql = "select No_of_rooms from Mini_Game where GameID = '{0}'"
            cur.execute(_sql.format(game_id))
            stored=cur.fetchall()
            curr_rooms = stored[0][0]
            curr_rooms = curr_rooms + 1
            _sql = "update Mini_Game set No_of_rooms = '{0}' where GameID = '{1}'"
            cur.execute(_sql.format(curr_rooms,game_id))
            _sql = "insert into Players_In_Game values('{0}','{1}','{2}')"
            cur.execute(_sql.format(email, game_id, curr_rooms))
            mysql.connection.commit()
            return render_template('waitingPage.html', email=email, game_id=game_id)

        else:
            
            _sql = "select No_of_rooms from Mini_Game where GameID = '{0}'"
            cur.execute(_sql.format(game_id))
            stored=cur.fetchall()
            curr_rooms = stored[0][0]
            _sql = "insert into Players_In_Game values('{0}','{1}','{2}')"
            cur.execute(_sql.format(email, game_id, curr_rooms))
            mysql.connection.commit()

            if game_id == GAME_ID_SNAKE:
                snakePartners[email]=snakeWaitingSid[0]
                snakePartners[snakeWaitingSid[0]]=email
                return redirect(url_for('SAL'))

            elif game_id == GAME_ID_CONNECT4:
                c4pairs[email] = c4WaitingSid[0]
                c4pairs[c4WaitingSid[0]] = email 
                return redirect(url_for('Connect4'))

    else:
        return redirect(url_for('Login'))


@app.route('/snakegame.html')
def SAL():
    email = request.cookies.get('email')
    if email in logged_in_users:
        return render_template('snakegame.html', player2=snakePartners[email])
    else:
        return redirect(url_for('Login'))

@app.route('/connect4')
def Connect4():
    email = request.cookies.get('email')
    paired_email = c4pairs[email]
    if email in logged_in_users:
        if email in c4WaitingSid:
            return render_template('connect4.html', email = email, paired_email=paired_email, color="red")
        else:
            return render_template('connect4.html', email = email, paired_email=paired_email, color="black")
    else:
        return redirect(url_for('Login'))

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
        cur=mysql.connection.cursor()
        arr.clear()
        _sql = "select Quantity from Owned_Perk where PerkID = '{0}'"
        cur.execute(_sql.format(1))
        stored=cur.fetchall()
        if(len(stored)==0 or stored[0][0]==0):
            arr.append('twoxFailed')
        else:
            newVal = stored[0][0] - 1
            print(newVal)
            _sql = "update Owned_Perk set Quantity='{0}' where PlayerID = '{1}' and PerkID = {2}"
            cur.execute(_sql.format(newVal,email,1))
            mysql.connection.commit()
            arr.append('twoxPassed')
        emit('getMove',arr,room=snakeUsers[email])
    else:
        partner = snakePartners[email]
        emit('getMove',arr,room=snakeUsers[partner])

@socketio.on('board', namespace='/private')
def running_game(data):
    print (f"\n\n"+str(data)+" "+str("twoXMultiplier")+" "+" "+(str(data == "twoXMultiplier"))+"\n\n")
    if data == "twoXMultiplier":
        email = request.cookies.get('email')
        cur=mysql.connection.cursor()
        _sql = "select Quantity from Owned_Perk where PerkID = '{0}'"
        cur.execute(_sql.format(1))
        stored=cur.fetchall()
        if(len(stored)==0 or stored[0][0]==0):
            emit('game_state',"fail",room=c4users[email])
        else:
            newVal = stored[0][0] - 1
            print(newVal)
            _sql = "update Owned_Perk set Quantity='{0}' where PlayerID = '{1}' and PerkID = {2}"
            cur.execute(_sql.format(newVal,email,1))
            mysql.connection.commit()
            emit('game_state',"passed",room=c4users[email])
    else:
        email = data['user']
        paired_email = c4pairs[email]
        emit('game_state',data,room=c4users[paired_email])

@socketio.on('update_database', namespace='/private')
def update_db(arr):
    email = request.cookies.get('email')
    cur=mysql.connection.cursor()
    _sql = "select GameID,RoomID from Players_In_Game where PlayerID = '{0}'"
    cur.execute(_sql.format(email))
    stored=cur.fetchall()
    gameID = stored[0][0]
    roomID = stored[0][1]
    _sql = "insert into Player_History values ('{0}',{1},{2},{3},{4});"
    cur.execute(_sql.format(email,gameID,roomID,arr[0],arr[1]))
    _sql = "delete from Players_In_Game where PlayerID = '{0}'"
    cur.execute(_sql.format(email))
    _sql = "select Cash,Gold from Player_Profile where PlayerID = '{0}'"
    cur.execute(_sql.format(email))
    stored = cur.fetchall()
    cash = stored[0][0]
    gold = stored[0][1]
    cash += arr[0]
    gold += arr[1]
    _sql = "update Player_Profile set Cash={0}, Gold={1} where PlayerID='{2}'"
    cur.execute(_sql.format(cash,gold,email))
    mysql.connection.commit()
    cur.close()

@socketio.on('buyPerk', namespace='/private')
def buyPerk(arr):
    email = request.cookies.get('email')
    cur=mysql.connection.cursor()
    if(arr[0]=='getAvailableGold'):
        _sql = "select Gold from Player_Profile where PlayerID = '{0}'"
        cur.execute(_sql.format(email))
        stored = cur.fetchall()
        gold = stored[0][0]
        arr.clear()
        arr.append('goldAvailable')
        arr.append(gold)
        emit('perkResult',arr,room=request.sid)
    else:
        _sql = "select Quantity from Owned_Perk where PlayerID = '{0}' and PerkID = {1}"
        # print('HERE',_sql.format(email,arr[1]))
        cur.execute(_sql.format(email,arr[1]))
        stored=cur.fetchall()
        # print(stored)
        if(len(stored) is 0):
            quantity = 1
            _sql = "insert into Owned_Perk values('{0}',{1},{2})"
            cur.execute(_sql.format(email,arr[1],quantity))
        else:
            quantity = stored[0][0]
            quantity = quantity + 1
            _sql = "update Owned_Perk set Quantity ={0} where PlayerID = '{1}' and PerkID = {2}"
            cur.execute(_sql.format(quantity,email,arr[1]))
        _sql = "update Player_Profile set Gold ={0} where PlayerID = '{1}'"
        cur.execute(_sql.format(arr[2],email))
        mysql.connection.commit()

if __name__ == "__main__":
    socketio.run(app)