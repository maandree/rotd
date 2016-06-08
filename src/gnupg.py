# -*- python -*-
# See LICENSE file for copyright and license details.

def gnupg_expiry(warn_period = 30):
    '''
    Get a list of all secret keys that will expire soon
    
    @param   warn_peroid:int     The number of days to warn before the key expires
    @return  :list<(str, int)>?  List of key–days pairs. Each element is 2-tuple,
                                 where the first tuple-element is the key ID, and
                                 then second tuple-element is the number of days
                                 before the key exires. `None` is returned on error.
    '''
    try:
        from subprocess import Popen, PIPE
        import time
        proc = Popen(['gpg', '--list-secret-keys'], stdout = PIPE)
        output = proc.communicate()[0].decode('utf-8', 'strict')
        output = output.split('\n')
        output = [x.split('/')[1].split(' ') for x in output if x.startswith('sec') and 'expires' in x]
        output = [(x[0], x[4][:-1]) for x in output]
        rc = []
        now = time.time()
        warn_period = warn_period * 60 * 60 * 24
        for key, expiry in output:
            expiry = float(time.strftime('%s', time.strptime(expiry, '%Y-%m-%d'))) - now
            if expiry >= 0 and expiry < warn_period:
                rc.append((key, int(expiry) // 60 // 60 // 24))
        rc.sort(key = lambda x : x[1])
        return rc
    except:
        return None
