import os
import requests
import hashlib
import smtplib
from email.message import EmailMessage

from flask import Flask, session, render_template, request, redirect, jsonify
from functools import wraps
from dotenv import load_dotenv
from flask_session import Session
from sqlalchemy import and_
from models import *

import datetime
from datetime import date, timedelta, tzinfo, datetime
from math import inf



# Check for environment variables
load_dotenv()
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

if not os.getenv("EMAIL_ADDRESS"):
    raise RuntimeError("EMAIL_ADDRESS is not set")

if not os.getenv("EMAIL_PASSWORD"):
    raise RuntimeError("EMAIL_PASSWORD is not set")

# EMAIL
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
# The maximum number of items the session stores
# before it starts deleting some, default 500
app.config['SESSION_FILE_THRESHOLD'] = 500
db.init_app(app)

# ENABLE SESSION
Session(app)
# session = {}

class EST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours = -5)

    def tzname(self, dt):
        return "EST"

    def dst(self, dt):
        return timedelta(0)

# INDEX
@app.route("/")
def index():
    return render_template("index.html")

# LOGIN REQUIRED
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")
    return wrap

# AUTHENTICATE
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
        session["logged_in"] = True
        return redirect(f"/home/{session['user_id']}")
    else:
        # LOGIN
        if not user.validateCredentials():
            return render_template("index.html", alert=True, alertType="danger", alertMessage="You Are Not Registered")
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        session["logged_in"] = True
        return redirect(f"/home/{session['user_id']}")

# HOME
@app.route("/home/<string:user_id>")
@login_required
def home(user_id):
    limitQuery = ExpenseLimit.query.filter_by(user_id=int(user_id)).first()
    try:
        expenseLimits = {
            "this-day": limitQuery.day,
            "this-week": limitQuery.week,
            "this-month": limitQuery.month,
            "this-year": limitQuery.year
        }
    except AttributeError:
        expenseLimits = {"this-day":None, "this-week":None, "this-month":None, "this-year":None}

    totalExpenses = {
        "this-day": getTotalExpense("this-day"),
        "this-week": getTotalExpense("this-week"),
        "this-month": getTotalExpense("this-month"),
        "this-year": getTotalExpense("this-year")
    }
    return render_template("home.html", user_id=user_id, user_expense_limits=str(expenseLimits), total_expenses=str(totalExpenses))


# GET USER INFO
@app.route("/getUserInfo", methods=["GET"])
@login_required
def getUserInfo():
    try:
        user = User.query.get(session['user_id'])
    except KeyError:
        return redirect("/")

    userInfo = {
        'id': user.id,
        'userName': user.name,
        'Email': user.email,
        'phoneNumber': user.phone_number
    }
    return jsonify(userInfo)

# UPDATE USER INFO
@app.route("/updateUserInfo/<string:userID>/<string:infoToUpdate>/<string:newInfo>", methods=["POST"])
@login_required
def updateUserInfo(userID, infoToUpdate, newInfo):
    user = User.query.get(userID)
    if infoToUpdate == 'userName':
        user.name = newInfo
        db.session.commit()
    elif infoToUpdate == 'userEmail':
        user.email = newInfo
        db.session.commit()
    elif infoToUpdate == 'userPhoneNumber':
        user.phone_number = newInfo
        db.session.commit()
    elif infoToUpdate == 'userPassword':
        storedHashOfUserPassword = user.password
        # CHECK IF THE CURRENT PASSWORD ENTERED MATCHES THE HASH STORED
        currentUserEnteredPassword = request.form.get('currentPassword')
        if check_password_hash(currentUserEnteredPassword, storedHashOfUserPassword):
            # UPDATE THE USER PASSWORD
            user.password = hash_password(newInfo)
            db.session.commit()
        else:
            return '-1'

    return ''

