from flask import Flask, render_template, redirect, url_for
import sqlite3
from utils import dbLibrary
import hashlib

story_app = Flask(__name__)

@story_app.route("/")
def root():
    return redirect(url_for('login'))

@story_app.route("/login",methods = ['POST','GET'])
def login():
    return render_template("login.html")


@story_app.route("/createAccount", methods = ['POST' , 'GET'])
def account():
    return render_template("createAccount.html")


@story_app.route("/home",methods = ['POST','GET'])
def homepage():
    return render_template("base.html")

@story_app.route("/create")
def create_story():
    return render_template("create.html")




if __name__ == "__main__":
    story_app.run(debug=True)

