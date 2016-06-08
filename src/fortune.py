# -*- python -*-
# See LICENSE file for copyright and license details.

def fortune(max_lines = 5, max_columns = 80, max_tries = 100, file = None):
    '''
    Get random fortune quote
    
    @param   max_lines:int    The maximum number of lines the quote may continue
    @param   max_columns:int  The maximum number of columns the quote may require
    @param   max_tries:int    The maximum number of tries before giving up
    @param   file:str?        The file from which to take the quote
    @return  :str?            The quote in plain text, `None` on error
    '''
    try:
        from subprocess import Popen, PIPE
        import time
        for _ in range(max_tries):
            proc = Popen(['fortune', file] if file is not None else ['fortune'], stdout = PIPE)
            output = proc.communicate()[0].decode('utf-8', 'strict')
            lines = output.split('\n')
            if len(lines) <= max_lines and max(len(x) for x in lines) <= max_columns:
                return output
    except:
        pass
    return None
