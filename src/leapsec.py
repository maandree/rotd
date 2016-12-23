# -*- python -*-
# See LICENSE file for copyright and license details.

def leap_seconds(abort_timer = 2):
    '''
    Return a list of all leapsecond announcements (possibly including
    retroactive announcements), the list can be filtered with `events.filter_events`
    
    @param   abort_timer:int               The number of seconds to wait before giving up
    @return  :list<((u:, l: n:, k:), d:)>  List of announcements.
                                             u: UTC-time as (year, month, day, hour, minute)-tuple
                                             l: local time as (year, month, day, hour, minute)-tuple
                                             n: the number of leap seconds, either negative or positive
                                             k: either 'primary', 'secondarty', or 'out-of-band',
                                                describes the announcement slot
                                             d: the local time as a %Y-%m-%d formatted string
    '''
    from __main__ import spawn
    import time
    try:
        #url = 'http://maia.usno.navy.mil/ser7/leapsec.dat'
        url = 'https://oceandata.sci.gsfc.nasa.gov/Ancillary/LUTs/modis/leapsec.dat'
        annons = spawn('curl', url, abort_timer = abort_timer, get_stdout = True)
        annons = annons.decode('utf-8', 'strict')
        while not annons.startswith(' '):
            annons = '\n'.join(annons.split('\n')[1:])
        while '  ' in annons:
            annons = annons.replace('  ', ' ')
            annons = annons.replace('= ', '=').replace('=JD ', '=JD')
        annons = [annon.lstrip().split(' ') for annon in annons.split('\n') if not annon == '']
        test = lambda annon : annon.startswith('TAI-UTC=') or annon.startswith('UTC-TAI=')
        annons = [annon[:3] + list(filter(test, annon)) for annon in annons]
        MONTHS = { 'JAN' : 1
                 , 'FEB' : 2
                 , 'MAR' : 3
                 , 'APR' : 4
                 , 'MAY' : 5
                 , 'JUN' : 6
                 , 'JUL' : 7
                 , 'AUG' : 8
                 , 'SEP' : 9
                 , 'OCT' : 10
                 , 'NOV' : 11
                 , 'DEC' : 12
                 }
        DAYS_OF_MONTHS = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        def days(year, mon):
            rc = DAYS_OF_MONTHS[mon]
            if mon == 2:
                if (year % 4 == 0 and not year % 100 == 0) or year % 400 == 0:
                    rc += 1
            return rc
        def get_local_time(utctime, tz):
            year, mon, mday, hour, minute = utctime
            tzh, tzm = tz // 60 // 60, (tz // 60) % 60
            hour, minute = hour + tzh, minute + tzm
            if minute >= 60:
                hour, minute = hour + 1, minute - 60
            if minute < 0:
                hour, minute = hour - 1, minute + 60
            if hour >= 24:
                mday, hour = mday + 1, hour - 24
                if mday > days(year, mon):
                    mon, mday = mon + 1, 1
                    if mon == 13:
                        year, mon = year + 1, 1
            if hour < 0:
                mday, hour = mday - 1, hour + 24
                if mday == 0:
                    mon -= 1
                    if mon == 0:
                        year, mon = year - 1, 12
                    mday = days(year, mon)
            return (year, mon, mday, hour, minute)
        def timezone(date):
            guessed = time.mktime(time.strptime(date, '%Y-%m-%d'))
            for tzname, tzval in zip(time.tzname, (time.timezone, time.altzone)):
                if time.mktime(time.strptime('%s %s' % (date, tzname), '%Y-%m-%d %Z')) == guessed:
                    return -tzval
            return -time.timezone
        def translate(annon):
            year = int(annon[0])
            mon = MONTHS[annon[1]]
            mday = int(annon[2]) - 1
            amount = annon[3]
            if amount.startswith('TAI-UTC='):
                amount = int(amount.split('=')[1].split('.')[0])
            else:
                amount = -(int(amount.split('=')[1].split('.')[0]))
            kind = 'out-of-band'
            if mday == 0:
                mon -= 1
                if mon == 0:
                    mon = 12
                    year -= 1
                mday = days(year, mon)
                if mon in (6, 12):
                    kind = 'primary'
                elif mon in (3, 9):
                    kind = 'secondary'
            utctime = (year, mon, mday, 23, 59)
            localtime = get_local_time(utctime, time.timezone)
            tz = timezone('%i-%02i-%02i' % localtime[:3])
            localtime = get_local_time(utctime, tz)
            return [utctime, localtime, amount, kind]
        annons = [translate(annon) for annon in annons]
        for i in reversed(range(len(annons) - 1)):
            annons[i + 1][2] -= annons[i][2]
        annons = annons[1:]
        rc = []
        for annon in [annon for annon in annons if annon[2] != 0]:
            rc.append((tuple(annon), '%i-%02i-%02i' % annon[1][:3]))
        return rc
    except:
        return None

def leap_seconds_to_strings(events, local = True, include_date = False, include_desc = False):
    '''
    Convert output from `leap_seconds` to human-friendly output
    that can still be passed to `events.filter_events`
    
    You must have \\usepackage[normalem]{ulem} in our document
    
    @parma   events:            Output from `leap_seconds`
    @param   local:bool         Print the leap seconds in local time rather than UTC
    @param   include_date:bool  Include the date of the leap second in each element
    @param   include_desc:bool  Include the text 'Leap seconds: ' at the beginning of each element
    @return  :list<(str, str)>  A more human-friendly version of `events`
    '''
    rc = []
    KIND = { 'primary'     : ''
           , 'secondary'   : '; secondary slot'
           , 'out-of-band' : '; out-of-band'
           }
    zone = 'local time' if local else 'UTC'
    desc = 'Leap seconds: ' if include_desc else ''
    for (utime, ltime, amount, kind), ldate in events:
        time = (ltime if local else utime)
        date = '%i-%02i-%02i' % time[:3]
        time = '%02i:%02i' % time[3:]
        if amount > 0:
            text = ['%s:%i' % (time, 60 + n) for n in range(amount)]
        else:
            text = ['\\sout{%s:%i}' % (time, 59 - n) for n in reversed(range(-amount))]
        if include_date:
            text = '%s%s %s (%s%s)' % (desc, date, ', '.join(text), zone, KIND[kind])
        else:
            text = '%s%s (%s%s)' % (desc, ', '.join(text), zone, KIND[kind])
        rc.append((text, ldate))
    return rc
