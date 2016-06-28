# -*- python -*-
# See LICENSE file for copyright and license details.

def wotd(lang = 'en', abort_timer = 2):
    '''
    Get Wiktionary's word of the day
    
    @param   lang:str         The language code. Supported languages codes:
                                en  English (word of the day)
                                sv  Swedish (word of the week)
    @param   abort_timer:int  The number of seconds before giving up
    @return  :str?            The word of the day, in LaTeX, `None` on error
    '''
    from __main__ import spawn, LIBEXEC
    try:
        text = spawn('%s/rotd-wotd-%s' % (LIBEXEC, lang), abort_timer = abort_timer, get_stdout = True)
        text = text.decode('utf-8', 'strict')
        return text
    except:
        return None
