import sys
sys.path.append(r"C:\Users\jahei\OneDrive\Documents\Hackathon-1\Finance_Project") # Add path where project is located to allow for import of application
import os
import unittest
import flask.globals
from unittest.mock import patch
from models import *
from application import *



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
            idToUse = max(allUserId)+1

            user = User(id=idToUse, name='username', email='email', password=hash_password('password'), phone_number='phone_number')
            user.addUser()
            session['user_id'] = idToUse


    # TEAR DOWN CLASS
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            # REMOVE USER EXPENSES
            expenseToRemove = Expense.query.filter_by(user_id=session['user_id']).all()
            for expense in expenseToRemove:
                db.session.delete(expense)
                db.session.commit()
            # REMOVE USER
            userToRemove = User.query.get(session['user_id'])
            db.session.delete(userToRemove)
            db.session.commit()


    # SET UP
    def setUp(self):
        with app.app_context():
            self.TestUser = User.query.get(session['user_id'])


    # HELPER FUNCTIONS
    def deleteAllTestExpenses(self):
        with app.app_context():
            expensesToDelete = Expense.query.filter_by(user_id=session['user_id']).all()
            for expense in expensesToDelete:
                db.session.delete(expense)
                db.session.commit()

    def getMonth(self, index):
        index = index % 12
        allMonths = {0: 'January', 1: 'February', 2: 'March', 3: 'April', 4: 'May', 5: 'June', 6: 'July', 7: 'August',
                     8: 'September', 9: 'October', 10: 'November', 11: 'December'}

        return allMonths[index]

    def test_Test(self):
        with app.app_context():
          pass

    # ENSURE THAT FLASK WAS SET UP CORRECTLY
    def test_index(self):
        Tester = app.test_client(self)
        Response = Tester.get('/')
        self.assertEqual(Response.status_code, 200)

    # ENSURE THAT THE HOME PAGE LOADS CORRECTLY
    def test_home(self):
        Tester = app.test_client(self)
        Response = Tester.get(f"/home/{session['user_id']}")
        # Response = Tester.get(f"/home/30")
        self.assertTrue(b'Portfolio' in Response.data)

    # ENSURE THAT getUserInfo RETURNS CORRECT INFO
    def test_getUserInfo(self):
        with app.app_context():
            Tester = app.test_client(self)
            Response = Tester.get('/getUserInfo', content_type='json')
            userInfo = Response.data.decode('utf-8')
            # PARSE JSON
            userInfo = json.loads(userInfo)

            TestUserInfo = {
                'Email': self.TestUser.email,
                'id': self.TestUser.id,
                'phoneNumber': self.TestUser.phone_number,
                'userName': self.TestUser.name,
                'Password': self.TestUser.password
            }
            self.assertDictEqual(userInfo, TestUserInfo)

    # ENSURE THAT updateUserInfo UPDATES INFO CORRECTLY
    def test_updateUserInfo(self):
        with app.app_context():
            Tester = app.test_client(self)

            """ TESTING UPDATE USERNAME """
            newUserNamesToTest = ['new_username', 'new_username1', 'new_username2', 'NEW_USERNAME']

            for newName in newUserNamesToTest:
                # MAKE A POST REQUEST TO UPDATE TEST_USER USERNAME
                Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userName/{newName}/{self.TestUser.name}")
                # GET THE TEST USER AFTER THE NAME HAS BEEN CHANGED
                self.TestUser = User.query.get(session['user_id'])

                # ENSURE THAT THE NAME WAS CHANGED CORRECTLY
                self.assertEqual(self.TestUser.name, newName)
                # ENSURE THAT ROUTE RETURNED CORRECT RETURN VALUE
                self.assertEqual(Response.data.decode('utf-8'), 'Update Successful')

            # ENSURE THAT FUNCTION RETURNS -1 IF NAME IS BEING CHANGED TO THE ONE ALREADY STORED
            Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userName/username/username")
            self.assertEqual(Response.data.decode('utf-8'), '-1')


            # CHANGE TEST_USER USERNAME BACK TO DEFAULT
            User.query.get(session['user_id']).name = 'username'
            db.session.commit()

            """ TESTING UPDATE EMAIL """
            newUserEmailsToTest = ['new_email', 'new_email1', 'new_email2', 'NEW_EMAIL']

            for newEmail in newUserEmailsToTest:
                # MAKE A POST REQUEST TO UPDATE TEST_USER EMAIL
                Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userEmail/{newEmail}/{self.TestUser.email}")
                # GET THE TEST_USER AFTER THE EMAIL HAS BEEN CHANGED
                self.TestUser = User.query.get(session['user_id'])

                # ENSURE THAT THE EMAIL WAS CHANGED CORRECTLY
                self.assertEqual(self.TestUser.email, newEmail)
                # ENSURE THAT ROUTE RETURNED CORRECT RETURN VALUE
                self.assertEqual(Response.data.decode('utf-8'), 'Update Successful')

            # ENSURE THAT THE FUNCTION RETURNS -1 IF EMAIL IS BEING CHANGED TO THE ONE ALREADY STORED
            Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userEmail/email/email")
            self.assertEqual(Response.data.decode('utf-8'), '-1')


            # CHANGE TEST_USER EMAIL BACK TO DEFAULT
            User.query.get(session['user_id']).email = 'email'
            db.session.commit()


            """ TESTING UPDATE PHONE NUMBER """
            newUserPhoneNumbersToTest = ['new_phone_number', 'new_phone_number_1', 'new_phone_number_2', 'NEW_PHONE_NUMBER']

            for newPhoneNumber in newUserPhoneNumbersToTest:
                # MAKE A POST REQUEST TO UPDATE TEST_USER PHONE NUMBER
                Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userPhoneNumber/{newPhoneNumber}/{self.TestUser.phone_number}")
                # GET THE TEST_USER AFTER THE PHONE NUMBER HAS BEEN CHANGED
                self.TestUser = User.query.get(session['user_id'])

                # ENSURE THAT THE PHONE NUMBER WAS CHANGED CORRECTLY
                self.assertEqual(self.TestUser.phone_number, newPhoneNumber)
                # ENSURE THAT ROUTE RETURNED CORRECT RETURN VALUE
                self.assertEqual(Response.data.decode('utf-8'), 'Update Successful')

            # ENSURE THAT THE FUNCTION RETURNS -1 PHONE NUMBER IS BEING CHANGED TO THE ONE ALREADY STORED
            Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userPhoneNumber/phone_number/phone_number")
            self.assertEqual(Response.data.decode('utf-8'), '-1')

            # CHANGE TEST_USER PHONE NUMBER BACK TO DEFAULT
            User.query.get(session['user_id']).phone_number = 'phone_number'
            db.session.commit()

            """ TESTING UPDATE PASSWORD """
            newUserPasswordsToTest = ['new_password', 'new_password_1', 'new_password_2','NEW_PASSWORD']

            for newPassword in newUserPasswordsToTest:
                # MAKE A POST REQUEST TO UPDATE TEST_USER PASSWORD
                Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userPassword/{newPassword}/password")
                # GET THE TEST_USER AFTER THE PASSWORD HAS BEEN CHANGED
                self.TestUser = User.query.get(session['user_id'])

                # ENSURE THAT THE PASSWORD WAS CHANGED CORRECTLY
                self.assertEqual(self.TestUser.password, hash_password(newPassword))
                # ENSURE THAT ROUTE RETURNED CORRECT RETURN VALUE
                self.assertEqual(Response.data.decode('utf-8'), 'Update Successful')

                # CHANGE TEST_USER PASSWORD BACK TO DEFAULT
                User.query.get(session['user_id']).password = hash_password('password')
                db.session.commit()

            # ENSURE THAT THE FUNCTION RETURNS -1 IF THE INCORRECT CURRENT PASSWORD IS ENTERED
            Response = Tester.post(f"/updateUserInfo/{session['user_id']}/userPassword/new_password/not_current_password")
            self.assertEqual(Response.data.decode('utf-8'), '-1')

            # CHANGE TEST_USER PASSWORD BACK TO DEFAULT
            User.query.get(session['user_id']).password = hash_password('password')
            db.session.commit()

    # ENSURE THAT addExpense ADDS EXPENSE WITH THE CORRECT DATA
    def test_addExpense(self):
        with app.app_context():
            Tester = app.test_client(self)

            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")
            expenseData = {
                'expenseName': 'Test Item 1',
                'expensePrice': 1.0,
                'expenseDate': now,
                'expenseTime': getCurrentTime(),
                'user_id': session['user_id'],
                'auto-send-email': 'disabled'
            }
            Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')
            testUserExpenses = Expense.query.filter_by(user_id = session['user_id']).first()

            # CHECK TO SEE IF THE EXPENSE DATA IS CORRECT
            self.assertEqual(expenseData['expenseName'], testUserExpenses.item_name)
            self.assertEqual(expenseData['expensePrice'], testUserExpenses.item_price)
            self.assertEqual(expenseData['expenseDate'], testUserExpenses.date)
            self.assertEqual(expenseData['expenseTime'], testUserExpenses.time)
            self.assertEqual(expenseData['user_id'], testUserExpenses.user_id)

    # ENSURE THAT editExpense CHANGES THE EXPENSE DATA CORRECTLY
    def test_editExpense(self):
        with app.app_context():
            Tester = app.test_client(self)

            # ADD EXPENSE
            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")
            expenseData = {
                'expenseName': 'Test Item 2',
                'expensePrice': 1.0,
                'expenseDate': now,
                'expenseTime': getCurrentTime(),
                'user_id': session['user_id'],
                'auto-send-email': 'disabled'
            }
            Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')
            testUserExpense = Expense.query.filter(and_(Expense.item_name == expenseData['expenseName']), Expense.user_id == expenseData['user_id']).first()

            newExpenseName = 'New Test Item 2'
            newExpensePrice = '2.0'

            newExpenseName2 = 'New Test Item 3'
            newExpensePrice2 = '3.0'

            # EDIT EXPENSE NAME
            Response = Tester.post(f"/editExpense/{testUserExpense.id}/{newExpenseName}/Empty")
            # ENSURE THAT EXPENSE NAME WAS CHANGED CORRECTLY
            testUserExpense = Expense.query.filter(and_(Expense.item_name == newExpenseName, Expense.user_id == expenseData['user_id'])).first()
            self.assertNotEqual(testUserExpense, None)
            self.assertEqual(testUserExpense.item_name, newExpenseName)
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Name Successfully Changed')

            # EDIT EXPENSE PRICE
            Response = Tester.post(f"/editExpense/{testUserExpense.id}/Empty/{newExpensePrice}")
            # ENSURE THAT EXPENSE PRICE WAS CHANGED CORRECTLY
            testUserExpense = Expense.query.filter(and_(Expense.item_price == float(newExpensePrice), Expense.user_id == expenseData['user_id'])).first()
            self.assertNotEqual(testUserExpense, None)
            self.assertEqual(str(testUserExpense.item_price), newExpensePrice)
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Price Successfully Changed')

            # EDIT EXPENSE NAME AND PRICE
            Response = Tester.post(f"/editExpense/{testUserExpense.id}/{newExpenseName2}/{newExpensePrice2}")
            # ENSURE THAT EXPENSE NAME AND PRICE WAS CHANGED CORRECTLY
            testUserExpense = Expense.query.filter(and_(Expense.item_name == newExpenseName2, Expense.item_price == newExpensePrice2, Expense.user_id == expenseData['user_id'])).first()
            self.assertNotEqual(testUserExpense, None)
            self.assertEqual(testUserExpense.item_name, newExpenseName2)
            self.assertEqual(str(testUserExpense.item_price), newExpensePrice2)
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Name and Price Successfully Changed')

            # EDIT NOTHING
            Response = Tester.post(f"/editExpense/{testUserExpense.id}/Empty/Empty")
            # ENSURE THAT NOTHING WAS CHANGED
            testUserExpense = Expense.query.filter(and_(Expense.item_name == 'Empty', Expense.user_id == expenseData['user_id'])).first()
            self.assertEqual(testUserExpense, None)
            self.assertEqual(Response.data.decode('utf-8'), 'No Changes Made')

    # ENSURE THAT AN EXPENSE IS PROPERLY DELETED
    def test_deleteExpense(self):
        with app.app_context():
            Tester = app.test_client(self)

            # ADD EXPENSE
            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")
            expenseData = {
                'expenseName': 'Test Delete Item 1',
                'expensePrice': 1.0,
                'expenseDate': now,
                'expenseTime': getCurrentTime(),
                'user_id': session['user_id'],
                'auto-send-email': 'disabled'
            }
            Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')
            testUserExpense = Expense.query.filter(and_(Expense.item_name == expenseData['expenseName']), Expense.user_id == expenseData['user_id']).first()

            # DELETE EXPENSE
            Response = Tester.post(f"deleteExpense/{str(testUserExpense.id)}")
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Successfully Deleted')
            # CHECK IF EXPENSE WAS DELETED
            deletedExpense = Expense.query.get(testUserExpense.id)
            self.assertEqual(deletedExpense, None)
            # CHECK IF ERROR MESSAGE IS RETURNED IF TRYING TO DELETE AN EXPENSE THAT DOESN'T EXIST
            Response = Tester.post(f"deleteExpense/{str(testUserExpense.id)}")
            self.assertEqual(Response.data.decode('utf-8'), 'Expense Not Found')

    # ENSURE THAT getExpenses WORE CORRECTLY WHEN GETTING EXPENSES FOR DIFFERENT TIME PERIODS, ORDER AND SORT
    def test_getExpenses(self):
        with app.app_context():
            Tester = app.test_client(self)

            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")

            allPossibleSortBy = ['item_name', 'item_price']

            for sortBy in allPossibleSortBy:
                # DELETE ANY PREVIOUS EXPENSES, IF ANY
                self.deleteAllTestExpenses()

                """ ADD EXPENSES TO TEST FOR PERIOD: all-time and this-day """

                testExpenseAttributes = {
                    'item_name': ['Test Item 0', 'Test Item 1', 'Test Item 2', 'Test Item 3'],
                    'item_price': [0.0, 1.0, 2.0, 3.0]
                }

                """
                If we are sorting by item_name, then we loop over all the test item names and add those names to the database while
                item_price remains a default value 1.0. We then check if those item_names get retrieved correctly.
                If we are sorting by item_price, then we loop over all the test item prices and add those names to the database while
                item_name remains a default value: 'Test Item 0', 'Test Item 1'.. We then check if those item_prices get retrived correctly.
                """
                for i, testAttr in enumerate(testExpenseAttributes[sortBy]):
                    expenseData = {
                        'expenseName': testAttr if sortBy == 'item_name' else f'Test Item {i}',
                        'expensePrice': testAttr if sortBy == 'item_price' else 1.0,
                        'expenseDate': now,
                        'expenseTime': getCurrentTime(),
                        'user_id': session['user_id'],
                        'auto-send-email': 'disabled'
                    }
                    Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                    self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')


                # TEST FOR PERIOD: all-time CHECK FOR ORDER: asc
                Response = Tester.get(f"/getExpenses/all-time/{sortBy}/asc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF THE asc ORDER MATCHES
                """
                HARD CODED WAY TO CHECK asc ORDER: 
                self.assertEqual(expensesReturned[0][sortBy], testExpenseAttributes[sortBy][0])
                self.assertEqual(expensesReturned[1][sortBy], testExpenseAttributes[sortBy][1])
                self.assertEqual(expensesReturned[2][sortBy], testExpenseAttributes[sortBy][2])
                
                HARD CODED WAY TO CHECK desc ORDER:
                self.assertEqual(expensesReturned[0][sortBy], testExpenseAttributes[sortBy][2])
                self.assertEqual(expensesReturned[1][sortBy], testExpenseAttributes[sortBy][1])
                self.assertEqual(expensesReturned[2][sortBy], testExpenseAttributes[sortBy][0])
                
                """
                i = 0
                while i < len(testExpenseAttributes[sortBy]):
                    self.assertEqual(expensesReturned[i][sortBy], testExpenseAttributes[sortBy][i])
                    i += 1
                # TEST FOR PERIOD: all-time CHECK FOR ORDER: desc
                Response = Tester.get(f"/getExpenses/all-time/{sortBy}/desc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF THE desc ORDER MATCHES
                i, j = 0, len(testExpenseAttributes[sortBy])-1
                while j >= 0:
                    self.assertEqual(expensesReturned[i][sortBy], testExpenseAttributes[sortBy][j])
                    i, j = i+1, j-1

                # TEST FOR PERIOD: this-day. CHECK FOR ORDER: asc
                Response = Tester.get(f"/getExpenses/this-day/{sortBy}/asc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF asc ORDER MATCHES
                i = 0
                while i < len(testExpenseAttributes[sortBy]):
                    self.assertEqual(expensesReturned[i][sortBy], testExpenseAttributes[sortBy][i])
                    i += 1
                # TEST FOR PERIOD: this-day CHECK FOR ORDER: desc
                Response = Tester.get(f"/getExpenses/this-day/{sortBy}/desc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF desc ORDER MATCHES
                i, j = 0, len(testExpenseAttributes[sortBy])-1
                while j >= 0:
                    self.assertEqual(expensesReturned[i][sortBy], testExpenseAttributes[sortBy][j])
                    i, j = i+1, j-1

                self.deleteAllTestExpenses()
                """ ADD EXPENSES TO TEST FOR PERIOD: this-week """

                testExpenseDates = getThisWeekForQuery()

                for i, testDate in enumerate(testExpenseDates):
                    expenseData = {
                        'expenseName': f'Test Item {i}',
                        'expensePrice': float(i+1),
                        'expenseDate': testDate,
                        'expenseTime': getCurrentTime(),
                        'user_id': session['user_id'],
                        'auto-send-email': 'disabled'
                    }
                    Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                    self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

                # TEST FOR PERIOD: this-week CHECK FOR ORDER: asc
                Response = Tester.get(f"/getExpenses/this-week/{sortBy}/asc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF asc ORDER MATCHES
                i = 0
                while i < len(testExpenseDates):
                    self.assertEqual(expensesReturned[i]['date'], testExpenseDates[i])
                    i += 1
                # TEST FOR PERIOD: this-week CHECK FOR ORDER: desc
                Response = Tester.get(f"/getExpenses/this-week/{sortBy}/desc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                # CHECK IF desc ORDER MATCHES
                i, j = 0, len(testExpenseDates)-1
                while j >= 0:
                    self.assertEqual(expensesReturned[i]['date'], testExpenseDates[j])
                    i, j = i+1, j-1

                self.deleteAllTestExpenses()
                """ADD EXPENSES TO TEST FOR PERIOD: this-month"""

                Today = getCurrentDay(now)
                thisYear = getCurrentYear(now)
                currentMonthIndex = getMonthIndex(now)-1

                testExpenseDates = [f"{self.getMonth(currentMonthIndex+i)} {Today}, {thisYear}" for i in range(12)]

                """
                testExpensesDates is an array of dates that is generated with dates of varying months, each iteration adds
                a date with month +1 of the previous month(adds a date with January, then February, then March, and so on..)
                We then make a request to get the expense that was added this-month, testExpensesDates start populating dates
                starting with the current month that we are in; so the first expenses that is added, is THE expense of this month.
                So we check to see if the date of the expense that was returned matches with the first date that was populated(which is
                the date with this month)
                Same logic applies when testing for this-year, the only change is the dates that are generated are of different years
                2021, then 2022, and so on..
                """
                for i, testDate in enumerate(testExpenseDates):
                    expenseData = {
                        'expenseName': f'Test Item {i}',
                        'expensePrice': float(i+1),
                        'expenseDate': testDate,
                        'expenseTime': getCurrentTime(),
                        'user_id': session['user_id'],
                        'auto-send-email': 'disabled'
                    }
                    Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                    self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

                # TEST FOR PERIOD: this-month CHECK FOR ORDER: DOEST NOT MATTER, ONLY 1 EXPENSE WILL GET RETURNED EVERYTIME
                Response = Tester.get(f"/getExpenses/this-month/{sortBy}/asc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                self.assertEqual(expensesReturned[0]['date'], testExpenseDates[0])


                self.deleteAllTestExpenses()
                """ADD EXPENSES TO TEST FOR PERIOD: this-year"""

                Today = getCurrentDay(now)
                thisYear = int(getCurrentYear(now))
                currentMonthIndex = getMonthIndex(now) - 1

                testExpenseDates = [f"{self.getMonth(currentMonthIndex)} {Today}, {thisYear+i}" for i in range(5)]

                for i, testDate in enumerate(testExpenseDates):
                    expenseData = {
                        'expenseName': f'Test Item {i}',
                        'expensePrice': float(i+1),
                        'expenseDate': testDate,
                        'expenseTime': getCurrentTime(),
                        'user_id': session['user_id'],
                        'auto-send-email': 'disabled'
                    }
                    Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                    self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

                # TEST FOR PERIOD: this-year CHECK FOR ORDER: DOEST NOT MATTER, ONLY 1 EXPENSE WILL GET RETURNED EVERYTIME
                Response = Tester.get(f"/getExpenses/this-year/{sortBy}/asc")
                expensesReturned = json.loads(Response.data.decode('utf-8'))
                self.assertEqual(expensesReturned[0]['date'], testExpenseDates[0])

                self.deleteAllTestExpenses()

    def test_getTotalExpenses(self):
        with app.app_context():
            Tester = app.test_client(self)

            now = datetime.now(EST()).date()
            now = now.strftime("%B %d, %Y")

            # DELETE PREVIOUS EXPENSES IF ANY
            self.deleteAllTestExpenses()
            """ ADD EXPENSES TO TEST FOR PERIOD: all-time, this-day """

            testExpensePrices = [float(i) for i in range(5)]

            for i, testPrice in enumerate(testExpensePrices):
                expenseData = {
                    'expenseName': f'Test Item {i}',
                    'expensePrice': testPrice,
                    'expenseDate': now,
                    'expenseTime': getCurrentTime(),
                    'user_id': session['user_id'],
                    'auto-send-email': 'disabled'
                }
                Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

            # CHECK IF THE TOTAL EXPENSE RETURNED IS CORRECT FOR PERIOD: all-time
            Response = Tester.get(f"/getTotalExpense/all-time")
            self.assertEqual(float(Response.data.decode('utf-8')), sum(testExpensePrices))
            # CHECK IF THE TOTAL EXPENSE RETURNED IS CORRECT FOR PERIOD: this-day
            Response = Tester.get(f"/getTotalExpense/this-day")
            self.assertEqual(float(Response.data.decode('utf-8')), sum(testExpensePrices))


            self.deleteAllTestExpenses()
            """ ADD EXPENSES TO TEST FOR PERIOD: this-week """

            testExpenseDates = getThisWeekForQuery()
            testExpensePrices = [float(i) for i in range(len(testExpenseDates))]

            for i, testDate in enumerate(testExpenseDates):
                expenseData = {
                    'expenseName': f'Test Item {i}',
                    'expensePrice': testExpensePrices[i],
                    'expenseDate': testDate,
                    'expenseTime': getCurrentTime(),
                    'user_id': session['user_id'],
                    'auto-send-email': 'disabled'
                }
                Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

            # CHECK IF THE TOTAL EXPENSE RETURNED IS CORRECT FOR PERIOD: this-week
            Response = Tester.get(f"/getTotalExpense/this-week")
            self.assertEqual(float(Response.data.decode('utf-8')), sum(testExpensePrices))


            self.deleteAllTestExpenses()
            """ ADD EXPENSES TO TEST FOR PERIOD: this-month """

            Today = getCurrentDay(now)
            thisYear = getCurrentYear(now)
            currentMonthIndex = getMonthIndex(now) - 1

            testExpenseDates = [f"{self.getMonth(currentMonthIndex + i)} {Today}, {thisYear}" for i in range(12)]
            testExpensePrices = [float(i) for i in range(len(testExpenseDates))]

            """
            testExpensesDates is an array of dates that is generated with dates of varying months, each iteration adds
            a date with month +1 of the previous month(adds a date with January, then February, then March, and so on..)
            We then make a request to get the total expense of this month, testExpensesDates start populating dates
            starting with the current month that we are in; so the first expenses that is added, is THE expense of this month.
            So we check to see if the price of that expense matches with the first price that was populated(which is
            the expense price of this month)
            Same logic applies when testing for this-year, the only change is the dates that are generated are of different years
            2021, then 2022, and so on..
            """
            for i, testDate in enumerate(testExpenseDates):
                expenseData = {
                    'expenseName': f'Test Item {i}',
                    'expensePrice': testExpensePrices[i],
                    'expenseDate': testDate,
                    'expenseTime': getCurrentTime(),
                    'user_id': session['user_id'],
                    'auto-send-email': 'disabled'
                }
                Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

            # CHECK IF THE TOTAL EXPENSE RETURNED IS CORRECT FOR PERIOD: this-month
            Response = Tester.get(f"/getTotalExpense/this-month")
            self.assertEqual(float(Response.data.decode('utf-8')), testExpensePrices[0])


            self.deleteAllTestExpenses()
            """ ADD EXPENSES TO TEST FOR PERIOD: this-year """

            Today = getCurrentDay(now)
            thisYear = int(getCurrentYear(now))
            currentMonthIndex = getMonthIndex(now) - 1

            testExpenseDates = [f"{self.getMonth(currentMonthIndex)} {Today}, {thisYear + i}" for i in range(5)]
            testExpensePrices = [float(i) for i in range(len(testExpenseDates))]

            for i, testDate in enumerate(testExpenseDates):
                expenseData = {
                    'expenseName': f'Test Item {i}',
                    'expensePrice': testExpensePrices[i],
                    'expenseDate': testDate,
                    'expenseTime': getCurrentTime(),
                    'user_id': session['user_id'],
                    'auto-send-email': 'disabled'
                }
                Response = Tester.post(f"/addExpense/{json.dumps(expenseData)}")
                self.assertEqual(Response.data.decode('utf-8'), 'Expense Added, Spending Limit Not Exceeded')

            # CHECK IF THE TOTAL EXPENSE RETURNED IS CORRECT FOR PERIOD: this-month
            Response = Tester.get(f"/getTotalExpense/this-year")
            self.assertEqual(float(Response.data.decode('utf-8')), testExpensePrices[0])

            self.deleteAllTestExpenses()
















if __name__ == '__main__':
    unittest.main()
