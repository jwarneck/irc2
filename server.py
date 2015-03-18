import os
import uuid
from flask import Flask, session, render_template, request, redirect, url_for
from flask.ext.socketio import SocketIO, emit
import psycopg2
import psycopg2.extras

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

gUsername = ""

socketio = SocketIO(app)

messages = [{'text': 'test', 'name': 'testing'}]
users = {}

firstConnect = False

def connectToDB():
                #Need DB namd and user/password...cerate an admin to login that can make all changes?
    connectionString = 'dbname=irc user=admin password=test host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect do database")



def updateRoster():
    names = []
    for user_id in  users:
        print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    emit('roster', names, broadcast=True)
    

@socketio.on('connect', namespace='/chat')
def test_connect():
    session['uuid']=uuid.uuid1()
    session['username']='Anonymous'
    print 'connected'
    
    users[session['uuid']]={'username':'Anonymous'}
    updateRoster()

    query2 = "SELECT * FROM messages ORDER BY(msg_id) DESC LIMIT 5"
    conn = connectToDB()
    displayMSG = conn.cursor()
    displayMSG.execute(query2)
    MSGS = []
    MSGS = displayMSG.fetchall()
    
#    print len(MSGS)
#    x = 0
#    while x < len(MSGS):
#        this = MSGS[x][2]
#        that = MSGS[x][1]
#        messages = [{'text': that, 'name': this}]
#        x += 1
#        emit('message', messages)
#        print "MESSAGES"
#        print messages
        
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
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    con = connectToDB()
    cur = con.cursor()
    if session['username'] is not 'Anonymous':
        messages.append(tmp)
        emit('message', tmp, broadcast=True)
        query = "insert into messages (content, poster) values ('"+message+"', '"+session['username']+"')"
        print query
        cur.execute(query)
        con.commit()
        
    else:
        print "Could not post message: Not logged in."
        emit('message', tmp, broadcast=False)
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
    print 'login '  + pw
    query = "SELECT * FROM users WHERE username = '"+gUsername+"' AND password = crypt('"+pw+"', password)"
    print query
    conn = connectToDB()
    logCur = conn.cursor()
    logCur.execute(query)
    results = logCur.fetchone()
    x = 0
    if results is not None:
        print "Logging in."
        session['username'] = gUsername
        


    else:
        print "Unable to log in. Check username and password."
        #this should also be reflected in the GUI
        session['username'] = 'Anonymous'
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
    
@app.route('/search', methods = ['GET', 'POST'])
def search():
    conn = connectToDB()
    cur1 = conn.cursor()
    cur2 = conn.cursor()
    
    if request.method == 'POST':
        print "Search function entered."
        searchTerm = request.form['term']
        
        uQuery = "select * from messages where poster = '"+searchTerm+"'"
        mQuery = "select * from messages where content like '%"+searchTerm+"%'"
        
        print uQuery
        print mQuery
        
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
        print userResults
        print contentResults
        print "Search done."
        
        notFound = ""
        if contentResults is not None:
            if userResults is not None:
                notFound = "Sorry, no results could be found."
    return render_template('search.html', contentResults = contentResults, userResults = userResults, notFound = notFound)
    
@app.route('/register', methods = ['GET', 'POST'])
def register():
    #all of the other shit that puts the info in the database goes here
    newAccountCreated = "";
    
    conn = connectToDB()
    curR = conn.cursor()
    curS = conn.cursor()

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
     