# ADD EXPENSE
@app.route("/addExpense", methods=["POST"])
@login_required
def addExpense():
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    expenseName = request.form.get("expenseName")
    expensePrice = request.form.get("expensePrice")
    date = now
    time = getCurrentTime()

    expense = Expense(item_name=expenseName, item_price=expensePrice, date=date, time=time, user_id=session["user_id"])
    expense.addExpense()
    # CHECK IF EXPENSE WENT OVER SPENDING LIMIT
    if not userWentOverSpendingLimit():
        return redirect(f"/home/{session['user_id']}")
    else:
        # SEND EMAIL TO USER INFORMING THEM THAT THEY WENT OVER THEIR SPENDING LIMIT
        limitsWentOver = userWentOverSpendingLimit()
        userEmailAddress = User.query.get(session['user_id']).email
        if userEmailAddress == None:
            return redirect(f"/home/{session['user_id']}")
        for limit in limitsWentOver:
            Message = f"You have just exceeded your expense limit for {limit} on the purchase: {expenseName} by ${limitsWentOver[limit]}\n\n" \
                      f"Item Price: ${expensePrice}\n" \
                      f"Expense Limit For {limit.title()}: ${getExpenseLimit(session['user_id'], limit.replace(' ', '-'))}\n" \
                      f"Total Expense For {limit.title()}: ${getTotalExpense(limit.replace(' ', '-'))}"

            sendEmail(userEmailAddress, 'Expense Limit Exceeded', Message)
        return redirect(f"/home/{session['user_id']}")


def userWentOverSpendingLimit():
    exceededLimits = {}

    userExpenseLimit = ExpenseLimit.query.filter_by(user_id=session['user_id']).first()
    userTotalExpenses = {
        'this-day': float(getTotalExpense('this-day')),
        'this-week': float(getTotalExpense('this-week')),
        'this-month': float(getTotalExpense('this-month')),
        'this-year': float(getTotalExpense('this-year'))
    }
    userExpenseLimits = {
        'this-day': userExpenseLimit.day,
        'this-week': userExpenseLimit.week,
        'this-month': userExpenseLimit.month,
        'this-year': userExpenseLimit.year
    }

    for item in userTotalExpenses:
        if userExpenseLimits[item] == None:
            continue
        if userTotalExpenses[item] > userExpenseLimits[item]:
            exceededLimits.update({item.replace('-', ' '): format(userTotalExpenses[item] - userExpenseLimits[item], ',.2f')})

    if exceededLimits == {}:
        return False
    else:
        return exceededLimits

# EDIT EXPENSE
@app.route("/editExpense/<string:item_id>/<string:newItemName>/<string:newItemPrice>", methods=["POST"])
@login_required
def editExpense(item_id, newItemName, newItemPrice):
    userID = session['user_id']

    userExpense = Expense.query.filter(and_(Expense.user_id == userID, Expense.id == item_id)).first()
    # ITEM NAME BEING EDITED
    if newItemPrice == "Empty" and newItemName != "":
        userExpense.item_name = newItemName
        db.session.commit()
    # ITEM PRICE BEING EDITED
    if newItemName == "Empty" and newItemPrice != "":
        userExpense.item_price = float(newItemPrice)
        db.session.commit()
    # BOTH NAME AND PRICE BEING EDITED
    if newItemName != "Empty" and newItemPrice != "Empty":
        userExpense.item_name = newItemName
        userExpense.item_price = float(newItemPrice)
        db.session.commit()
    return ""

# DELETE EXPENSE
@app.route("/deleteExpense/<string:item_id>", methods=["POST"])
@login_required
def deleteExpense(item_id):
    userExpense = Expense.query.get(item_id)
    db.session.delete(userExpense)
    db.session.commit()
    return ""

# GET EXPENSES
@app.route("/getExpenses/<string:period>", methods=["GET"])
@login_required
def getExpenses(period):
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    userExpenses = []
    if period == 'all-time':
        expenseQuery = Expense.query.filter_by(user_id = session['user_id']).all()
    elif period == 'this-day':
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date == now)).all()
    elif period == 'this-week':
        thisWeek = getThisWeekForQuery()
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.in_(thisWeek))).all()
    elif period == 'this-month':
        thisMonth, thisYear = now.split()[0], now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).all()
    elif period == 'this-year':
        thisYear = now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisYear}%"))).all()

    for i, expense in enumerate(expenseQuery):
        userExpenses.append({
            "id": expense.id,
            "item_name": expense.item_name,
            "item_price": expense.item_price,
            "date": expense.date,
            "time": expense.time
        })

    return jsonify(userExpenses)

# GET TOTAL EXPENSE
@app.route("/getTotalExpense/<string:period>", methods=["GET"])
@login_required
def getTotalExpense(period):
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    totalExpense = 0

    if period == 'all-time':
        expenseQuery = Expense.query.filter_by(user_id = session['user_id']).all()
    elif period == 'this-day':
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date == now)).all()
    elif period == 'this-week':
        thisWeek = getThisWeekForQuery()
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.in_(thisWeek))).all()
    elif period == 'this-month':
        thisMonth, thisYear = now.split()[0], now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).all()
    elif period == 'this-year':
        thisYear = now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisYear}%"))).all()


    for expense in expenseQuery:
        totalExpense += expense.item_price

    return str(format(totalExpense, ".2f"))

