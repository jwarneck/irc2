import os
import uuid
from flask import Flask, session, render_template, request, redirect, url_for
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
import psycopg2
import psycopg2.extras

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.secret_key = os.urandom(24).encode('hex')

gUsername = ""

socketio = SocketIO(app)

messages = []
users = {}
rooms = ''


tempUsername = ""

firstConnect = False

def connectToDB():
                #Need DB namd and user/password...cerate an admin to login that can make all changes?
    connectionString = 'dbname=irc user=admin password=test host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect do database.")
        
def updateRooms():
    socketio.emit('rooms', session['room'])


def is_empty(any_structure):
    if any_structure:
        print('Structure is not empty.')
        return False
    else:
        print('Structure is empty.')
        return True

def updateRoster():
    names = []
    for user_id in  users:
        print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    print session['room']
    global rooms
    rooms = session['room']
    emit('roster', names, broadcast=True)
    

@socketio.on('connect', namespace='/chat')
def test_connect():
    session['uuid']=uuid.uuid1()
    session['username']='Anonymous'
    session['room']='General'
    join_room(session['room'])
    print 'connected'
    
    global rooms
    rooms = session['room']
    
    users[session['uuid']]={'username':'Anonymous'}
    updateRoster()
    updateRooms()

    query2 = "SELECT * FROM messages WHERE room = 'General' ORDER BY(msg_id) DESC LIMIT 5"
    conn = connectToDB()
    displayMSG = conn.cursor()
    displayMSG.execute(query2)
    MSGS = []
    MSGS = displayMSG.fetchall()
        
    print MSGS
    
    if firstConnect == False:
        x = 0
        while x < 5:
            print "Entering while loop."
            messages.append({'text': MSGS[x][1], 'name': MSGS[x][2]})
            x = x + 1
        global firstConnect
        firstConnect = True
        

    for message in messages:
        emit('message', message)
    print "Old messsages emitted."

@socketio.on('message', namespace='/chat')
def new_message(message):
    #tmp = {'text':message, 'name':'testName'}
    #checks to see if the message entred was a command
    global rooms
    rooms = session['room']
    if message.startswith('/'):
        if message.endswith('/'):
            print "transferring rooms sequence"
            newRoomName = message.lstrip('/')
            newRoomName = newRoomName.rstrip('/')
            #checks to see if the user is logged in
            if session['username'] is not 'Anonymous':
                print "user is logged in"
                #checks to see if user is subscribed to the room they are trying to go to
                subConn = connectToDB()
                subCur = subConn.cursor()
                userCur = subConn.cursor()
                roomCur = subConn.cursor()
                roomIDQuery = "select id from rooms where name ='"+newRoomName+"'"
                print roomIDQuery
                roomCur.execute(roomIDQuery)
                roomID = roomCur.fetchone()
                print type(roomID)
                #checks if the room actually exists
                if roomID is None:
                    notARoom = {'text':'Error: Room does not exist.', 'name':'System'}
                    emit('message', notARoom, broadcast = False)
                else:
                    #sets the session Room variable to the new room
                    #could be done more efficiently subqueries, but who cares? It's easier for me to keep track of this and we wont be expecting any kind of heavy load on the DB
                    userIDQuery = "select key_column from users where username = '"+session['username']+"'"
                    userCur.execute(userIDQuery)
                    userID = userCur.fetchone()
                    userID = userID[0]
                    print "userID ="+str(userID)+"."
                    #again, this could be done with a join and subqueries. But for learning purposes this is fine and easy to keep track of.
                    roomID = roomID[0]
                    subQuery = "select * from subs where userid = '"+str(userID)+"' AND roomid = '"+str(roomID)+"'"
                    subCur.execute(subQuery)
                    isSubscribed = subCur.fetchall()
                    print isSubscribed
                    print len(isSubscribed)
                    if len(isSubscribed) != 0:
                        
                        #user IS subbed to the chat channel
                        print "Joining room."
                        leave_room(session['room'])
                        session['room'] = newRoomName
                        join_room(session['room'])
                        roomJoined = {'text':'You have been connected to the new room '+newRoomName+'. Have fun!', 'name':'System'}
                        emit('message', roomJoined, broadcast = False)
                        print session['room']
                        print rooms
                        print 'Those should be the same.'
                        global tempUsername
                        tempUsername = session['username']
                    else:
                        #user is not subbed to the chat channel
                        notSubbed = {'text':'Sorry, you are not subscribed to that chat channel.', 'name':'System'}
                        emit('message', notSubbed, broadcast = False)
            else:
                notLoggedIn = {'text':'Please log in to change chat channels.', 'name':'System'}
                emit('message', notLoggedIn, broadcast = False)
        else:
            #this is lazy of me and isn't futureproofed or modular as it could be
            #but if the thing starts with a / but does not end with one
            #like a room change command would
            #it sees it as an unknown command
            #I can make this more modular if we need to use this kind of thing for other features as well later on
            print "unknown command"
            unknownCommand = {'text':'Sorry, that is an unknown command.', 'name':'System'}
            emit('message', unknownCommand, broadcast = False)
    else:
        tmp = {'text':message, 'name':users[session['uuid']]['username'], 'room':session['room']}
        print tmp['room']
        reject = {'text':'Sorry, could not send that messsage. Please log in.', 'name':'System'}
        con = connectToDB()
        cur = con.cursor()
        if session['username'] is not 'Anonymous':
            messages.append(tmp)
            emit('message', tmp, broadcast=True, room = session['room'])
            print rooms
            global tempUsername
            tempUsername = session['username']
            print session['username']
            query = "insert into messages (content, poster, room) values ('"+message+"', '"+session['username']+"', '"+session['room']+"')"
            print query
            cur.execute(query)
            con.commit()
        
        else:
            print "Could not post message: Not logged in."
            #emit('message', tmp, broadcast=False)
            emit('message', reject, broadcast = False)
            #these messages show up to the posting user but are not broadcast to others
            #we should eventually make changes in the UI to demonstrate this
        #emit('message', tmp, broadcast=True)
    
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'identify' + message
    global gUsername 
    gUsername = message
    users[session['uuid']]={'username':message}
    updateRoster()


