import os
import requests
import hashlib
import smtplib
import json
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
app.config['TESTING'] = False
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

from Classes import EST
from Methods import getIntegerDayForNow, getMostRecentDate




# LOGIN REQUIRED
if app.config['TESTING'] == False:
    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                if session['logged_in'] == True:
                    return f(*args, **kwargs)
                else:
                    return redirect('/')
            else:
                return redirect('/')
        return wrap
else:
    session = {}

    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            return f(*args, **kwargs)
        return wrap


# INDEX
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/test2', methods=['GET'])
def newTest():
    return redirect('/test')
# AUTHENTICATE
@app.route("/authenticate/<string:userId>/<string:userName>/<string:userEmail>/<string:userPassword>/<string:confirmPassword>", methods=["POST"])
def authenticate(userId, userName, userEmail, userPassword, confirmPassword):
    if userId == 'null':
        userId = None
    if userEmail == 'null':
        userEmail = None
    if confirmPassword == 'null':
        confirmPassword = None

    userPassword = hash_password(userPassword)

    if userId != None:
        user = User(id=int(userId), name=userName, email=userEmail, password=userPassword)
    else:
        user = User(name=userName, email=userEmail, password=userPassword)
    # print(f'ConfirmPassword: {confirmPassword}')

    if confirmPassword != None and userEmail != None:
        # REGISTER
        if user.addUser() == -1:
            dataRouteToReturn = {
                'message': 'User Already Registered',
                'route': None
            }
            return jsonify(dataRouteToReturn)
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        session["logged_in"] = True

        dataRouteToReturn = {
            'message': 'Register User',
            'route': f"/home/{session['user_id']}"
        }
        return jsonify(dataRouteToReturn)

    else:
        # LOGIN
        if not user.validateCredentials():
            # return render_template("index.html", alert=True, alertType="danger", alertMessage="You Are Not Registered")
            dataRouteToReturn = {
                'message': 'User Not Registered',
                'route': None
            }
            return jsonify(dataRouteToReturn)
        session["user_id"] = User.query.filter(and_(User.name == userName, User.password == userPassword)).first().id
        session["userName"] = user.name
        session["logged_in"] = True
        # return redirect(f"/home/{session['user_id']}")
        dataRouteToReturn = {
            'message': 'Login User',
            'route': f"/home/{session['user_id']}"
        }
        return jsonify(dataRouteToReturn)

# HOME
@app.route("/home/<string:user_id>")
@login_required
def home(user_id):
    # print(f"User ID: {user_id}")
    limitQuery = ExpenseLimit.query.filter_by(user_id=int(user_id)).first()
    # try:
    #     expenseLimits = {
    #         "this-day": limitQuery.day,
    #         "this-week": limitQuery.week,
    #         "this-month": limitQuery.month,
    #         "this-year": limitQuery.year
    #     }
    # except AttributeError:
    #     expenseLimits = {"this-day":None, "this-week":None, "this-month":None, "this-year":None}
    #
    # totalExpenses = {
    #     "this-day": getTotalExpense("this-day"),
    #     "this-week": getTotalExpense("this-week"),
    #     "this-month": getTotalExpense("this-month"),
    #     "this-year": getTotalExpense("this-year")
    # }
    return render_template("home.html", user_id=user_id)


# GET USER INFO
@app.route("/getUserInfo", methods=["GET"])
@login_required
def getUserInfo():
    user = User.query.get(session['user_id'])


    userInfo = {
        'id': user.id,
        'userName': user.name,
        'Email': user.email,
        'phoneNumber': user.phone_number,
        'Password': user.password
    }
    return jsonify(userInfo)

