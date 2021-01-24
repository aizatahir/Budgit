import os
import hashlib
from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import and_

from models import *


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
db.init_app(app)

# ENABLE SESSION
Session(app)

@app.route("/")
def index():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")





def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password_hash(password, hash):
    if hash_password(password) == hash:
        return True
    return False

if __name__ == '__main__':
    app.run(debug=True)