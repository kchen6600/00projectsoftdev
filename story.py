from flask import Flask, render_template

story_app = Flask(__name__)


@story_app.route("/")
def login():
    return render_template("login.html")

@story_app.route("/home")
def homepage():
    return render_template("base.html")

@story_app.route("/create")
def create_story():
    return render_template("create.html")

if __name__ == "__main__":
    story_app.run(debug=True)