# UPDATE USER INFO
@app.route("/updateUserInfo/<string:userID>/<string:infoToUpdate>/<string:newInfo>/<string:prevInfo>", methods=["POST"])
@login_required
def updateUserInfo(userID, infoToUpdate, newInfo, prevInfo):
    user = User.query.get(userID)
    if infoToUpdate == 'userName':
        # CHECK IF THE UPDATED NAME IS THE SAME AS THE NAME ALREADY STORED
        if newInfo == prevInfo:
            return '-1'
        user.name = newInfo
        db.session.commit()
    elif infoToUpdate == 'userEmail':
        # CHECK IF THE UPDATED EMAIL IS THE SAME AS THE EMAIL ALREADY STORED
        if newInfo == prevInfo:
            return '-1'
        user.email = newInfo
        db.session.commit()
    elif infoToUpdate == 'userPhoneNumber':
        # CHECK IF THE UPDATED PHONE NUMBER IS THE SAME AS THE PHONE NUMBER ALREADY STORED
        if newInfo == prevInfo:
            return '-1'
        user.phone_number = newInfo
        db.session.commit()
    elif infoToUpdate == 'userPassword':
        storedHashOfUserPassword = user.password
        # CHECK IF THE CURRENT PASSWORD ENTERED MATCHES THE HASH STORED
        currentUserEnteredPassword = prevInfo
        # print(currentUserEnteredPassword)
        if check_password_hash(currentUserEnteredPassword, storedHashOfUserPassword):
            # UPDATE THE USER PASSWORD
            user.password = hash_password(newInfo)
            db.session.commit()
        else:
            return '-1'

    return 'Update Successful'

# ADD EXPENSE
@app.route("/addExpense/<string:expenseData>", methods=["POST"])
@login_required
def addExpense(expenseData):
    expenseData = json.loads(expenseData)
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    expenseName = expenseData['expenseName']
    expensePrice = expenseData['expensePrice']
    autoSendEmail = expenseData['auto-send-email']

    try:
        date = expenseData['expenseDate']
    except KeyError:
        date = now

    time = getCurrentTime()

    expense = Expense(item_name=expenseName, item_price=expensePrice, date=date, time=time, user_id=session["user_id"])
    expense.addExpense()

    # CHECK IF EXPENSE WENT OVER SPENDING LIMIT
    if not userWentOverSpendingLimit():
        return 'Expense Added, Spending Limit Not Exceeded'
        # return redirect(f"/home/{session['user_id']}")
    else:
        if autoSendEmail == 'enabled' and autoSendEmail != None:
            # SEND EMAIL TO USER INFORMING THEM THAT THEY WENT OVER THEIR SPENDING LIMIT
            limitsWentOver = userWentOverSpendingLimit()
            userEmailAddress = User.query.get(session['user_id']).email
            if userEmailAddress == None:
                return 'Expense Added, Spending Limit Exceeded'
                # return redirect(f"/home/{session['user_id']}")
            for limit in limitsWentOver:
                Message = f"You have just exceeded your expense limit for {limit} by ${limitsWentOver[limit]} on the purchase: {expenseName}\n\n" \
                          f"Item Price: ${expensePrice}\n" \
                          f"Expense Limit For {limit.title()}: ${getExpenseLimit(limit.replace(' ', '-'))}\n" \
                          f"Total Expense For {limit.title()}: ${getTotalExpense(limit.replace(' ', '-'))}"

                sendEmail(userEmailAddress, 'Expense Limit Exceeded', Message)
            return 'Expense Added, Spending Limit Exceeded'
            # return redirect(f"/home/{session['user_id']}")
        else:
            return 'Expense Added, Spending Limit Exceeded'
            # return redirect(f"/home/{session['user_id']}")

# ADD SCHEDULE EXPENSE
@app.route("/scheduleExpense/<string:expenseName>/<string:expensePrice>/<string:startDate>/<string:frequency>", methods=["POST", "GET"])
@login_required
def addScheduleExpense(expenseName, expensePrice, startDate, frequency):
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    # CONVERT DATE FROM mm-dd-yyyy TO 'now' FORMAT
    startDate = convertStartDate(startDate, 'mm-dd-yyyy', 'now-format')
    now = getIntegerDayForNow(now)
    # EXPENSE IS TO BE ADDED TODAY
    if startDate == now:
        now = Date(now)
        expenseData = {
            'expenseName': expenseName,
            'expensePrice': expensePrice,
            'auto-send-email': None
        }
        addExpense(json.dumps(expenseData))

        nextDue = str(now.addTime('day', 1))
        SE = ScheduledExpense(expense_name=expenseName, expense_price=expensePrice, start_date=startDate, next_due=nextDue, frequency=frequency, user_id=session['user_id'])
        SE.addScheduledExpense()

    else:
        SE = ScheduledExpense(expense_name=expenseName, expense_price=expensePrice, start_date=startDate, next_due=startDate, frequency=frequency, user_id=session['user_id'])
        SE.addScheduledExpense()

    return 'Expense Successfully Scheduled'



