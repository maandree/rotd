# -*- python -*-
# See LICENSE file for copyright and license details.

def filter_events(events, inclusion_period = 10):
    '''
    Filter a list of events to only include events that will happen soon
    
    @param   events:itr<(data:¿D?, date:str)>        List of events, each element shall be 2-tuple,
                                                     where the first element will be passed unmodified
                                                     in the return, the second element shall be the
                                                     date in %Y-%m-%d or %m-%d format
    @return  :list<(data:¿D?, days:int, date:date)>  Events that will happen soon
                                                       data: unmodifid data passed via `events`
                                                       day: the number of days until the event occurs
                                                            0 if today
                                                       date: a date structure of the date it event occurs
    '''
    try:
        import time
        now = time.localtime()
        year = now.tm_year
        tz = time.strftime('%z', now)
        tz = (int(tz[:3]) * 60 + int(tz[:1] + tz[3:])) * 60
        now = int(time.strftime('%s', now))
        a_day = 60 * 60 * 24
        rc = []
        more_events = []
        for evs in (events, more_events):
            for data, date in evs:
                if len(date.split('-')) == 2:
                    more_events.append((data, '%i-%s' % (year + 1, date)))
                    date = '%i-%s' % (year, date)
                date = time.strptime(date, '%Y-%m-%d')
                days = (int(time.strftime('%s', date)) + tz) // a_day - now // a_day
                if days >= 0 and days < inclusion_period:
                    rc.append((data, days, date))
        rc.sort(key = lambda x : x[1])
        return rc
    except Exception as e:
        raise e
        return None


def first_weekday(weekday, first, extra_days = 0):
    import time
    date = time.strptime(first, '%Y-%m-%d')
    diff = weekday - date.tm_wday
    if diff < 0:
        diff += 7
    year, mon, mday = date.tm_year, date.tm_mon, date.tm_mday + diff + extra_days
    return date_to_string(year, mon, mday)


def weekday_in_week(weekday, year, mon, week, extra_days = 0):
    import time
    date = time.strptime('%i-%02i-01' % (year, mon), '%Y-%m-%d')
    mday = 1 - date.tm_wday + 7 * (week - 1) + extra_days
    return date_to_string(year, mon, mday)


