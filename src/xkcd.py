# -*- python -*-
# See LICENSE file for copyright and license details.

def xkcd(index = None, abort_timer = 2):
    '''
    Get XKCD comic
    
    @param   index:int?       The index comic, `None` for the last one
    @param   abort_timer:int  The number of seconds to wait before giving up
    @return  :(index:int, img:str, title:str, text:str)
                              Information about the comic
                                index: The index of the fetched comic
                                img:   The URL of comic image
                                title: The comic's title
                                text:  The text that appears when in the comic's
                                       tool tip text on the web page
    '''
    from __main__ import spawn
    import html
    url = 'https://xkcd.com/'
    if index is not None:
        url += str(index) + '/'
    page = spawn('curl', url, abort_timer = abort_timer, get_stdout = True)
    page = page.decode('utf-8', 'strict').split('\n')
    if index is None:
        [index, _] = [line for line in page if '<a ' in line and 'rel="prev"' in line]
        [index] = [word for word in index.split(' ') if word.startswith('href="/')]
        index = int(''.join(c for c in index if c in '0123456789')) + 1
    [n] = [i for i, line in enumerate(page) if 'id="comic"' in line]
    page = [line for line in page[n:] if '<img ' in line][0]
    page = ' '.join((page[:-2] + ' ').split(' ')[1:])
    page = page.split('" ')
    attrs = [attr.split('="') for attr in page[:-1]]
    attrs = dict((key, html.unescape(value)) for [key, value] in attrs)
    img = attrs['src']
    if img.startswith('//'):
        img = 'https:' + img
    elif img.startswith('/'):
        img = 'https://xkcd.com' + img
    else:
        while url.endswith('/'):
            url = url[:-1]
        proto, url = url.split('//')[0], '//'.join(url.split('//')[1:])
        domain, url = url.split('/')[0], '/'.join(url.split('/')[1 : -1])
        if len(url) > 0:
            url = url + '/'
        img = '%s//%s/%s%s' % (proto, domain, url, img)
    return (index, img, attrs['alt'], attrs['title'])
