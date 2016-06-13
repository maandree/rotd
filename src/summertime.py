# -*- python -*-
# See LICENSE file for copyright and license details.

def is_summer_time(days_offset = 0, check_time = '12:00:00'):
    '''
    Is summer time in effect during (most of) the selected day?
    
    Assumes that there is, and only is, standard time and summer time.
    Problems can occur if you for example also have double summer time
    or if you have permanent summer time.
    
    @param   days_offset:int  The number of days into the future to check, 0 for today (local time)
    @param   check_time:str   The time of the day to check (current timezone), either in
                              '%H:%M:%S' or '%H:%M' format.
    @return  :(:bool, :date)  Whether summer time is in effect durning the day, and the selected date
    '''
    import time
    check_time = ':'.join((check_time + ':00').split(':')[:3])
    now = time.localtime()
    (year, mon, mday) = now.tm_year, now.tm_mon, now.tm_mday + days_offset
    feb = lambda y : 29 if y % 400 == 0 or y % 4 == 0 and not y % 100 == 0 else 28
    DAYS_OF_MONTHS = [-1, 31, feb(year), 31, 30, 31, 30, 30, 31, 30, 31, 30, 31]
    while mday > DAYS_OF_MONTHS[mon]:
        mday -= DAYS_OF_MONTHS[mon]
        mon += 1
        if mon > 12:
            mon = 1
            year += 1
            DAYS_OF_MONTHS = [-1, 31, feb(year), 31, 30, 31, 30, 30, 31, 30, 31, 30, 31]
    while mday <= 0:
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
            DAYS_OF_MONTHS = [-1, 31, feb(year), 31, 30, 31, 30, 30, 31, 30, 31, 30, 31]
        mday += DAYS_OF_MONTHS[mon]
    date = '%i-%02i-%02i' % (year, mon, mday)
    check_time = '%s %s' % (date, check_time)
    date = time.strptime(date, '%Y-%m-%d')
    guessed = time.mktime(time.strptime(check_time, '%Y-%m-%d %H:%M:%S'))
    for tzname, summer in zip(time.tzname, (False, True)):
        if time.mktime(time.strptime('%s %s' % (check_time, tzname), '%Y-%m-%d %H:%M:%S %Z')) == guessed:
            return (summer, date)
    return (False, date)
