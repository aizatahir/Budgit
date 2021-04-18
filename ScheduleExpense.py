import requests
from flask_script import Manager
from application import app,  sendEmail,  getCurrentTime
# from application import *

from models import *

from flask_apscheduler import APScheduler
scheduler = APScheduler()

manager = Manager(app)


from Classes import Date

@manager.command
def ScheduledTask():
    now = datetime.now(EST()).date()
    now = now.strftime("%B %d, %Y")
    # now = Date(now)

    with app.app_context():
        allScheduledExpenses = ScheduledExpense.query.all()

        # CHECK IF ANY EXPENSE IS DUE TO BE ADDED
        for expense in allScheduledExpenses:
            if expense.next_due == now:

                scheduleExpense = Expense(item_name=expense.expense_name, item_price=expense.expense_price, date=str(now), time=getCurrentTime(), user_id=expense.user_id)
                scheduleExpense.addExpense()

                # UPDATE THE NEXT DUE OF THE EXPENSE
                expense.next_due = str(getUpdatedNextDueDate(now, expense.frequency))
                db.session.commit()

                # SEND EMAIL
                totalExpenses = {
                    'this-day': f"${format(scheduleExpense.getTotalUserExpense('this-day'), ',.2f')}",
                    'this-week': f"${format(scheduleExpense.getTotalUserExpense('this-week'), ',.2f')}",
                    'this-month': f"${format(scheduleExpense.getTotalUserExpense('this-month'), ',.2f')}",
                    'this-year': f"${format(scheduleExpense.getTotalUserExpense('this-year'), ',.2f')}"
                }

                user = User.query.get(expense.user_id)

                if user.email != None:
                    message = f"Your Scheduled Expense: '{expense.expense_name}' Has Just Been Added.\n\n" \
                              f"Total Expense For Today: {totalExpenses['this-day']}\n" \
                              f"Total Expense For This Week: {totalExpenses['this-week']}\n" \
                              f"Total Expense For This Month: {totalExpenses['this-month']}\n" \
                              f"Total Expense For This Year: {totalExpenses['this-year']}\n"

                    sendEmail(user.email, 'Scheduled Expense Added', message)


def getUpdatedNextDueDate(currentDate, frequency):
    """ RETURNS THE NEXT DUE DATE FOR AN EXPENSE WHEN GIVEN ITS FREQUENCY """
    if not isinstance(currentDate, Date):
        currentDate = Date(currentDate)

    frequencyAmount = int(frequency.split('-')[1])

    if 'day' in frequency:
        return currentDate.addTime('day', frequencyAmount)
    elif 'week' in frequency:
        return currentDate.addTime('week', frequencyAmount)
    elif 'month' in frequency:
        return currentDate.addTime('month', frequencyAmount)
    elif 'year' in frequency:
        return currentDate.addTime('year', frequencyAmount)



def Test():
    pass
    # ScheduledTask()
    # pass


if __name__ == '__main__':
    manager.run()
