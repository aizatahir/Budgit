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
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    userName = request.form.get('userName')
    userEmail = request.form.get('userEmail')
    userPassword = hash_password(request.form.get('userPassword'))
    confirmPassword = request.form.get('confirmPassword')

    user = User(name=userName, email=userEmail, password=userPassword)

    if confirmPassword != '':
        # REGISTER
        if user.addUser() == -1:
            return render_template("index.html", alert=True, alertType="warning", alertMessage="You Are Already Registered")
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        session["userPassword"] = user.email
        return redirect("/home")
    else:
        # LOGIN
        if not user.validateCredentials():
            return render_template("index.html", alert=True, alertType="danger", alertMessage="You Are Not Registered")
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        return redirect("/home")




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