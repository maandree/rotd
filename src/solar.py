# -*- python -*-
# See LICENSE file for copyright and license details.

# Requires https://github.com/maandree/solar-python

class Solar:
    def __init__(self, lat = None, lon = None):
        '''
        Constructor
        
        @param  lat:float?  The GPS latitude of your location
        @param  lon:float?  The GPS longitude of your location
        
        If `lon` most be specified iff `lat` is specified. If `lat`
        and `lon` are not specified, `~/.config/geolocation` and
        `/etc/geolocation` are read.
        
        Be aware, and exception is raised if no location has
        been set.
        '''
        if lat is not None:
            self.lat = lat
            self.lon = lon
        else:
            import os, pwd
            filenames = []
            if 'HOME' in os.environ and len(os.environ['HOME']) > 0:
                filenames.append(os.environ['HOME'] + '/.config/geolocation')
            try:
                filenames.append(wd.getpwuid(os.getuid()).pw_dir + '/.config/geolocation')
            except:
                pass
            filenames.append('/etc/geolocation')
            for filename in filenames:
                try:
                    with open(filename, 'rb') as file:
                        loc = file.read().decode('utf-8', 'replace').split('\n')[0]
                    loc = loc.split(' ')
                    if len(loc) != 2:
                        continue
                    self.lat, self.lon = float(loc[0]), float(loc[1])
                    return
                except:
                    pass
            raise Exception('No location set')
    
    
    @staticmethod
    def __jc_to_str(t):
        import time, solar_python
        t = solar_python.julian_centuries_to_epoch(t)
        t = time.localtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)
    
    
    def season(self):
        '''
        Returns whether 'summer' or 'winter'
        
        @return  :str  The current season, either 'summer' or 'winter'
        '''
        import solar_python
        if solar_python.is_summer(self.lat):
            return 'summer'
        else:
            return 'winter'
    
    
    def have_sunrise_and_sunset(self):
        '''
        Do you have both day and night rather than 24-hour
        days or 24-hour nights?
        
        @return  :bool  The answer to the question above
        '''
        import solar_python
        return solar_python.have_sunrise_and_sunset(self.lat)
    
    
    def next_equinox(self):
        '''
        Get the time of the next equinox
        
        Will be off by a few minutes from aa.usno.navy.mil/data/docs/EarthSeasons.php,
        I don't know why, and I don't know which is more correct. Our times are
        calculated using interpolation, I don't know how aa.usno.navy.mil does
        it, but probably with a formula.
        
        @return  :str  The time of the next equinox formatted as '%Y-%m-%d %H:%M:%S'
        '''
        import solar_python
        return Solar.__jc_to_str(solar_python.future_equinox())
    
    
    def next_solstice(self):
        '''
        Get the time of the next solstice
        
        Will be off by a few minutes from aa.usno.navy.mil/data/docs/EarthSeasons.php,
        I don't know why, and I don't know which is more correct. Our times are
        calculated using interpolation, I don't know how aa.usno.navy.mil does
        it, but probably with a formula.
        
        @return  :str  The time of the next solstice formatted as '%Y-%m-%d %H:%M:%S'
        '''
        import solar_python
        return Solar.__jc_to_str(solar_python.future_solstice())
    
    
    def elevations(self, days_offset = 0):
        '''
        Return the time of the astronomical, nautical, and civil dusk and dawns,
        as well as the solar noon and the sunrise and sunset, for the day (local time).
        
        @param   days_offset:int                       The number of days into the future, 0 for today.
        @return  :(:str?, :str?, :str?, :str?, :str,   The time, restrict to the selected day of, in order:
                   :str?, :str?, :str?, :str?)         the astronomical dawn, the nautical dawn, the civil
                                                       dawn, the sunrise, the solar noon, the sunset, the
                                                       the civil dusk, thenautical dusk, and the astronomical
                                                       dusk. (Those are in chronological order.) If such
                                                       condition is not meet during the day, `None` is
                                                       returned in place. Solar noon is guaranteed (I think.)
                                                       Times are formatted in '%Y-%m-%d %H:%M:%S'.
        '''
        import solar_python as s, time
        tz = -(time.timezone, time.altzone)[time.localtime().tm_isdst]
        a_day = 60 * 60 * 24
        t = time.time()
        t += tz
        t -= t % a_day
        t -= tz
        t += days_offset * a_day
        start = s.epoch_to_julian_centuries(t)
        end = s.epoch_to_julian_centuries(t + a_day)
        t1 = s.future_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_ASTRONOMICAL_DUSK_DAWN, start)
        t2 = s.future_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_NAUTICAL_DUSK_DAWN, start)
        t3 = s.future_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_CIVIL_DUSK_DAWN, start)
        t4 = s.future_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_SUNSET_SUNRISE, start)
        t5a = s.future_elevation_derivative(self.lat, self.lon, 0, start)
        t5b = s.future_elevation_derivative(self.lat, self.lon, 0, t5a + 0.000001)
        t6 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_SUNSET_SUNRISE, end)
        t7 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_CIVIL_DUSK_DAWN, end)
        t8 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_NAUTICAL_DUSK_DAWN, end)
        t9 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_ASTRONOMICAL_DUSK_DAWN, end)
        e1 = s.solar_elevation(self.lat, self.lon, t5a)
        e2 = s.solar_elevation(self.lat, self.lon, t5b)
        t5 = t5a if e1 > e2 else t5b
        t = (t1, t2, t3, t4, t5, t6, t7, t8, t9)
        return tuple(Solar.__jc_to_str(x) if x is not None and start <= x <= end else None for x in t)
    
    
    def lengths(self, today, tomorrow, format = '%ih %i\' %i\'\'', solar_noon_string = ''):
        '''
        Calculate the length of the day and night, measures from
        astronomical dawn/dusk, nautical dawn/dusk, civil dawn/dusk,
        and sunrise/sunset.
        
        @param   today:(str?{4}, str, str?{4})      Values returned for `self.elevations(n)`,
                                                    where `n` is any integer
        @param   tomorrow,:(str?{4}, str, str?{4})  Values returned for `self.elevations(n + 1)`,
                                                    where `n` is the same as in `today`
        @param   format:str?                        The format for the returned strings,
                                                    must take three integers, in order:
                                                    hours, minutes, and seconds, or
                                                    `None` if the total seconds shall be
                                                    returned as integers
        @param   solar_noon_string:str?             The strings to return in the middle of the
                                                    returned tuple, `None` if it should be omitted
        @return  :(str{9|8})|(int{9|8})             0: The duration between astronomical dawn and
                                                       astronomical dusk
                                                    1: The duration between nautical dawn and
                                                       nautical dusk
                                                    2: The duration between civil dawn and civil dusk
                                                    3: The duration between sunrise and sunset
                                                    4: `solar_noon_string`, omitted if
                                                       `solar_noon_string` is `None`
                                                    5: The duration between sunset and sunrise
                                                    6: The duration between civil dusk and civil dawn
                                                    7: The duration between astronomical dusk and
                                                       astronomical dawn
                                                    8: The duration between nautical dusk and
                                                       nautical dawn
        '''
        seconds  = lambda h, m, s : int(h) * 60 * 60 + int(m) * 60 + int(s)
        today    = [None if x is None else seconds(*(x.split(' ')[1].split(':'))) for x in today]
        tomorrow = [None if x is None else seconds(*(x.split(' ')[1].split(':'))) for x in tomorrow]
        one_day  = 24 * 60 * 60
        for L in (today, tomorrow):
            for i in range(5, 9):
                if L[i] is None:
                    L[i] = one_day
            for i in reversed(range(0, 4)):
                if L[i] is None:
                    L[i] = 0
        for i in range(0, 9):
            tomorrow[i] += one_day
        def strise(s):
            if format is None:
                return s
            m, s = s // 60, s % 60
            h, m = m // 60, m % 60
            return format % (h, m, s)
        day = [strise(today[8] - today[0]),
               strise(today[7] - today[1]),
               strise(today[6] - today[2]),
               strise(today[5] - today[3])]
        noon = [] if solar_noon_string is None else [solar_noon_string]
        night = [strise(tomorrow[3] - today[5]),
                 strise(tomorrow[2] - today[6]),
                 strise(tomorrow[1] - today[7]),
                 strise(tomorrow[0] - today[8])]
        return tuple(day + noon + night)
    
    
    def hours(self, elevations, days_offset = 0, format = '%ih %i\' %i\'\''):
        '''
        Calculates the time and duration when the Sun's elevation is in
        a specific range. We will call this the X hour. Both the morning
        X hour and evening X hour is calculated. These may in fact be the
        same.
        
        @param  days_offset:int  The number of days into the future, 0 for today
        @param  :(float, float)  The Sun's lowest (first element) and highest
                                 (second element) elevation during the X hour
        @param  format:str?      The format for the returned strings, must take
                                 three integers, in order: hours, minutes, and
                                 seconds, or `None` if the total seconds shall be
                                 returned as integers
        @param  :(str?, str?, str|int, str?, str?, str|int)
                                 0: The beginning of the morning X hour
                                 1: The end of the morning X hour
                                 2: The duration of the morning X hour
                                 3: The beginning of the evening X hour
                                 4: The end of the evening X hour
                                 5: The duration of the evening X hour
        '''
        import solar_python as s, time
        tz = -(time.timezone, time.altzone)[time.localtime().tm_isdst]
        a_day = 60 * 60 * 24
        t = time.time()
        t += tz
        t -= t % a_day
        t -= tz
        t += days_offset * a_day
        start = s.epoch_to_julian_centuries(t)
        end = s.epoch_to_julian_centuries(t + a_day)
        t1 = s.future_elevation(self.lat, self.lon, elevations[0], start)
        t2 = s.future_elevation(self.lat, self.lon, elevations[1], start)
        t3 = s.past_elevation(self.lat, self.lon, elevations[1], end)
        t4 = s.past_elevation(self.lat, self.lon, elevations[0], end)
        (t1, t2, t3, t4) = tuple(x if x is not None and start <= x <= end else None for x in (t1, t2, t3, t4))
        if t2 is None:
            t2 = t4
        if t3 is None:
            t3 = t1
        def dur(a, z):
            if a is None and z is None:
                e = s.solar_elevation(self.lat, self.lon, (start + end) / 2)
                if elevations[0] <= e <= elevations[1]:
                    return s.julian_centuries_to_epoch(end) - s.julian_centuries_to_epoch(start)
                return 0
            elif a is None and z is not None:
                return s.julian_centuries_to_epoch(z) - s.julian_centuries_to_epoch(start)
            elif a is not None and z is None:
                return s.julian_centuries_to_epoch(end) - s.julian_centuries_to_epoch(a)
            else:
                return s.julian_centuries_to_epoch(z) - s.julian_centuries_to_epoch(a)
        d12 = dur(t1, t2)
        d34 = dur(t3, t4)
        (t1, t2, t3, t4) = tuple(Solar.__jc_to_str(x) if x is not None else None for x in (t1, t2, t3, t4))
        def strise(s):
            if format is None:
                return int(s)
            m, s = s // 60, s % 60
            h, m = m // 60, m % 60
            return format % (h, m, s)
        return (t1, t2, strise(d12), t3, t4, strise(d34))


    def golden_hour(self, days_offset = 0, format = '%ih %i\' %i\'\''):
        '''
        Calculates the morning and evening (can be the same) golden hour
        
        @param  days_offset:int  The number of days into the future, 0 for today
        @param  format:str?      The format for the returned strings, must take
                                 three integers, in order: hours, minutes, and
                                 seconds, or `None` if the total seconds shall be
                                 returned as integers
        @param  :(str?, str?, str|int, str?, str?, str|int)
                                 0: The beginning of the morning golden hour
                                 1: The end of the morning golden hour
                                 2: The duration of the morning golden hour
                                 3: The beginning of the evening golden hour
                                 4: The end of the evening golden hour
                                 5: The duration of the evening golden hour
        '''
        from solar_python import SOLAR_ELEVATION_RANGE_GOLDEN_HOUR as elevs
        return self.hours(elevs, days_offset = days_offset, format = format)


    def blue_hour(self, days_offset = 0, format = '%ih %i\' %i\'\''):
        '''
        Calculates the morning and evening (can be the same) blue hour
        
        @param  days_offset:int  The number of days into the future, 0 for today
        @param  format:str?      The format for the returned strings, must take
                                 three integers, in order: hours, minutes, and
                                 seconds, or `None` if the total seconds shall be
                                 returned as integers
        @param  :(str?, str?, str|int, str?, str?, str|int)
                                 0: The beginning of the morning blue hour
                                 1: The end of the morning blue hour
                                 2: The duration of the morning blue hour
                                 3: The beginning of the evening blue hour
                                 4: The end of the evening blue hour
                                 5: The duration of the evening blue hour
        '''
        from solar_python import SOLAR_ELEVATION_RANGE_BLUE_HOUR as elevs
        return self.hours(elevs, days_offset = days_offset, format = format)

