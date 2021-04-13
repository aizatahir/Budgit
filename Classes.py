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
            self.now = now.strftime("%B %d, %Y")

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