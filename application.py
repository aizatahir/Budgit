import os
import requests
import hashlib
from flask import Flask, session, render_template, request, redirect, jsonify
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
        return redirect(f"/home/{session['user_id']}")
    else:
        # LOGIN
        if not user.validateCredentials():
            return render_template("index.html", alert=True, alertType="danger", alertMessage="You Are Not Registered")
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        return redirect(f"/home/{session['user_id']}")

@app.route("/home/<string:user_id>")
def home(user_id):
    return render_template("home.html", user_id=user_id)



@app.route("/addExpense", methods=["POST"])
def addExpend():
    expenseName = request.form.get("expenseName")
    expensePrice = request.form.get("expensePrice")
    date = now
    time = getCurrentTime()

    try:
        expense = Expense(item_name=expenseName, item_price=expensePrice, date=date, time=time, user_id=session["user_id"])
    except KeyError:
        return redirect("/")
    expense.addExpense()
    # return render_template("home.html", alert=True, alertInfo={"type":"primary", "message": f"{expenseName} Has Been Added"})
    return redirect(f"/home/{session['user_id']}")





@app.route("/getExpenses", methods=["POST","GET"])
def getExpenses():
    expenseQuery = Expense.query.filter_by(user_id = session['user_id']).all()
    userExpenses = []

    for i, expense in enumerate(expenseQuery):
        userExpenses.append({
            "item_name": expense.item_name,
            "item_price": expense.item_price,
            "date": expense.date,
            "time": expense.time
        })

    return jsonify(userExpenses)



@app.route("/setExpenseLimit", methods=["POST", "GET"])
def setExpenseLimit():
    try:
        return render_template("set_expense.html", user_id=session['user_id'])
    except KeyError:
        return redirect("/")









def getCurrentTime():
    from datetime import datetime
    time = datetime.today().strftime("%H:%M %p")
    time = time.split(':')
    hour = int(time[0])
    minute = time[1]
    if hour <= 12:
        pass
    else:
        hour -= 12
    time = f"{hour}:{minute}"
    return time



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