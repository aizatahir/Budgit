import hashlib
# from datetime import date, datetime
# current_date = date.today()
# now = current_date.strftime("%B %d, %Y")

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    password = db.Column(db.String, nullable=False)

    def addUser(self):
        newUser = User(name=self.name, email=self.email, password=self.password)
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

    def addExpense(self):
        e = Expense(item_name=self.item_name, item_price=self.item_price, date=self.date, time=self.time, user_id=self.user_id)
        db.session.add(e)
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