def date_to_string(year, mon, mday):
    feb = 29 if year % 400 == 0 or (year % 4 == 0 and not year % 100 == 0) else 28
    maxday = (0, 31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[mon]
    while mday <= 0:
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
            feb = 29 if year % 400 == 0 or (year % 4 == 0 and not year % 100 == 0) else 28
        maxday = (0, 31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[mon]
        mday += maxday
    while mday > maxday:
        mday -= maxday
        mon += 1
        if mon == 13:
            mon = 1
            year += 1
            feb = 29 if year % 400 == 0 or (year % 4 == 0 and not year % 100 == 0) else 28
        maxday = (0, 31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[mon]
    return '%i-%02i-%02i' % (year, mon, mday)


def western_easter(year):
    '''
    Get the date of the Western Easter
    
    @param   year:int               The year
    @return  :(month:int, day:int)  The month and the day when easter occurs
    '''
    a = year % 19;
    b = year // 100;
    c = year % 100;
    d = b // 4;
    e = b % 4;
    f = (b + 8) // 25;
    g = (b - f + 1) // 3;
    h = (19 * a + b - d - g + 15) % 30;
    i = c // 4;
    k = c % 4;
    l = (32 + 2 * e + 2 * i - h - k) % 7;
    m = (a + 11 * h + 22 * l) // 451;
    n = (h + l - 7 * m + 114) // 31;
    p = (h + l - 7 * m + 114) % 31;
    return (n, p + 1)


def swedish_holidays():
    '''
    Return a list of Swedish holidays than can be filtered with `filter_events`
    
    @return  :list<(title:str, date:str)>  See `filter_events`
    '''
    import time
    year = time.localtime().tm_year
    rc = []
    for y in (year, year + 1):
        (em, ed) = western_easter(y)
        rc.append(('Nyårsdagen',             '%i-01-01' % y))
        rc.append(('Trettondedag jul',       '%i-01-06' % y))
        rc.append(('Första maj',             '%i-05-01' % y))
        rc.append(('Sveriges nationaldag',   '%i-06-06' % y))
        rc.append(('Juldagen',               '%i-12-25' % y))
        rc.append(('Annandag jul',           '%i-12-26' % y))
        rc.append(('Midsommardagen',         first_weekday(5, '%i-06-20' % y)))
        rc.append(('Alla helgons dag',       first_weekday(5, '%i-10-31' % y)))
        rc.append(('Annandag påsk',          date_to_string(y, em, ed + 1)))
        rc.append(('Långfredagen',           date_to_string(y, em, ed - 2)))
        rc.append(('Kristi himmelsfärdsdag', date_to_string(y, em, ed + 4 + 5 * 7)))
    rc.sort(key = lambda x : x[1])
    return rc


def swedish_events(only_common = False):
    '''
    Return a list of special non-holiday days (more or less often)
    celibrated in Sweden, the list can be filtered with `filter_events`.
    
    Some days have been excluded. This is because they do not
    occur on predicatable days, and I'm not going to look for
    some source where it can be queried. Please, when you add
    new days we all should celibrate, give them a fixed date!
    
    @return  :list<(title:str, date:str)>  See `filter_events`
    '''
    import time
    year = time.localtime().tm_year
    rc = []
    for y in (year, year + 1):
        (em, ed) = western_easter(y)
        rc.append(('Trettondagsafton',            '%i-01-05' % y))
        rc.append(('Alla hjärtans dag',           '%i-02-14' % y))
        rc.append(('Internationella kvinnodagen', '%i-03-08' % y))
        rc.append(('Första april',                '%i-04-01' % y))
        rc.append(('Valborgsmässoafton',          '%i-04-30' % y))
        rc.append(('Första maj',                  '%i-05-01' % y))
        rc.append(('Midsommarafton',              first_weekday(4, '%i-06-19' % y)))
        rc.append(('Lucia',                       '%i-12-13' % y))
        rc.append(('Julafton',                    '%i-12-24' % y))
        rc.append(('Allhelgonaafton',             first_weekday(4, '%i-10-30' % y)))
        rc.append(('Nyårsafton',                  '%i-12-31' % y))
        rc.append(('Skärtorsdagen',               date_to_string(y, em, ed - 3)))
        rc.append(('Påskdagen',                   date_to_string(y, em, ed)))
        rc.append(('Påskafton',                   date_to_string(y, em, ed - 1)))
        rc.append(('Pingstdagen',                 date_to_string(y, em, ed + 7 * 7)))
        rc.append(('Pingstafton',                 date_to_string(y, em, ed + 7 * 7 - 1)))
        rc.append(('Fettisdagen',                 date_to_string(y, em, ed - 47)))
        rc.append(('Första söndagen i advent',    first_weekday(6, '%i-11-27' % y)))
        rc.append(('Andra söndagen i advent',     first_weekday(6, '%i-12-04' % y)))
        rc.append(('Tredje söndagen i advent',    first_weekday(6, '%i-12-11' % y)))
        rc.append(('Fjärde söndagen i advent',    first_weekday(6, '%i-12-18' % y)))
        if not only_common:
            rc.append(('Palmsöndagen',                                  date_to_string(y, em, ed - 7)))
            rc.append(('Förintelsens minnesdag',                        '%i-01-27' % y))
            rc.append(('Världsreligionsdagen',                          first_weekday(6, '%i-01-01' % y, 6 * 7)))
            rc.append(('Darwindagen',                                   '%i-02-12' % y))
            rc.append(('Internationella modersmålsdagen',               '%i-02-21' % y))
            if y % 400 == 0 or (y % 4 == 0 and not y % 100 == 0):
                rc.append(('Föredetta skottdagen',                      '%i-02-24' % y))
            rc.append(('Kyndelsmässodagen',                             '%i-02-02' % y))
            rc.append(('Sverigefinnarnas dag',                          '%i-02-24' % y))
            rc.append(('Internationella vattendagen',                   '%i-03-22' % y))
            rc.append(('Matematikens dag (Pi-dagen)',                   '%i-03-14' % y))
            rc.append(('Nordens dag',                                   '%i-03-23' % y))
            rc.append(('Jungfru Marie bebådelsedag',                    first_weekday(6, '%i-03-22' % y)))
            rc.append(('Världsböndagen för fred',                       first_weekday(4, '%i-03-01' % y)))
            rc.append(('Världspoesidagen',                              '%i-03-21' % y))
            rc.append(('Dansens dag',                                   '%i-04-29' % y))
            rc.append(('Försöksdjurens dag',                            '%i-04-24' % y))
            rc.append(('Jordens dag',                                   '%i-04-22' % y))
            rc.append(('Världens konstdag',                             '%i-04-15' % y))
            rc.append(('Världshälsodagen',                              '%i-04-07' % y))
            rc.append(('Europadagen/Segerdagen',                        '%i-05-09' % y))
            rc.append(('Handduksdagen',                                 '%i-05-25' % y))
            rc.append(('Internationella dagen för biologisk mångfald',  '%i-05-22' % y))
            rc.append(('Internationella familjedagen',                  '%i-05-15' % y))
            rc.append(('Internationella fredssoldatdagen/Veterandagen', '%i-05-29' % y))
            rc.append(('Jungfru Marie besökelsedag',                    '%i-05-31' % y))
            rc.append(('Tobaksfria dagen',                              '%i-05-31' % y))
            rc.append(('Världsdagen för pressfrihet',                   '%i-05-03' % y))
            rc.append(('Internationella heraldikdagen',                 '%i-06-10' % y))
            rc.append(('Mobilfria dagen',                               '%i-06-01' % y))
            rc.append(('Världsmiljödagen',                              '%i-06-05' % y))
            rc.append(('Den helige Johannes Döparens dag',              first_weekday(6, '%i-06-21' % y)))
            rc.append(('Tau-dagen',                                     '%i-06-28' % y))
            rc.append(('Mandeladagen',                                  '%i-07-18' % y))
            rc.append(('Sjusovardagen',                                 '%i-07-27' % y))
            rc.append(('Victoriadagen',                                 '%i-07-14' % y))
            rc.append(('Europeisk minnesdag för stalinismens och nazismens offer', '%i-08-23' % y))
            rc.append(('Jungfru Marie himmelsfärd',                     '%i-08-15' % y))
            rc.append(('Raoul Wallenbergs dag',                         '%i-08-27' % y))
            rc.append(('Vänsterhäntas dag',                             '%i-08-13' % y))
            rc.append(('Det heliga korsets upphöjelse',                 '%i-09-14' % y))
            rc.append(('Europeiska språkdagen',                         '%i-09-26' % y))
            rc.append(('Geologins dag',                                 first_weekday(5, '%i-09-01' % y, 7)))
            rc.append(('Internationella bilfria dagen',                 '%i-09-22' % y))
            rc.append(('Internationella fredsdagen',                    '%i-09-21' % y))
            rc.append(('Jungfru Marie födelse',                         '%i-09-08' % y))
            rc.append(('Jungfru Marie heliga namn',                     '%i-09-12' % y))
            rc.append(('Software Freedom Day',                          '%i-09-19' % y))
            rc.append(('Djurens dag',                                   '%i-10-04' % y))
            rc.append(('FN-dagen',                                      '%i-10-24' % y))
            rc.append(('Internationella dagen för utrotande av fattigdom', '%i-10-17' % y))
            rc.append(('Internationella flickdagen',                    '%i-10-11' % y))
            rc.append(('Internationella handtvättsdagen',               '%i-10-15' % y))
            rc.append(('Internationella stamningsdagen',                '%i-10-22' % y))
            rc.append(('Kanelbullens dag',                              '%i-10-04' % y))
            rc.append(('Lantbruksdjurens dag',                          '%i-10-02' % y))
            rc.append(('Vegetariska världsdagen',                       '%i-10-01' % y))
            rc.append(('Världshungerdagen',                             '%i-10-16' % y))
            rc.append(('Alla själars dag',                              '%i-11-02' % y))
            rc.append(('Allhelgonadagen',                               '%i-11-01' % y))
            rc.append(('Arkivens dag',                                  first_weekday(5, '%i-11-01' % y, 7)))
            rc.append(('Gustav Adolfsdagen',                            '%i-11-06' % y))
            rc.append(('Internationella dagen mot våld mot kvinnor',    '%i-11-25' % y)) # déjà vu...
            rc.append(('Internationella filosofidagen',                 first_weekday(3, '%i-11-01' % y, 2 * 7)))
            rc.append(('Internationella mansdagen',                     '%i-11-19' % y))
            rc.append(('Internationella solidaritetsdagen med det palestinska folket', '%i-11-29' % y))
            rc.append(('Internationella vegandagen',                    '%i-11-01' % y)) # demi-déju vu...
            rc.append(('Kåldolmens dag',                                '%i-11-30' % y))
            rc.append(('Mårtensafton',                                  '%i-11-10' % y))
            rc.append(('Stilleståndsdagen',                             '%i-11-11' % y))
            rc.append(('Världsdiabetesdagen',                           '%i-11-14' % y))
            rc.append(('Söndagen före domssöndagen',                    first_weekday(6, '%i-11-13' % y)))
            rc.append(('Söndagen efter Alla helgons dag',               first_weekday(5, '%i-10-31' % y, 1)))
            rc.append(('Internationella GIS-dagen',                     weekday_in_week(2, y, 10, 3)))
            rc.append(('Internationella dagen för mänskliga rättigheter', '%i-12-10' % y))
            rc.append(('Internationella volontärdagen',                 '%i-12-05' % y))
            rc.append(('Tangons dag',                                   '%i-12-11' % y))
            rc.append(('Världs-AIDS-dagen',                             '%i-12-01' % y))
            rc.append(('Värnlösa barns dag',                            '%i-12-28' % y))
    rc.sort(key = lambda x : x[1])
    return rc