# SET EXPENSE LIMIT
@app.route("/setExpenseLimit/<string:limit>/<string:period>", methods=["POST", "GET"])
@login_required
def setExpenseLimit(limit, period):
    day = week = month = year = None
    if period == 'this-day':
        day = limit
    elif period == 'this-week':
        week = limit
    elif period == 'this-month':
        month = limit
    elif period == 'this-year':
        year = limit


    expenseLimit = ExpenseLimit(day=day,week=week,month=month,year=year, user_id=session['user_id'])


    expenseLimit.addExpenseLimit(limit, period)
    return ""

# GET EXPENSE LIMIT
@app.route("/getExpenseLimit/<string:userID>/<string:period>/", methods=["GET"])
@login_required
def getExpenseLimit(userID, period):
    userID = int(userID)
    try:
        if period == 'this-day':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().day
        elif period == 'this-week':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().week
        elif period == 'this-month':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().month
        elif period == 'this-year':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().year
    except AttributeError:
        return ""

    return str(limitQuery)

# ACCOUNT
@app.route("/account", methods=["GET"])
@login_required
def account():
    return render_template("account.html")


# SEND EMAIL
def sendEmail(To, Subject, Message):
    msg = EmailMessage()
    msg["Subject"] = Subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = To
    msg.set_content(Message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        # LOGIN TO THE MAIL SERVER
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # smtp.sendmail(SENDER, RECEIVER, msg)
        smtp.send_message(msg)

# LOG OUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route("/test")
def test():
    return render_template("test.html")




def getCurrentTime():
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

def getThisWeekForQuery():
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    todayDay = getCurrentDay(now)
    monthIndex = getMonthIndex(now)
    currentYear = getCurrentYear(now)
    startOfWeek = getStartOfWeek(currentYear, monthIndex, todayDay)

    if type(startOfWeek) == tuple:
        lastMonthIndex = startOfWeek[1]
        return getWeeks(currentYear, lastMonthIndex, startOfWeek[0])

    return getWeeks(currentYear, monthIndex, startOfWeek)

def getStartOfWeek(currentYear, monthIndex, todayDay, takeLastSunday=False):
    dayTolerance = {}
    foundPositiveTolerance = False
    if not takeLastSunday:
        for sunday in getSundays(currentYear, monthIndex):
            dayTolerance.update({sunday: (todayDay - sunday)})
    else:
        return (getSundays(currentYear, monthIndex - 1)[-1], monthIndex - 1)

    startOfWeek = None
    minTolerance = inf
    for t in dayTolerance:
        if dayTolerance[t] >= 0:
            foundPositiveTolerance = True
        if dayTolerance[t] < minTolerance and dayTolerance[t] >= 0:
            minTolerance = dayTolerance[t]
            startOfWeek = t

    if foundPositiveTolerance:
        return startOfWeek
    else:
        # WE ARE IN A NEW MONTH AND THE START OF THE WEEK IS STILL IN THE PREVIOUS MONTH
        return getStartOfWeek(currentYear, monthIndex, todayDay, takeLastSunday=True)

def getSundays(year, currentMonthIndex: int):
    Sundays = []
    def allsundays(year, currentMonthIndex: int):
       d = date(year, currentMonthIndex, 1)
       d += timedelta(days = 6 - d.weekday())
       while d.month == currentMonthIndex:
          yield d
          d += timedelta(days = 7)

    for d in allsundays(year, currentMonthIndex):
        Sundays.append(d.day)
    return Sundays

def getWeeks(year, monthIndex, day):
    import datetime
    numweeks = 1
    start_date = datetime.datetime(year=year, month=monthIndex, day=day)

    weeks = {}

    offset = datetime.timedelta(days=0)
    for week in range(numweeks):
        this_week = []
        for day in range(7):
            date = start_date + offset
            date = date.strftime("%B %d, %Y")
            this_week.append(date)
            offset += datetime.timedelta(days=1)
        weeks[week] = this_week

    return weeks[0]

def getCurrentDay(now):
    day = now.split()[1]
    return int(day.replace(',', ''))

def getCurrentYear(now):
    year = now.split()[2]
    return int(year)

def getMonthIndex(now):
    currentMonth = now.split()[0]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]

    for i, month in enumerate(months, 1):
        if month == currentMonth:
            return i
    return None

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password_hash(password, hash):
    if hash_password(password) == hash:
        return True
    return False

if __name__ == '__main__':
    app.run()