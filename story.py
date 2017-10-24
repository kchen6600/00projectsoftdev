from flask import Flask, render_template

story_app = Flask(__name__)


@story_app.route("/")
def login():
    return "awdawd"

@story_app.route("/home")
def homepage():
    return render_template("base.html")


if __name__ == "__main__":
    story_app.run(debug=True)
