import datetime
from calendar import monthrange
from datetime import date, timedelta, tzinfo, datetime
# from Methods import getMonthIndex



class EST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours = -5)

    def tzname(self, dt):
        return "EST"

    def dst(self, dt):
        return timedelta(0)

class HashTable():
    def __init__(self, dict=None):
        if dict == None:
            self.keys = []
            self.values = []
        else:
            if len(dict) == 1:
                self.key = list(dict)[0]
                self.keys = [self.key]
                self.value = list(dict.values())[0]
                self.values = [self.value]
            else:
                self.keys = list(dict.keys())
                self.values = list(dict.values())

    def update(self, key, value):
        if key not in self.keys:
            self.keys.append(key)
            self.values.append(value)
        else:
            indexOfKey = self.indexOf(self.keys, key)
            Value = self.values[indexOfKey]
            if type(Value) != set:
                new_vals = {Value, value}
                self.values[indexOfKey] = new_vals
            else:
                Value.add(value)
                self.values[indexOfKey] = Value
    def get(self, key):
        indexOfKey = self.indexOf(self.keys, key)
        try:
            return self.values[indexOfKey]
        except TypeError:
            return None
    @staticmethod
    def indexOf(array, item):
        for i in range(len(array)):
            if array[i] == item:
                return i
        return None

    def getTable(self):
        Table = {self.keys[i]:self.values[i] for i in range(len(self.keys))}
        return Table

    def __str__(self):
        return f"{self.getTable()}"