# USER WENT OVER SPENDING LIMIT
def userWentOverSpendingLimit():
    exceededLimits = {}

    userExpenseLimit = ExpenseLimit.query.filter_by(user_id=session['user_id']).first()
    if userExpenseLimit == None:
        return False
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
@app.route("/editExpense/<string:item_id>/<string:newExpenseName>/<string:newExpensePrice>", methods=["POST"])
@login_required
def editExpense(item_id, newExpenseName, newExpensePrice):
    userID = session['user_id']

    userExpense = Expense.query.filter(and_(Expense.user_id == userID, Expense.id == item_id)).first()
    # ITEM NAME BEING EDITED
    if newExpensePrice == "Empty" and newExpenseName != "Empty":
        userExpense.item_name = newExpenseName
        db.session.commit()
        return 'Expense Name Successfully Changed'
    # ITEM PRICE BEING EDITED
    elif newExpenseName == "Empty" and newExpensePrice != "Empty":
        userExpense.item_price = float(newExpensePrice)
        db.session.commit()
        return 'Expense Price Successfully Changed'
    # BOTH NAME AND PRICE BEING EDITED
    elif newExpenseName != "Empty" and newExpensePrice != "Empty":
        userExpense.item_name = newExpenseName
        userExpense.item_price = float(newExpensePrice)
        db.session.commit()
        return 'Expense Name and Price Successfully Changed'
    else:
        return 'No Changes Made'

# EDIT SCHEDULE EXPENSE
@app.route("/editScheduleExpense/<string:newExpenseInfo>", methods=["POST"])
@login_required
def editScheduleExpense(newExpenseInfo):
    newExpenseInfo = json.loads(newExpenseInfo)

    for expense in newExpenseInfo:
        scheduleExpenseToEdit = ScheduledExpense.query.get(expense['id'])

        scheduleExpenseToEdit.expense_name = expense['newName']
        scheduleExpenseToEdit.expense_price = expense['newPrice']
        scheduleExpenseToEdit.frequency = expense['newFrequency']

        db.session.commit()


    return 'done'

# DELETE EXPENSE
@app.route("/deleteExpense/<expense_id>", methods=["POST"])
@login_required
def deleteExpense(expense_id):
    userExpense = Expense.query.get(expense_id)
    if userExpense == None:
        return 'Expense Not Found'
    db.session.delete(userExpense)
    db.session.commit()
    return 'Expense Successfully Deleted'


# DELETE SCHEDULE EXPENSE
@app.route("/deleteScheduleExpense/<string:schedule_expense_id>", methods=["POST"])
@login_required
def deleteScheduleExpense(schedule_expense_id):
    scheduleExpenseToDelete = ScheduledExpense.query.get(int(schedule_expense_id))
    db.session.delete(scheduleExpenseToDelete)
    db.session.commit()

    return 'done'

