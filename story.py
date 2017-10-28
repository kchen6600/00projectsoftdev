from flask import Flask, render_template, redirect, url_for,request, session, flash
import sqlite3
from utils import dbLibrary
import hashlib, uuid, os
from datetime import datetime




def hash_password(password):
    key = uuid.uuid4().hex
    return hashlib.sha256(key.encode() + password.encode()).hexdigest() + ':' + key

def check_password(hashed_password, user_password):
    password,key = hashed_password.split(":")
    return password == hashlib.sha256(key.encode() + user_password.encode()).hexdigest()


story_app = Flask(__name__)
story_app.secret_key = os.urandom(32)


#------------------------LOGIN----------------------------------
@story_app.route("/")
def root():
    return redirect(url_for('login'))

@story_app.route("/login", methods = ['POST' , 'GET'])
def login():
    return render_template("login.html")

@story_app.route("/authenticate",methods = ['POST','GET'])
def authenticate():
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)
    input_username = request.form['username']
    input_password = request.form['password']
    #print input_username
    #print input_password


    if input_username=='' or input_password=='' :
        flash("Please Fill In All Fields")
        return redirect(url_for('login'))

    hashed_passCursor = cursor.execute("SELECT password FROM accounts WHERE username = '" + input_username + "'")
    numPasses = 0 #should end up being 1 if all fields were filled

    for item in hashed_passCursor:
        numPasses += 1
        hashed_pass = item[0]
        print item[0]

    dbLibrary.closeFile(dbStories)

    if  numPasses == 0:
        flash ("User doesn't exist")
        return redirect(url_for('login'))

    elif check_password(hashed_pass, input_password):
        flash("Login Successful")
        session["username"] = input_username;#in order to keep track of user
        return redirect(url_for('home'))

    else:
        flash("Invalid Login Information")
        return redirect(url_for('login'))
#-------------------------------------------------------------------



#---------------CREATING AN ACCOUNT----------------------------------
@story_app.route("/account", methods = ['POST' , 'GET'])
def account():
    return render_template("account.html")

@story_app.route("/accountSubmit", methods = ['POST' , 'GET'])
def accountSubmit():
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)
    #print request.form
    username = request.form['username']
    password = request.form['password']

    if username == '' or password == '':
        dbLibrary.closeFile(dbStories)
        flash("Please Fill In All Fields")
        return redirect(url_for('account'))

    elif len(password)< 6:
        dbLibrary.closeFile(dbStories)
        flash("Password must have at least 6 characters")
        return redirect(url_for('account'))

    elif (' ' in username or ' ' in password):
        dbLibrary.closeFile(dbStories)
        flash("Username and Password cannot contain the space character")
        return redirect(url_for('account'))

    password = hash_password(password)
    sameUser = cursor.execute("SELECT username FROM accounts WHERE username = '" + username +"'")

    counter = 0 #should remain 0 if valid username since username needs to be unique
    for item in sameUser:
        counter += 1

    if counter == 0:
        dbLibrary.insertRow('accounts',['username', 'password'],[username, password],cursor)
        flash("Account Successfully Created")
        dbLibrary.commit(dbStories)
        dbLibrary.closeFile(dbStories)
        return redirect(url_for('login'))

    else:
        flash("Invalid: Username taken")
        dbLibrary.commit(dbStories)
        dbLibrary.closeFile(dbStories)
        return redirect(url_for('account'))

#-----------------------------------------------------------

@story_app.route("/home",methods = ['POST','GET'])
def home():
    return render_template("base.html") #I don't think its a good idea to put it in base, base shud never be rendered

#---------------CREATING STORY----------------------------

@story_app.route("/create")
def create_story():
    return render_template("create.html")

@story_app.route("/new_submit", methods = ['POST'])
def new_submit():

    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    print request.form
    title = request.form['title']
    print title
    body = request.form['body']

    #print 'stories/' + title + '.txt'
    #print os.getcwd()
    #Creating story file:
    story_obj = open('stories/' + title + '.txt', "w+")
    story_obj.write(body)

    datetime2 = str(datetime.now())[0:-7]#date and time (w/o milliseconds)
    print datetime2
    print session
    last_editor = session["username"]
    dbLibrary.insertRow('mainStories', ['title', 'timeLast', 'lastAdd', 'storyFile', 'lastEditor'], [title, datetime2, body, title + ".txt", last_editor], cursor)

    #print dbLibrary.display('mainStories', 'storyIDs', cursor)

    dbLibrary.insertRow('userStories', ['username', 'myAddition'], [last_editor, body], cursor)

    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    return redirect(url_for('home'))

#---------------------------------------------------------

#---------------CREATING STORY----------------------------

@story_app.route("/view")
def view_stories():
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    stories_raw = dbLibrary.display('mainStories', ['title', 'storyID', 'timeLast', 'storyFile', 'lastEditor'], cursor)
    #print stories_raw

    entries_list = stories_raw.split("\n")#list of entries
    header = entries_list.pop(0)


    split_entries_list = [line.split(",") for line in entries_list] #list of lists of entries
    split_entries_list.pop(-1)#delete empty field created by split

    your_split_entries = []

    for entry in split_entries_list:
        print "ENTRY"
        print entry
        #print entry[5]
        #print session["username"]
        if entry[5] == ' ' + session["username"]:#entry has space in front idk why
            your_split_entries.append(entry)#append only your additions

    print your_split_entries


    return render_template("view.html", story_list = your_split_entries)


@story_app.route("/view/<id>")#create route to view each story
def view_single(id):
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    command = "SELECT storyFile FROM mainStories WHERE storyID =" + str(id) + ";"#match story IDs
    cursor.execute(command)

    filename = cursor.fetchall()[0][0]#extract from tuple from list
    print "FILENAME"
    print filename
    readobj = open("stories/" + filename, "r")
    body = readobj.read()

    return render_template("view_single.html", title = filename[:-4], body = body)


#-------------------------------------------------------
@story_app.route("/edit")
def edit_stories():
    return "hi"


if __name__ == "__main__":
    story_app.run(debug=True)
