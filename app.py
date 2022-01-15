#Property of @bybadev © 2021 

from flask import Flask, render_template, redirect, url_for, request, session, flash
from sqlalchemy import create_engine
from datetime import timedelta
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30) #30 minutes of inactivity

####### CONNECTING TO DATABASE #######

engine = create_engine('mysql+pymysql://username:password@host:port/database_name')

connection = engine.connect()

####### ROUTES #######

def base():
    return render_template('base.html') 

@app.route('/') 
def welcome():
    if 'username' and 'userpswd' in session: 
        return redirect(url_for('user')) 
    else:
        return render_template('welcome.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST": 
        username = request.form['username']
        userpswd = request.form['userpswd']
        query = connection.execute ('SELECT * FROM users WHERE username = %s AND pswd = %s;', (username, userpswd))
        acc = query.fetchone() 
        if acc: 
            session.permanent = True
            session['username'] = username
            session['userpswd'] = userpswd
            return redirect(url_for('user'))
        else:
            flash('User does not exist!', 'error')
            return render_template('login.html')
            
    else:
        return render_template('login.html') 
            

@app.route("/user") 
def user(): 
    if 'username' and 'userpswd' in session:
        username = session.get('username')
        return render_template('user.html',user=username)
    else:
        flash('You need to Log In first!', 'info')
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.pop("username", None) 
    session.pop('userpswd', None)
    session.pop('room', None)
    flash('Log Out Successful.', 'success')
    return redirect(url_for('login'))
        

@app.route('/registration', methods = ['GET', 'POST']) 
def register():
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail']
        userpswd = request.form['userpswd']
        addUser = connection.execute("INSERT INTO users(username, email, pswd) VALUES (%s, %s, %s)", (username, useremail, userpswd))
        flash('Registration Successful. You can now Log In.', 'success')
        return redirect(url_for('login')) 
    else:
        return render_template('registration.html')


@app.route("/join", methods=['GET', 'POST'])
def join():
    if 'username' and 'userpswd' in session: 
        if request.method == 'POST':
            room = request.form['room'].lower()
            roompswd = request.form['roompswd']
            session['room'] = room
            checkRoom = connection.execute('SELECT room_name_number, room_pswd FROM room WHERE room_name_number=%s AND room_pswd=%s;', (room, roompswd))
            joinRoom = checkRoom.fetchone()

            if joinRoom: 
                return redirect(url_for('chat'))
            else:
                createRoom = connection.execute('INSERT INTO room(room_name_number, room_pswd) VALUES( %s, %s);', (room, roompswd))
                if createRoom:
                    flash('Chat Room Created.', 'success')
                    return render_template('room.html')
                else:
                    flash('Chat Room Not Created!', 'error')     
        else:
            return render_template('room.html')
    else:
        flash('You need to Log In first!', 'info')
        return redirect(url_for('login'))

@app.route("/chat")
def chat():
    if 'username' and 'userpswd' in session:
        username = session.get('username', '')
        room = session.get('room', '')
        return render_template('chat.html', name=username, room=room)
    else:
        flash('You need to Log In first!', 'info')
        return redirect(url_for('login'))
        

@app.route("/recovery", methods=['GET', 'POST'])
def recovery():
    if request.method == 'POST':
        useremail = request.form['useremail']
        newpswd = request.form['newpswd']
        email = connection.execute('SELECT email FROM users WHERE email=%s;', (useremail))
        checkEmail = email.fetchone()
        if checkEmail:          
            passRecovery = connection.execute('UPDATE users SET pswd=%s WHERE email=%s;', (newpswd, useremail))
            flash('New Password Updated.', 'success')
        else:
            flash('Email not found!', 'error')
    return render_template('recovery.html')

####### EVENTS #######

@socketio.on('joined', namespace='/chat')
def joined(message):
    #message sent to everyone when new user joins room
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    #message that users send to other users in the same room
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    #message sent to everyone when specific user leaves room
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)

if __name__ == "__main__":
    socketio.run(app)
    