# GET EXPENSES
@app.route("/getExpenses/<string:period>/<sortBy>/<string:order>", methods=["GET"])
@login_required
def getExpenses(period, sortBy, order):
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    userExpenses = []
    if period == 'all-time':
        if order == 'asc':
            # Hard Coded Way: expenseQuery = Expense.query.order_by(Expense.item_name).filter_by(user_id=session['user_id']).all()
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter_by(user_id = session['user_id']).all()
        else:
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy).desc()).filter_by(user_id=session['user_id']).all()
    elif period == 'this-day':
        if order == 'asc':
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter(and_(Expense.user_id == session['user_id'], Expense.date == now)).all()
        else:
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy).desc()).filter(and_(Expense.user_id == session['user_id'], Expense.date == now)).all()
    elif period == 'this-week':
        thisWeek = getThisWeekForQuery(now)
        if order == 'asc':
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter(and_(Expense.user_id == session['user_id'], Expense.date.in_(thisWeek))).all()
        else:
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy).desc()).filter(and_(Expense.user_id == session['user_id'], Expense.date.in_(thisWeek))).all()
    elif period == 'this-month':
        thisMonth, thisYear = now.split()[0], now.split()[2]
        if order == 'asc':
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).all()
        else:
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy).desc()).filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).all()
    elif period == 'this-year':
        thisYear = now.split()[2]
        if order == 'asc':
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisYear}%"))).all()
        else:
            expenseQuery = Expense.query.order_by(getattr(Expense, sortBy).desc()).filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisYear}%"))).all()



    for i, expense in enumerate(expenseQuery):
        userExpenses.append({
            "id": expense.id,
            "item_name": expense.item_name,
            "item_price": expense.item_price,
            "date": expense.date,
            "time": expense.time
        })

    return jsonify(userExpenses)

# GET SCHEDULE EXPENSES
@app.route("/getUserScheduleExpenses/<string:sortBy>/<string:order>", methods=['GET'])
@login_required
def getUserScheduleExpenses(sortBy, order):
    if order == 'asc':
        # expenseQuery = Expense.query.order_by(getattr(Expense, sortBy)).filter_by(user_id=session['user_id']).all()

        userScheduleExpenses = ScheduledExpense.query.order_by(getattr(ScheduledExpense, sortBy)).filter_by(user_id=session['user_id']).all()
        # userScheduleExpenses = ScheduledExpense.query.filter_by(user_id=session['user_id']).all()
    else:
        userScheduleExpenses = ScheduledExpense.query.order_by(getattr(ScheduledExpense, sortBy).desc()).filter_by(user_id=session['user_id']).all()

    allUserScheduleExpenses = []

    for schedule_expense in userScheduleExpenses:
        expenseDates = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.item_name == schedule_expense.expense_name)).all()

        # GET LAST DUE
        if expenseDates != []:
            allExpenseDates = [expense.date for expense in expenseDates]
            lastDue = str(getMostRecentDate(allExpenseDates))
        else:
            lastDue = 'Never'

        allUserScheduleExpenses.append({
            'id': schedule_expense.id,
            'expense_name': schedule_expense.expense_name,
            'expense_price': schedule_expense.expense_price,
            'start_date': schedule_expense.start_date,
            'last_due': lastDue,
            'next_due': schedule_expense.next_due,
            'frequency': schedule_expense.frequency,
            'user_id': schedule_expense.user_id
        })

    return jsonify(allUserScheduleExpenses)

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
        thisWeek = getThisWeekForQuery(now)
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.in_(thisWeek))).all()
    elif period == 'this-month':
        thisMonth, thisYear = now.split()[0], now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).all()
    elif period == 'this-year':
        thisYear = now.split()[2]
        expenseQuery = Expense.query.filter(and_(Expense.user_id == session['user_id'], Expense.date.like(f"%{thisYear}%"))).all()
    elif period == 'all-expenses-JSON':
        allTotalExpenses = {
            'this-day': getTotalExpense('this-day'),
            'this-week': getTotalExpense('this-week'),
            'this-month': getTotalExpense('this-month'),
            'this-year': getTotalExpense('this-year'),
        }
        return jsonify(allTotalExpenses)


    for expense in expenseQuery:
        totalExpense += expense.item_price

    return str(format(totalExpense, ".2f"))

# SET EXPENSE LIMIT
@app.route("/setExpenseLimit/<string:limit>/<string:period>", methods=["POST"])
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
    return 'Expense Limit Successfully Set'

