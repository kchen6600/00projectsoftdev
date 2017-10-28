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


@story_app.route("/")
def root():
    return redirect(url_for('login'))

@story_app.route("/login",methods = ['POST','GET'])
def login():
    return render_template("login.html")

@story_app.route("/account", methods = ['POST' , 'GET'])
def account():
    return render_template("account.html")

@story_app.route("/accountSubmit", methods = ['POST' , 'GET'])
def accountSubmit():
    dbStories = dbLibrary.openDb("data/stories.db")
    cursor = dbLibrary.createCursor(dbStories)
    #print request.form
    username = request.form['username']
    password = hash_password(request.form['password'])
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

    
    
@story_app.route("/home",methods = ['POST','GET'])
def homepage():
    return render_template("base.html")

@story_app.route("/create")
def create_story():
    return render_template("create.html")




if __name__ == "__main__":
    story_app.run(debug=True)