class Date:
    monthLookup = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',9: 'September',
                   10: 'October', 11: 'November', 12: 'December'}

    def __init__(self, date=None):
        if date != None:
            self.day = int(date.split()[1].replace(',', ''))
            self.month = date.split()[0]
            self.year = int(date.split()[2])
        else:
            now = datetime.now(EST()).date()
            self.today = now.strftime("%B %d, %Y")
            self.day = int(self.today.split()[1].replace(',', ''))
            self.month = self.today.split()[0]
            self.year = int(self.today.split()[2])

    @staticmethod
    def validateDate(due_date):
        tmp_date = due_date
        all_months = {"January", "February", "March", "April", "May", "June", "July", "August",
                      "September", "October", "November", "December"}

        try:
            due_date = due_date.split()
            due_date_month = due_date[0]
            due_date_day = int(due_date[1].replace(',', ''))
            due_date_year = int(due_date[2])
        except:
            return -1

        # INVALID MONTH
        if due_date_month not in all_months:
            return -2
        # INVALID DAY
        if due_date_day < 1 or due_date_day > 31 if due_date_month != "February" else 28:
            return -3
        # DATE HAS PASSED
        if Date.dateHasPassed(tmp_date):
            return -4

        return 0

    @staticmethod
    def dateHasPassed(due_date):
        now = Date()
        due_date = Date(due_date)

        all_months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                      "September": 9, "October": 10, "November": 11, "December": 12}

        try:
            today_date_day = now.day
            today_date_month = now.month
            today_date_year = now.year

            due_date_day = due_date.day
            due_date_month = due_date.month
            due_date_year = due_date.year

            Today = [all_months[today_date_month], today_date_day, today_date_year]
            Due_Date = [all_months[due_date_month], due_date_day, due_date_year]

            # THE YEAR HAS PASSED
            if Due_Date[2] < Today[2]:
                return True
            if Due_Date[2] > Today[2]:
                return False
            # MONTH HAS PASSED
            if Due_Date[0] < Today[0]:
                return True
            if Due_Date[0] > Today[0]:
                return False
            # DAY HAS PASSED
            if Due_Date[0] == Today[0]:
                if Due_Date[1] < Today[1]:
                    return True
            return False
        except:
            return False


    # TODO - FIX
    def isValidDate(self, date):
        if len(date.split()) != 3:
            return False
        if ',' not in date:
            return False
        # CHECK DAY
        try:
            day = date.split()[1]
            day = int(day.replace(',', ''))
        except:
            return False
        # CHECK MONTH
        try:
            currentMonth = date.split()[0]
        except:
            return False
        if currentMonth not in ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                "October", "November", "December"]:
            return False
        # CHECK YEAR
        try:
            year = int(date.split()[2])
        except:
            return False

        return True


    def getMonthIndex(self, now=None, specificMonth=None):
        if specificMonth == None:
            # if not self.isValidDate(now):
            #     raise ValueError(f"date is invalid")

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

    # ADD TIME
    def addTime(self, timePeriod, amount):
        """ FUNCTIONALITY FOR ADDING DIFFERENT TIME PERIODS TO THE DATE """
        NDIM = self.getNumDaysInMonth()
        numMonthsAdded = 0
        if timePeriod == 'day':
            """ 
            IF THE AMOUNT OF DAYS THAT IS TO BE ADDED IS > THE NUMBER OF DAYS IN THE MONTH AFTER THE FIRST
            EQUATION: 'self.day = (self.day + amount) - NDIM', THEN WE KEEP SUBTRACTING THE NUMBER OF DAYS IN EACH MONTH
            UNTIL self.day <= NDIM, THIS WILL CALCULATE THE DAY THAT THE NEW DATE WILL FALL ON 
            """
            if (self.day + amount) > NDIM:
                self.day = (self.day + amount) - NDIM
                self.month = self.addMonth(1, updateYear=False)
                NDIM = self.getNumDaysInMonth()
                numMonthsAdded += 1
                while (self.day) > NDIM:
                    self.day -= NDIM
                    self.month = self.addMonth(1)
                    NDIM = self.getNumDaysInMonth()
                    numMonthsAdded += 1
                    if self.month == 'December':
                        self.year += 1
            else:
                self.day += amount
            # RETURN THE UPDATED DATE OBJECT
            return self
        elif timePeriod == 'week':
            return self.addTime('day', 7*amount)
        elif timePeriod == 'month':
            self.month = self.addMonth(amount)
            return self
        elif timePeriod == 'year':
            self.year += amount
            return self

    # GET NUM DAYS IN MONTH
    def getNumDaysInMonth(self) -> int:
        """ RETURNS THE NUMBER OF DAYS IN THE MONTH """
        NDIM = monthrange(self.year, self.getMonthIndex(specificMonth=self.month))
        return NDIM[1]

    # ADD MONTH
    def addMonth(self, amount: int, updateYear=True) -> str:
        """ FUNCTIONALITY FOR INCREMENTING MONTH """
        if updateYear:
            monthIndex = self.getMonthIndex(self.month)
            monthIndex += amount
            offset = 0
            while monthIndex > 12:
                offset += 1
                monthIndex -= 12

            self.year += offset
            return Date.monthLookup[monthIndex]
        else:
            monthIndex = self.getMonthIndex(self.month)
            monthIndex += amount
            monthIndex = monthIndex % 12 if monthIndex != 12 else 12
            return Date.monthLookup[monthIndex]


    def __str__(self):
        """ RETURNS THE DATE IN THE 'now' FORMAT """
        if self.day > self.getNumDaysInMonth():
            """ 
            THIS IS AN EDGE CASE WHERE IF FOR EXAMPLE: YOU ADD 1 MONTH TO THE DATE 'January 31', YOU WILL GET 'February 31' WHICH
            DOEST NOT EXIST(THE CORRECT DATE WOULD GO OVER INTO THE NEXT MONTH, SO IT WOULD BE 'March 3', IF FEBRUARY CURRENTLY
            HAS 28 DAYS), SO WE CORRECT THE OFFSET BY ADDING 1 TO THE MONTH AND SET THE DAY = (31 - 28 = 3) 
            """
            self.day -= self.getNumDaysInMonth()
            self.month = self.addMonth(1)

        return f'{self.month} {self.day}, {self.year}' if len(str(self.day)) != 1 else f'{self.month} 0{self.day}, {self.year}'

    def __eq__(self, other):
        if (isinstance(other, Date)):
            return (self.day == other.day) and (self.month == other.month) and (self.year == other.year)
        else:
            return (self.day == Date(other).day) and (self.month == Date(other).month) and (self.year == Date(other).year)




def Test():
    pass

Test()