# GET EXPENSE LIMIT
@app.route("/getExpenseLimit/<string:period>", methods=["GET"])
@login_required
def getExpenseLimit(period):
    userID = int(session['user_id'])
    try:
        if period == 'this-day':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().day
        elif period == 'this-week':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().week
        elif period == 'this-month':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().month
        elif period == 'this-year':
            limitQuery = ExpenseLimit.query.filter_by(user_id = userID).first().year
        elif period == 'all-limits-json':
            limitQuery = ExpenseLimit.query.filter_by(user_id= userID).first()
            try:
                expenseLimits = {
                    "this-day": limitQuery.day,
                    "this-week": limitQuery.week,
                    "this-month": limitQuery.month,
                    "this-year": limitQuery.year
                }
            except AttributeError:
                expenseLimits = {"this-day": None, "this-week": None, "this-month": None, "this-year": None}
            return jsonify(expenseLimits)
        else:
            return 'Invalid period'
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



def convertStartDate(startDate, currentFormat, newFormat):
    SupportedFormats = ['mm-dd-yyyy', 'dd-mm-yyyy', 'mm/dd/yyyy', 'dd/mm/yyyy', 'now-format']
    if currentFormat not in SupportedFormats:
        raise ValueError(f'{currentFormat} is not supported as currentFormat')
    if newFormat not in SupportedFormats:
        raise ValueError(f'{newFormat} is not supported as newFormat')

    monthLookup = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
                   10: 'October', 11: 'November', 12: 'December'}
    if currentFormat == 'mm-dd-yyyy':
        if newFormat == 'now-format':
            try:
                day, month, year = int(startDate.split('-')[1]), monthLookup[int(startDate.split('-')[0])], int(startDate.split('-')[2])
            except ValueError:
                raise ValueError('startDate was not formatted correctly')

            newFormat = f'{month} {day}, {year}'
            return newFormat


def getThisWeekForQuery(now):
    """ THIS FUNCTION RETURNS AN ARRAY OF ALL THE DATES IN THE CURRENT WEEK """

    if not isValidDate(now):
        raise ValueError('date is invalid')

    todayDay = getCurrentDay(now)
    monthIndex = getMonthIndex(now)
    currentYear = getCurrentYear(now)
    startOfWeek = getStartOfWeek(currentYear, monthIndex, todayDay)

    if type(startOfWeek) == tuple:
        """
        THE START OF THE WEEK IS IN THE PREV MONTH
        startOfWeek = (Last sunday in prev_month, prev_month_index)
        """
        lastSunday = startOfWeek[0] # THE LAST SUNDAY IN THE PREV MONTH IS THE START OF THE WEEK FOR THE REQUESTED MONTH
        lastMonthIndex = startOfWeek[1]
        return getWeek(currentYear, lastMonthIndex, lastSunday)

    return getWeek(currentYear, monthIndex, startOfWeek)

def getStartOfWeek(year, monthIndex, todayDay, takeLastSunday=False):
    """
    dayTolerance is a dict with key:(a sunday in the month) and value:(how far that sunday is from the current day).
    THE IDEA IS THAT WE POPULATE THIS DICT WITH ALL THE TOLERANCES IN THE MONTH AND WE TAKE THE SUNDAY WITH THE MIN +TOLERANCE.
    THE SUNDAY WITH THE MIN TOLERANCE IS THE SUNDAY THAT IS CLOSEST TO THE CURRENT DAY(Which means it is the start of the week).
    IN THE CASE WHERE A TOLERANCE IS < 0, THIS MEANS THAT PARTICULAR SUNDAY HAS NOT BEEN REACH AS YET
    IN THE CASE WHERE ALL THE TOLERANCES ARE < 0, WE TAKE THE LAST SUNDAY IN THE PREV MONTH. WHEN ALL THE TOLERANCES ARE < 0,
    THIS MEANS THAT THE START OF THE WEEK FOR THE REQUESTED MONTH IS STILL IN THE PREV MONTH. FOR EXAMPLE: LOOK ON THE
    CALENDAR ON THE DATE: September 2, 2021, THE START OF THAT WEEK IS August 29, 2021 (ITS IN THE PRV MONTH)
    """
    if todayDay not in [i for i in range(1, 32)]:
        raise ValueError('todayDay is out of range')

    dayTolerance = {}
    foundPositiveTolerance = False
    if not takeLastSunday:
        for sunday in getSundays(year, monthIndex):
            dayTolerance.update({sunday: (todayDay - sunday)})
    else:
        """
        IF WE ARE TAKING THE LAST SUNDAY THAT MEANS THE START OF THE WEEK IS IN THE PREV MONTH
        Return (last_sunday_of_prev_month, month_index_of_prev month)
        """
        return (getSundays(year, monthIndex - 1)[-1], monthIndex - 1)

    startOfWeek = None
    # GET THE MINIMUM POSITIVE DAY TOLERANCE
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
        return getStartOfWeek(year, monthIndex, todayDay, takeLastSunday=True)

