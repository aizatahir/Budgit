import hashlib
import datetime
from Classes import datetime, EST, Date
from Methods import getThisWeekForQuery
# from datetime import date, datetime
# current_date = date.today()
# now = current_date.strftime("%B %d, %Y")

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func




db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String)

    def addUser(self):
        if self.id == None:
            newUser = User(name=self.name, email=self.email, password=self.password, phone_number=self.phone_number)
        else:
            newUser = User(id=self.id, name=self.name, email=self.email, password=self.password, phone_number=self.phone_number)

        # CHECK IF USER ALREADY EXIST
        checkUsers = User.query.filter(and_(User.name == self.name, User.password == self.password)).all()
        if len(checkUsers) != 0:
            return -1
        else:
            db.session.add(newUser)
            db.session.commit()

    def validateCredentials(self):
        checkUsers = User.query.filter(and_(User.name == self.name, User.password == self.password)).all()
        return len(checkUsers) != 0

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String, nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")
    now = Date(now)


    def addExpense(self):
        e = Expense(item_name=self.item_name, item_price=self.item_price, date=self.date, time=self.time, user_id=self.user_id)
        db.session.add(e)
        db.session.commit()

    def getTotalUserExpense(self, period):
        if period == 'all-time':
            expenseQuery = db.session.query(func.sum(Expense.item_price)).filter_by(user_id=self.user_id).first()[0]
            return expenseQuery if expenseQuery != None else 0.0
        elif period == 'this-day':
            expenseQuery = db.session.query(func.sum(Expense.item_price)).filter_by(date=str(Expense.now), user_id=self.user_id).first()[0]
            return expenseQuery if expenseQuery != None else 0.0
        elif period == 'this-week':
            thisWeek = getThisWeekForQuery(str(Expense.now))
            expenseQuery = db.session.query(func.sum(Expense.item_price)).filter(and_(Expense.user_id == self.user_id, Expense.date.in_(thisWeek))).first()[0]
            return expenseQuery if expenseQuery != None else 0.0
        elif period == 'this-month':
            thisMonth, thisYear = Expense.now.month, str(Expense.now.year)
            expenseQuery = db.session.query(func.sum(Expense.item_price)).filter(and_(Expense.user_id == self.user_id, Expense.date.like(f"%{thisMonth}%"), Expense.date.like(f"%{thisYear}%"))).first()[0]
            return expenseQuery if expenseQuery != None else 0.0
        elif period == 'this-year':
            thisYear = str(Expense.now.year)
            expenseQuery = db.session.query(func.sum(Expense.item_price)).filter(and_(Expense.user_id == self.user_id, Expense.date.like(f"%{thisYear}%"))).first()[0]
            return expenseQuery if expenseQuery != None else 0.0




class ScheduledExpense(db.Model):
    __tablename__ = 'scheduled_expenses'
    id = db.Column(db.Integer, primary_key=True)
    expense_name = db.Column(db.String, nullable=False)
    expense_price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    next_due = db.Column(db.String, nullable=False)
    frequency = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def addScheduledExpense(self):
        SE = ScheduledExpense(expense_name=self.expense_name, expense_price=self.expense_price, start_date=self.start_date, next_due=self.next_due, frequency=self.frequency, user_id=self.user_id)
        db.session.add(SE)
        db.session.commit()

class ExpenseLimit(db.Model):
    __tablename__ = "expense_limit"
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Float)
    week = db.Column(db.Float)
    month = db.Column(db.Float)
    year   = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def addExpenseLimit(self, limit, period):
        l = ExpenseLimit(day=self.day, week=self.week, month=self.month, year=self.year, user_id=self.user_id)

        # CHECK IF USER HAS ALREADY SET A LIMIT
        checkLimit = ExpenseLimit.query.filter_by(user_id = self.user_id).all()
        if len(checkLimit) == 0:
            db.session.add(l)
            db.session.commit()
            return
        userLimits = ExpenseLimit.query.filter_by(user_id=self.user_id).first()
        if period == "this-day":
            userLimits.day = limit
            db.session.commit()
            return
        elif period == "this-week":
            userLimits.week = limit
            db.session.commit()
            return
        elif period == 'this-month':
            userLimits.month = limit
            db.session.commit()
            return
        elif period == 'this-year':
            userLimits.year = limit
            db.session.commit()
            return

class HomeSettings(db.Model):
    __tablename__ = 'home_settings'
    id = db.Column(db.Integer, primary_key=True)
    expense_table_time_period = db.Column(db.String, default='this-day')
    expense_table_sort_by = db.Column(db.String, default='item_name')
    expense_table_order = db.Column(db.String, default='asc')
    total_expense_time_period = db.Column(db.String, default='this-day')
    expense_limit_time_period = db.Column(db.String, default='this-day')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def createDefaultUserSettings(self):
        HS = HomeSettings(user_id=self.user_id)
        # CHECK IF SETTING HAS ALREADY BEEN CREATED
        checkHS = HomeSettings.query.filter_by(user_id=self.user_id).all()
        if checkHS == []:
            db.session.add(HS)
            db.session.commit()

    def getHomeSettings(self):
        HS = HomeSettings.query.filter_by(user_id=self.user_id).first()
        return HS

    def updateHomeSettings(self, newSettings):
        self.expense_table_time_period = newSettings['expenseTable-Time-Period']
        self.expense_table_sort_by = newSettings['expenseTable-SortBy']
        self.expense_table_order = newSettings['expenseTable-Order']
        self.expense_limit_time_period = newSettings['expenseLimit-TimePeriod']
        self.total_expense_time_period = newSettings['totalExpense-TimePeriod']
        db.session.commit()