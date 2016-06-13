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
        
        Will be off by a few hours from aa.usno.navy.mil/data/docs/EarthSeasons.php,
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
        
        Will be off by a few hours from aa.usno.navy.mil/data/docs/EarthSeasons.php,
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
        t5 = s.future_elevation_derivative(self.lat, self.lon, 0, start)
        t5 = s.future_elevation_derivative(self.lat, self.lon, 0, t5 + 0.000001)
        t6 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_SUNSET_SUNRISE, end)
        t7 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_CIVIL_DUSK_DAWN, end)
        t8 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_NAUTICAL_DUSK_DAWN, end)
        t9 = s.past_elevation(self.lat, self.lon, s.SOLAR_ELEVATION_ASTRONOMICAL_DUSK_DAWN, end)
        t = (t1, t2, t3, t4, t5, t6, t7, t8, t9)
        return tuple(Solar.__jc_to_str(x) if x and start <= x <= end is not None else None for x in t)