@socketio.on('login', namespace='/chat')
def on_login(pw):
    reject = {'text':'Sorry, you could not be logged in. Please try again.', 'name':'System'}
    accept = {'text':'You have been logged in. Welcome.', 'name':'System'}
    print 'login '  + pw
    query = "SELECT * FROM users WHERE username = '"+gUsername+"' AND password = crypt('"+pw+"', password)"
    print query
    conn = connectToDB()
    logCur = conn.cursor()
    logCur.execute(query)
    results = logCur.fetchone()
    if results is not None:
        print "Logging in."
        session['username'] = gUsername
        emit('message', accept, broadcast = False)
        global tempUsername
        tempUsername = gUsername
        


    else:
        print "Unable to log in. Check username and password."
        #this should also be reflected in the GUI
        session['username'] = 'Anonymous'
        emit('message', reject, broadcast = False)
        global tempUsername
        tempUsername = 'Anonymous'
    #users[session['uuid']]={'username':message}
    #updateRoster()
    

    
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    print 'disconnect'
    if session['uuid'] in users:
        del users[session['uuid']]
        updateRoster()

@app.route('/')
def hello_world():
    print 'in hello world'
    return app.send_static_file('index.html')
    return 'Hello World!'
    
@app.route('/newroom')
def newroom():
        
    return render_template('newroom.html')
    
@app.route('/newroommade', methods = ['GET', 'POST'])
def newroommade():
    conn = connectToDB()
    hueue = ""
    if request.method == 'POST':
        print "Name entered."
        roomName = request.form['roomname']
        print roomName
        alreadyExistsQuery = "select id from rooms where name = '"+roomName+"'"
        print alreadyExistsQuery
        alreadyCur = conn.cursor()
        alreadyCur.execute(alreadyExistsQuery)
        print "Query Executed."
        resultID = alreadyCur.fetchone()
        print resultID
        if is_empty(resultID):
            insertQuery = "insert into rooms (name) values ('"+roomName+"')"
            print insertQuery
            newCur = conn.cursor()
            newCur.execute(insertQuery)
            conn.commit()
            print "Room created."
            hueue = "Room created."
        else:
            hueue = "A room with that name already exists."
    return render_template('newroommade.html', hueue = hueue)
    