def getSundays(year, monthIndex: int):
    """ THIS FUNCTIONS RETURNS AN ARRAY OF ALL THE SUNDAY DAYS IN THE REQUESTED MONTH """

    if monthIndex not in [i for i in range(1, 13)]:
        raise ValueError('monthIndex is out of range')

    Sundays = []
    def allsundays(year, currentMonthIndex: int):
        """
        THIS FUNCTION ESSENTIALLY RETURNS AN ARRAY OF DATE OBJECTS THAT START AT THE BEGINNING OF THE MONTH AND += 7 days.
        SO THIS GENERATES ALL THE SUNDAYS IN THE MONTH
        """
        try:
            d = date(year, currentMonthIndex, 1)
        except ValueError:
            raise ValueError('year is out of range')
        d += timedelta(days = 6 - d.weekday())
        while d.month == currentMonthIndex:
            yield d
            d += timedelta(days = 7)

    for d in allsundays(year, monthIndex):
        """ APPEND ALL THE SUNDAY DAYS THAT WERE RETURNED THE THE Sundays ARRAY """
        Sundays.append(d.day)
    return Sundays

def getWeek(year, monthIndex, startDay):
    """
    THIS FUNCTION RETURNS AN ARRAY OF ALL THE DATES IN A WEEK, WHEN GIVEN THE INITIAL/START DAY.
    getWeeks(2021 3, 21) --> [March 21, 2021, March 22, 2021, ... March 27, 2021], WHERE 21 IS THE startDay
    """
    import datetime
    num_weeks = 1
    start_date = datetime.datetime(year=year, month=monthIndex, day=startDay)

    weeks = {}

    offset = datetime.timedelta(days=0)
    for week in range(num_weeks):
        this_week = []
        for startDay in range(7):
            """ GENERATE THE DAYS OF THE WEEK (7 for the range because 7 days make a week) AND ADD THEM TO this_week """
            date = start_date + offset
            date = date.strftime("%B %d, %Y")
            this_week.append(date)
            offset += datetime.timedelta(days=1)
        """ weeks IS A DICT WITH KEY:[week_num(starts at 0 for the 0th week)] AND VALUE:[an array of days in that week] """
        weeks[week] = this_week

    # RETURN THE FIRST WEEK
    return weeks[0]

def getCurrentTime():
    """ RETURNS THE CURRENT TIME IN 12 HOUR FORMAT """

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

def getCurrentDay(now):
    if not isValidDate(now):
        raise ValueError(f"date is invalid")

    day = now.split()[1]
    return int(day.replace(',', ''))

def getCurrentYear(now):
    if not isValidDate(now):
        raise ValueError("date is invalid")

    year = now.split()[2]
    return int(year)

def getMonthIndex(now=None, specificMonth=None):
    if specificMonth == None:
        if not isValidDate(now):
            raise ValueError(f"date is invalid")

        currentMonth = now.split()[0]
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

        for i, month in enumerate(months, 1):
            if month == currentMonth:
                return i
        return None
    else:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]

        for i, month in enumerate(months, 1):
            if month == specificMonth:
                return i
        return None


def isValidDate(date):
    if len(date.split()) != 3:
        return False
    if ',' not in date:
        return False
    # CHECK DAY
    try:
        day = date.split()[1]
        day =  int(day.replace(',', ''))
    except:
        return False
    # CHECK MONTH
    try:
        currentMonth = date.split()[0]
    except:
        return False
    if currentMonth not in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        return False
    # CHECK YEAR
    try:
        year = int(date.split()[2])
    except:
        return False

    return True



def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password_hash(password, hash):
    if hash_password(password) == hash:
        return True
    return False

if __name__ == '__main__':
    app.run()