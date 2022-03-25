import bdb
import json
import sys
sys.path.append(r"C:\Users\jahei\OneDrive\Documents\Hackathon-1\Finance_Project") # Add path where project is located to allow for import of application
import os
import unittest
import flask.globals
from unittest.mock import patch
from models import *
from application import *
from ScheduleExpense import getUpdatedNextDueDate, ScheduledTask
from Classes import HashTable





class TestApplication(unittest.TestCase):
    # SET UP CLASS
    @classmethod
    def setUpClass(cls):
        if app.config['TESTING'] == False:
            raise RuntimeError('Set app.config[TESTING] = True before running unittest')

        allUserId = []
        with app.app_context():
            # GET THE MOST RECENT ID
            users = User.query.all()
            for user in users:
                allUserId.append(user.id)
            idToUse = max(allUserId) + 1

            user = User(id=idToUse, name='username', email='email', password=hash_password('password'),
                        phone_number='phone_number')
            user.addUser()

            # CREATE TEST USER ACCOUNT SETTINGS
            testUserAS = AccountSettings(user_id=idToUse, auto_send_email__exceed_spending_limit='disabled',
                                         auto_send_email__schedule_expense_added='disabled')
            testUserAS.initializeAccountSettingsWithValues()
            # CREATE TEST USER HOME SETTINGS
            testUserHS = HomeSettings(user_id=idToUse)
            testUserHS.createDefaultUserSettings()
            # ADD TEST ID TO SESSION
            session['user_id'] = idToUse

    # HELPER FUNCTIONS
    def deleteAllTestExpenses(self):
        with app.app_context():
            expensesToDelete = Expense.query.filter_by(user_id=session['user_id']).all()
            for expense in expensesToDelete:
                db.session.delete(expense)
                db.session.commit()

    # TEST GET UPDATED NEXT DUE DATE
    def test_getUpdatedNextDueDate(self):
        datesToUpdate = [
            {'January 1, 2021': {'every-1-day': 'January 02, 2021'}},
            {'January 1, 2021': {'every-5-day': 'January 06, 2021'}},
            {'March 5, 2021': {'every-1-week': 'March 12, 2021'}},
            {'March 5, 2021': {'every-6-weeks': 'April 16, 2021'}},
            {'May 14, 2021': {'every-1-month': 'June 14, 2021'}},
            {'May 14, 2021': {'every-4-months': 'September 14, 2021'}},
            {'January 30, 2021': {'every-1-month': 'March 02, 2021'}},
            {'August 11, 2021': {'every-1-year': 'August 11, 2022'}},
            {'August 11, 2021': {'every-4-years': 'August 11, 2025'}},
        ]

        for dateDict in datesToUpdate:
            for date in dateDict:
                expectedResult = HashTable(dateDict[date])
                frequency = expectedResult.key
                expectedNewDate = expectedResult.value

                newDateFromFunction = str(getUpdatedNextDueDate(date,  frequency))

                self.assertEqual(expectedNewDate, newDateFromFunction)

    # TEST SCHEDULED TASK
    def test_ScheduledTask(self):
        with app.app_context():
            Tester = app.test_client(self)

            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")

            NUM_TEST_EXPENSES = 3
            testScheduleExpenseAttributes = {
                'expense_name': ['Test Expense 0', 'Test Expense 1', 'Test Expense 2'],
                'expense_price': [0, 1, 2],
                'start_date': ['01-01-9999', '01-01-9999', '01-01-9999'],
                'frequency': ['every-1-day', 'every-2-weeks', 'every-1-month']

            }
            # ADD TEST SCHEDULE EXPENSES
            for i in range(NUM_TEST_EXPENSES):
                expenseData = {
                    'expense_name': testScheduleExpenseAttributes['expense_name'][i],
                    'expense_price': testScheduleExpenseAttributes['expense_price'][i],
                    'start_date': testScheduleExpenseAttributes['start_date'][i],
                    'next_due': now,
                    'frequency': testScheduleExpenseAttributes['frequency'][i],
                }

                Response = Tester.get(f"/addScheduleExpense/{expenseData['expense_name']}/{expenseData['expense_price']}/{expenseData['start_date']}/{expenseData['frequency']}/{expenseData['next_due']}")
                self.assertEqual(Response.data.decode('utf-8'), 'Expense Successfully Scheduled')


            # RUN SCHEDULED TASK
            self.deleteAllTestExpenses()
            ScheduledTask()
            # CHECK IF EXPENSES WERE ADDED
            Response = Tester.get(f"/getExpenses/all-time/item_name/asc/null/null/false")
            expensesReturned = json.loads(Response.data.decode('utf-8'))
            for i, expense in enumerate(expensesReturned):
                # Check expense name
                self.assertEqual(testScheduleExpenseAttributes['expense_name'][i], expense['item_name'])
                # Check expense price
                self.assertEqual(testScheduleExpenseAttributes['expense_price'][i], expense['item_price'])
                # Check expense date
                self.assertEqual(now, expense['date'])





    # TEAR DOWN CLASS
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            # REMOVE USER EXPENSES
            expenseToRemove = Expense.query.filter_by(user_id=session['user_id']).all()
            for expense in expenseToRemove:
                db.session.delete(expense)
                db.session.commit()
            # REMOVE USER SCHEDULE EXPENSES
            scheduleExpensesToRemove = ScheduledExpense.query.filter_by(user_id=session['user_id']).all()
            for sch_expense in scheduleExpensesToRemove:
                db.session.delete(sch_expense)
                db.session.commit()
            # RESET EXPENSE LIMITS
            testExpenseToRemove = ExpenseLimit.query.filter_by(user_id=session['user_id']).first()
            if testExpenseToRemove != None:
                db.session.delete(testExpenseToRemove)
                db.session.commit()
            # REMOVE USER ACCOUNT SETTINGS
            ASToRemove = AccountSettings.query.filter_by(user_id=session['user_id']).first()
            db.session.delete(ASToRemove)
            db.session.commit()
            # REMOVE USER HOME SETTINGS
            HSToRemove = HomeSettings.query.filter_by(user_id=session['user_id']).first()
            db.session.delete(HSToRemove)
            db.session.commit()
            # REMOVE USER
            userToRemove = User.query.get(session['user_id'])
            db.session.delete(userToRemove)
            db.session.commit()


if __name__ == '__main__':
    unittest.main()