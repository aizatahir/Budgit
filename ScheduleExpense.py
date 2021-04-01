from flask_script import Manager
from application import app, datetime, sendEmail, EST
from models import ScheduledExpense, Expense
from email.message import EmailMessage
import smtplib

from flask_apscheduler import APScheduler
scheduler = APScheduler()

manager = Manager(app)


# @manager.command
def ScheduledTask():
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")

    print(now)
    with app.app_context():
        allScheduledExpenses = ScheduledExpense.query.all()
        # CHECK IF ANY EXPENSE IS DUE TO BE ADDED
        for expense in allScheduledExpenses:
            print(expense.expense_name)


if __name__ == '__main__':
    ScheduledTask()
    # manager.run()
