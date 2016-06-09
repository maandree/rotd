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
        Get the time of the next equinox.
        
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
        Get the time of the next solstice.
        
        Will be off by a few hours from aa.usno.navy.mil/data/docs/EarthSeasons.php,
        I don't know why, and I don't know which is more correct. Our times are
        calculated using interpolation, I don't know how aa.usno.navy.mil does
        it, but probably with a formula.
        
        @return  :str  The time of the next solstice formatted as '%Y-%m-%d %H:%M:%S'
        '''
        import solar_python
        return Solar.__jc_to_str(solar_python.future_solstice())

    
    # TODO solar noon
    # TODO sunrise/sunset
    # TODO civil dusk/dawn
    # TODO nautical dusk/dawn
    # TODO astronomical dusk/dawn