@app.route('/search', methods = ['GET', 'POST'])
def search():
    
    conn = connectToDB()
    cur1 = conn.cursor()
    cur2 = conn.cursor()
    curUserName = conn.cursor()
    curSub = conn.cursor()
    
    searchingUser = tempUsername
    
    if request.method == 'POST':
        print "Search function entered."
        searchTerm = request.form['term']
        
        uQuery = "select * from messages where poster = '"+searchTerm+"'"
        mQuery = "select * from messages where content like '%"+searchTerm+"%'"
        
        print uQuery
        print mQuery
        
        if tempUsername is not 'Anonymous':
            usernameQuery = "select key_column from users where username = '"+tempUsername+"'"
            print usernameQuery
            curUserName.execute(usernameQuery)
            userID = curUserName.fetchone()
            userID = userID[0]
            print userID
            sQuery = "select distinct rooms.name from subs inner join rooms on rooms.id = subs.roomid where subs.userid = '"+str(userID)+"'"
            print sQuery
            curSub.execute(sQuery)
            subs = curSub.fetchall()
            
            print subs
            for sub in subs:
                print sub
            print type(subs)
        cur1.execute(uQuery)
        try:
            userResults = cur1.fetchall()
        except:
            userResults = []
        cur2.execute(mQuery)
        try:
            contentResults = cur2.fetchall()
        except:
            contentResults = []
        newContentResults = []
        newUserResults = []
        for result in contentResults:
            print result[3]
            for sub in subs:
                for thing in sub:
                    print thing
                    if thing == result[3]:
                        print result
                        newContentResults.append(result)
                        print "Result omitted."
        for result in userResults:
            for sub in subs:
                if sub[0] == result[3]:
                    newUserResults.append(result)
                    print "Result omitted."
        print newUserResults
        print newContentResults
        print "Search done."
        
        notFound = ""
        if contentResults is None:
            if userResults is None:
                notFound = "Sorry, no results could be found."
    return render_template('search.html', contentResults = newContentResults, userResults = newUserResults, notFound = notFound, subs = subs)
    
@app.route('/subscribe')
def subscribe():
    
    return render_template('subscribe.html')
    
@app.route('/subbed', methods = ['GET', 'POST'])
def subbed():
    if request.method == 'POST':
        conn = connectToDB()
        userQuery = "select key_column from users where username = '"+request.form['username']+"'"
        roomQuery = "select id from rooms where name = '"+request.form['roomname']+"'"
        print userQuery
        print roomQuery
        userCur = conn.cursor()
        roomCur = conn.cursor()
        userCur.execute(userQuery)
        roomCur.execute(roomQuery)
        print "queries executed."
        user = userCur.fetchone()
        room = roomCur.fetchone()
        print user
        print room
        if is_empty(user):
            qwert = "Couldn't find that username or room name."
        elif is_empty(room):
            qwert = "Couldn't find that username or room name."
        else:
            user = int(user[0])
            room = int(room[0])
            print user
            print room
            insertQ = "insert into subs (userid, roomid) values ("+str(user)+", "+str(room)+")"
            print insertQ
            insertCur = conn.cursor()
            insertCur.execute(insertQ)
            conn.commit()
            qwert = "Subscription made."
    return render_template('subbed.html', qwert = qwert)
    
@app.route('/register', methods = ['GET', 'POST'])
def register():
    #all of the other shit that puts the info in the database goes here
    newAccountCreated = "";
    
    conn = connectToDB()
    curR = conn.cursor()
    curS = conn.cursor()
    curK = conn.cursor()
    curD = conn.cursor()

    if request.method == 'POST':
     
        username = request.form['username']
        password = request.form['pw']
        
        searchQuery = "select * from users where username = '"+username+"'"
        curS.execute(searchQuery)
        print "Search Query executed."
        result = curS.fetchone()
        
        if result is not None:
            newAccountCreated = "Sorry, an account with that name already exists."
        else:
               
            query = "INSERT into users (username, password) VALUES ('"+username+"', crypt('"+password+"', gen_salt('bf')))"
            print query
            curR.execute(query)
            print "Query executed."
            conn.commit()
            print "Query committed."
            newAccountCreated = "Account Created";
            query = "SELECT key_column from users where username = '"+username+"'"
            print query
            curK.execute(query)
            print "Execute ID fetch query."
            ID = curK.fetchone()
            print "fetched ID"
            if ID is not None:
                print ID
            else:
                print "Didn't fetch."
            print "stripping"
            ID = ID[0]
            print ID
            newUserID = ID
            newUserID = str(newUserID)
            print "Making new query."
            newQuery = "INSERT into subs (userid, roomid) VALUES ("+newUserID+", 1)"
            print newQuery
            curD.execute(newQuery)
            conn.commit()
            print "Subscription to General established."
        #if result is not None:
        #    newAccountCreated = "Sorry, an account with that name already exists."
    
    return render_template('register.html', newAccountCreated = newAccountCreated)
    



@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
     