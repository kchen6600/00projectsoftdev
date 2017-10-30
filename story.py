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
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@story_app.route("/login", methods = ['POST' , 'GET'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template("login.html")

@story_app.route("/authenticate",methods = ['POST','GET'])
def authenticate():
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)
    input_username = request.form['username']
    input_password = request.form['password']

    if input_username=='' or input_password=='' :
        flash("Please Fill In All Fields")
        return redirect(url_for('login'))

    if "'" in input_username or "'" in input_password:
        flash("Invalid Login Info")
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

@story_app.route("/home",methods = ['POST','GET'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("base.html",username = session['username'])

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

    elif (' ' in username or ' ' in password or "'" in username or "'" in password or '"' in username or '"' in password ):
        dbLibrary.closeFile(dbStories)
        flash("Username and Password cannot contain the space,single quote, or double quote character")
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



#---------------CREATING STORY----------------------------

@story_app.route("/create")
def create_story():
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    back = "/home"
    return render_template("create.html", back=back)

@story_app.route("/new_submit", methods = ['POST'])
def new_submit():
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    title = request.form['title']
    body = request.form['body']

    if title=='' or body =='':
        flash("Please fill out all fields before submitting")
        return redirect(url_for("create_story"))

    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    #dealing with the presence of single quotes and double quotes
    if "'" in body:
        body_list = list(body)
        for i in range(0, len(body_list)):
            if body_list[i] == "'":
                body_list[i] = '@single@'
        body = ("").join(body_list)

    if "'" in title:
        title_list = list(title)
        for i in range(0, len(title_list)):
            if title_list[i] == "'":
                title_list[i] = '@single@'
        title_tidy = ("").join(title_list)
    else:
        title_tidy = title
    
    #Creating story file:
    story_obj = open('stories/' + title + '.txt', "w+")
    story_obj.write(body)
    story_obj.close()

    datetime2 = str(datetime.now())[0:-7]#date and time (w/o milliseconds)
    last_editor = session["username"]
    dbLibrary.insertRow('mainStories', ['title', 'timeLast', 'lastAdd', 'storyFile', 'lastEditor'], [title_tidy, datetime2, body, title_tidy + ".txt", last_editor], cursor)

    storyid_cursor = cursor.execute('SELECT storyID FROM mainStories WHERE title = "' + title_tidy + '" AND timeLast ="' + datetime2 + '";')
    for item in storyid_cursor:
        #print item
        storyid = item[0]


    dbLibrary.insertRow('userStories', ['username', 'storyID','myAddition'], [last_editor, storyid, body], cursor)

    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    flash("You have successfully created a story! View " + title + " as it changes in 'View Your Stories'")
    return redirect(url_for('home'))

#---------------------------------------------------------

#---------------VIEWING STORY----------------------------

@story_app.route("/view")
def view_stories():
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    back = "/home"

    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    stories_raw = dbLibrary.display('mainStories', ['title', 'storyID', 'timeLast', 'storyFile', 'lastEditor'], cursor)


    entries_list = stories_raw.split("$|$\n")#list of entries
    header = entries_list.pop(0)

    print "RAW"
    print entries_list

    split_entries_list = [line.split("| ") for line in entries_list] #list of lists of entries
    split_entries_list.pop(-1)#delete empty field created by split

    your_split_entries = []

    #users_raw = dbLibrary.display('userStories', ['title', 'storyID', 'myAddition'], cursor)
    command = "SELECT username, storyID, myAddition FROM userStories"
    cursor.execute(command)

    print "FETCHALL"
    userdata = cursor.fetchall()
    print userdata

    for story in userdata:#maybe we can do this in not O(n^2)
        if story[0] == session["username"]:
            print story[0]
            print story[1]
            for entry in split_entries_list:
               #print entry
                if int(entry[1]) == story[1]:
                    print entry
                    your_split_entries.append(entry)#append only your additions


    print your_split_entries

    for entry in your_split_entries:
        title_list = (entry[0]).split("@single@")
        entry[0] = ("'").join(title_list)

    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    return render_template("view.html", username = session['username'],story_list = your_split_entries, back=back)


@story_app.route("/view/<id>")#create route to view each story
def view_single(id):
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    back = "/view"
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    command = "SELECT storyFile FROM mainStories WHERE storyID =" + str(id) + ";"#match story IDs
    cursor.execute(command)

    filename = cursor.fetchall()[0][0]#extract from tuple from list
    print "FILENAME"
    print filename

    title = filename[:-4]
    title_List = title.split("@single@")
    title = ("'").join(title_List)
    print title
    
    readobj = open("stories/" + str(title)+ ".txt", "r")
    body = readobj.read()

    #substituting all @single@ for single quotes
    body_List = body.split("@single@")
    body = ("'").join(body_List)

   
    
    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    return render_template("view_single.html", title = title, body = body, back=back)


#---------------------EDIT EXISTING STORY----------------------------------
@story_app.route("/edit")  #list of existing stories that user hasn't contributed to yet
def edit_stories():
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    back = "/home"
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    stories_raw = dbLibrary.display('mainStories', ['title', 'storyID', 'timeLast', 'storyFile', 'lastEditor'], cursor)

    print stories_raw

    entries_list = stories_raw.split("$|$\n")#list of entries
    header = entries_list.pop(0)

    print "RAW"
    print entries_list

    split_entries_list = [line.split("| ") for line in entries_list] #list of lists of entries
    split_entries_list.pop(-1)#delete empty field created by split

    available_split_entries = []

    command = "SELECT username, storyID, myAddition FROM userStories"
    cursor.execute(command)

    print "FETCHALL"
    userdata = cursor.fetchall()
    print userdata

    ids_edited = []
    for story in userdata:
        if story[0] == session["username"]:
            print story[0]
            print story[1]
            ids_edited.append(story[1])
            print "IDS EDITED"
            print ids_edited

    for story in userdata:#maybe we can do this in not O(n^2)
        if story[0] != session["username"]:
            #print story[0]
            #print story[1]
            for entry in split_entries_list:
                print entry
                if int(entry[1]) not in ids_edited and entry not in available_split_entries:
                    #print entry
                    available_split_entries.append(entry)#append only your additions

    print available_split_entries

    for entry in available_split_entries:
        title_list = (entry[0]).split("@single@")
        entry[0] = ("'").join(title_list)
    
    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    return render_template("edit.html", username = session['username'], story_list = available_split_entries, back=back)

@story_app.route("/edit/<id>")#takes you to a form to add to an existing story
def edit_single(id):
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))

    back = "/edit"
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    command = "SELECT * FROM mainStories WHERE storyID =" + str(id) + ";"#match story IDs

    #There should only be one row with a given storyID
    for row in cursor.execute(command):
        title = row[0]
        lastaddition = row[3]
        lastEditor = row[5]

    #substituting all @single@ for single quotes
    lastAdd_List = lastaddition.split("@single@")
    lastaddition = ("'").join(lastAdd_List)

    title_List = title.split("@single@")
    title = ("'").join(title_List)
    
    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    return render_template("edit_single.html", id = id, title = title, lastaddition = lastaddition, lastEditor= lastEditor, back = back)

@story_app.route("/edit_submit", methods = ['POST']) #adding edits to database
def edit_submit():
    if 'username' not in session:
        flash("Session timed out")
        return redirect(url_for('login'))


    title = request.form['title']
    id = request.form['id']
    newAdd = request.form['addition']
    last_editor = session["username"]

    if newAdd == '':
        flash("Please fill in all fields before submitting")
        return redirect('/edit/' +id)

    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)

    #dealing with the presence of single quotes and double quotes
    if "'" in newAdd:
        #print "\n\n\n\n\n\n\nHERE I AM\n\n\n\n\n\n\n"
        newAdd_list = list(newAdd)
        for i in range(0, len(newAdd_list)):
            if newAdd_list[i] == "'":
                newAdd_list[i] = '@single@'
        newAdd_tidy = ("").join(newAdd_list)
    else:
        newAdd_tidy = newAdd
    

    #Updating story file:
    story_obj = open('stories/' + title + '.txt', "a+")
    story_obj.write(newAdd)
    story_obj.close()

    #Updating the last addition and editor
    command = "UPDATE mainStories SET lastAdd = '" + newAdd_tidy + "' WHERE storyID =" + id + ";" #update lastAdd
    cursor.execute(command)
    command = "UPDATE mainStories SET lastEditor = '" + last_editor + "' WHERE storyID =" + id + ";" #update lastAdd
    cursor.execute(command)

    #Update the table of all the user additions
    dbLibrary.insertRow('userStories', ['username', 'storyID','myAddition'], [last_editor,id, newAdd_tidy], cursor)

    dbLibrary.commit(dbStories)
    dbLibrary.closeFile(dbStories)

    flash("Successfully contributed to " + title + "!")
    return redirect(url_for('home'))


@story_app.route('/logout',methods = ['GET'])
def logout():
    username = session.pop('username')
    msg = "Successfully logged out " + username
    flash(msg)
    return redirect(url_for('login'))

if __name__ == "__main__":
    story_app.run(debug=True)
