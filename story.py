from flask import Flask, render_template, redirect, url_for,request, session, flash
import sqlite3
from utils import dbLibrary
import hashlib, uuid



def hash_password(password):
    key = uuid.uuid4().hex
    return hashlib.sha256(key.encode() + password.encode()).hexdigest() + ':' + key

def check_password(hashed_password, user_password):
    password,key = hashed_password.split(":")
    return password == hashlib.sha256(key.encode() + user_password.encode()).hexdigest()


story_app = Flask(__name__)
story_app.secret_key = 'secret'


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

#---------------------------------------------------------------------    
    
@story_app.route("/home",methods = ['POST','GET'])
def home():
    return render_template("base.html") #I don't think its a good idea to put it in base, base shud never be rendered

@story_app.route("/create")
def create_story():
    return render_template("create.html")




if __name__ == "__main__":
    story_app.run(debug=True)

