import datetime
from calendar import monthrange
from datetime import date, timedelta, tzinfo, datetime
from math import inf

from Classes import Date, EST

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

def getIntegerDayForNow(now):
    """
    THIS IS A METHOD THAT PARSES THE DATE BY CONVERTING THE SINGLE DIGIT DAYS TO AN INTEGER. EXAMPLE: 'May 03, 2021' GETS RETURNED AS 'May 3, 2021'
    """
    if not isValidDate(now):
        raise ValueError("date is invalid")
    month = now.split()[0]
    day = f"{int(now.split()[1].replace(',', ''))}"
    year = now.split()[2]

    return f'{month} {day}, {year}'



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


def getMostRecentDate(listOfDates: list):
    mostRecentDay = 1
    mostRecentMonth = 1
    mostRecentYear = 1
    # FILTER YEAR
    for date in listOfDates:
        date = Date(date)
        if date.year > mostRecentYear:
            mostRecentYear = date.year
    # FILTER MONTH
    for date in listOfDates:
        date = Date(date)
        if date.year == mostRecentYear:
            if date.getMonthIndex(specificMonth=date.month) > mostRecentMonth:
                mostRecentMonth = date.getMonthIndex(specificMonth=date.month)
    # FILTER DAY
    for date in listOfDates:
        date = Date(date)
        if (date.year == mostRecentYear) and (date.month == Date.monthLookup[mostRecentMonth]) and (date.day > mostRecentDay):
            mostRecentDay = date.day

    # CONVERT MOST RECENT MONTH FROM INDEX FORM TO THE NAME OF THE MONTH
    mostRecentMonth = Date.monthLookup[mostRecentMonth]

    return Date(f"{mostRecentMonth} {mostRecentDay}, {mostRecentYear}")




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
        return 0

    # INVALID MONTH
    if due_date_month not in all_months:
        return -1
    # INVALID DAY
    if due_date_day < 1 or due_date_day > 31 if due_date_month != "February" else 28:
        return -2
    # DATE HAS PASSED
    if dateHasPassed(tmp_date):
        return -3

    return 1


def dateHasPassed(due_date):
    now = Date()
    due_date = Date(due_date)

    all_months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                  "September": 9, "October": 10, "November": 11, "December": 12}

    try:
        today_date_day   = now.day
        today_date_month = now.month
        today_date_year  = now.year

        due_date_day   = due_date.day
        due_date_month = due_date.month
        due_date_year  = due_date.year

        Today    = [all_months[today_date_month], today_date_day, today_date_year]
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




def main():
    pass
    # now = 'May 1, 2021'
    # print(Date.validateDate(now))



main()
