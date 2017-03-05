#!/usr/bin/env python3
# See LICENSE file for copyright and license details.

import os, sys, time

global spawn, write, LIBEXEC

LIBEXEC = os.getcwd() + ('/..' if os.getcwd().endswith('/src') else '') + '/libexec'
#%%%sys.path.insert(0, '%%PLUGINPATH%%')

argv0 = 'rotd' if len(sys.argv) == 0 else sys.argv[0]

def spawn(*cmd, successful_exits = [0], abort_timer = 0, get_stdout = False):
    '''
    Spawn a process without a stdin
    
    @param   cmd:*str                       The command to run
    @param   abort_timer:int                The number of seconds before aborting, 0 for never
    @param   successful_exits:set<int>|...  For which exit values shall rotd _not_ fail,
                                            `...` for never fail even if the command
                                            exited by a signal
    @param   get_stdout:bool|int|str        Should the process's stdout be returned, or
                                            a file descriptor to which to redirect stdout, or
                                            a file name to which to redirect stdout
    @return  :str?                          The process's output to stdout, if `get_stdout`
    '''
    close_this = None
    if isinstance(get_stdout, str):
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_EXCL
        get_stdout = os.open(get_stdout, flags = flags, mode = 0o600)
        close_this = get_stdout
    stdoutfd = None if isinstance(get_stdout, bool) else get_stdout
    get_stdout = get_stdout if isinstance(get_stdout, bool) else False
    if get_stdout:
        r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(0)
        except:
            pass
        if get_stdout:
            os.close(r)
            stdoutfd = w
        if stdoutfd is not None and stdoutfd != 1:
            os.dup2(stdoutfd, 1)
            os.close(stdoutfd)
        if int(abort_timer) > 0:
            import signal
            signal.alarm(int(abort_timer))
        os.execvp(cmd[0], cmd)
    else:
        if close_this is not None:
            os.close(close_this)
        output = None
        if get_stdout:
            os.close(w)
            output = b''
            while True:
                partial = os.read(r, 4096)
                if len(partial) == 0:
                    break
                output += partial
            os.close(r)
        _, status = os.waitpid(pid, 0)
        if successful_exits is ...:
            return output
        if os.WIFEXITED(status):
            if os.WEXITSTATUS(status) in successful_exits:
                return output
        raise Exception('External command failed')

def write(text):
    '''
    Add some code to the LaTex file.
    
    It is recommended to run this seldom
    for better performance.
    
    @param  text:str  The text to write.
    '''
    texfile.write(text.encode('utf-8'))
    texfile.flush()

# Get current globals
g = globals()

# Set process title
def setproctitle(title):
    '''
    Set process title
    
    @param  title:str  The title of the process
    '''
    import ctypes
    try:
        # Remove path, keep only the file,
        # otherwise we get really bad effects, namely
        # the name title is truncates by the number
        # of slashes in the title. At least that is
        # the observed behaviour when using procps-ng.
        title = title.split('/')[-1]
        # Create strng buffer with title
        title = title.encode(sys.getdefaultencoding(), 'replace')
        title = ctypes.create_string_buffer(title)
        if 'linux' in sys.platform:
            # Set process title on Linux
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            libc.prctl(15, ctypes.byref(title), 0, 0, 0)
        elif 'bsd' in sys.platform:
            # Set process title on at least FreeBSD
            libc = ctypes.cdll.LoadLibrary('libc.so.7')
            libc.setproctitle(ctypes.create_string_buffer(b'-%s'), title)
    except:
        pass
setproctitle(argv0)

# Parse command line
def usage():
    print('Usage: %s [-c config-file] output-file' % argv0, file = sys.stderr)
    sys.exit(1)
config_file = None
i, n = 1, len(sys.argv)
while i < n:
    arg = sys.argv[i]
    if arg.startswith('--'):
        i += 1
        break
    elif arg.startswith('-'):
        if arg.startswith('-c'):
            if arg == '-c':
                if i == n:
                    usage()
                i += 1
                config_file = sys.argv[i]
            else:
                config_file = arg[2:]
        else:
            usage()
    else:
        break
    i += 1
if i + 1 != n:
    usage()
output_file = sys.argv[i]

# Find configuration script
if config_file is None:
    # Possible auto-selected configuration scripts,
    # earlier ones have precedence, we can only select one.
    for file in ('$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc', '$~/.config/%/%rc', '$~/.%rc', '/etc/%rc'):
        # Expand short-hands
        file = file.replace('/', os.sep).replace('%', 'rotd')
        # Expand environment variables
        for arg in ('XDG_CONFIG_HOME', 'HOME'):
            # Environment variables are prefixed with $
            if '$' + arg in file:
                if arg in os.environ:
                    # To be sure that do so no treat a $ as a variable prefix
                    # incorrectly we replace any $ in the value of the variable
                    # with NUL which is not a value pathname character.
                    file = file.replace('$' + arg, os.environ[arg].replace('$', '\0'))
                else:
                    file = None
                    break
        # Proceed if there where no errors
        if file is not None:
            # With use $~ (instead of ~) for the user's proper home
            # directroy. HOME should be defined, but it could be missing.
            # It could also be set to another directory.
            if file.startswith('$~'):
                import pwd
                # Get the home (also known as initial) directory
                # of the real user, and the rest of the path
                file = pwd.getpwuid(os.getuid()).pw_dir + file[2:]
            # Now that we are done we can change back any NUL to $:s
            file = file.replace('\0', '$')
            # If the file we exists,
            if os.path.exists(file):
                # select it,
                config_file = file
                # and stop trying files with lower precedence.
                break
if config_file is None:
    print('No configuration file found', file = sys.stderr)
    sys.exit(1)
config_file = os.path.realpath(config_file)

# Create temporary directory
cwd = os.getcwd()
tempdir = '/tmp/rotd.%f~%i.d' % (time.time(), os.getuid())
os.mkdir(tempdir)

# Fork to ensure cleanup
pid = os.fork()
if pid != 0:
    # Block signals
    import signal
    mask = [x for x in range(1, signal.NSIG) if x != signal.SIGCHLD]
    signal.pthread_sigmask(signal.SIG_BLOCK, mask)
    # Wait of child to die
    pid, status = os.waitpid(pid, 0)
    # Remove temporary files
    spawn('rm', '-rf', '--', tempdir, successful_exits = ...)
    # Unblock signals
    signal.pthread_sigmask(signal.SIG_UNBLOCK, mask)
    # Die like the child (if we are still alive)
    sys.exit(os.WEXITSTATUS(status))

# Open LaTeX file, used in function `write`
os.chdir(tempdir)
texfile = open('rotd.tex', 'ab')

# Read configuration script file
with open(config_file, 'rb') as script:
    code = script.read()
# Decode configurion script file and add a line break
# at the end to ensure that the last line is empty.
# If it is not, we will get errors.
code = code.decode('utf-8', 'strict') + '\n'
# Compile the configuration script,
code = compile(code, config_file, 'exec')
# Run script
exec(code, g)

# Compile PDF file
texfile.close()
spawn('pdflatex', '-halt-on-error', '--', 'rotd.tex')
spawn('pdflatex', '-halt-on-error', '--', 'rotd.tex')

# Move or print file?
print_output = False
if output_file[:1] == '/':
    while output_file[:1] == '/':
        output_file = output_file[1:]
    if output_file in ('dev/', 'proc/'):
        print_output = True
    output_file = sys.argv[1]
elif output_file == '-':
    print_output = True
    output_file = '/dev/stdout'

# Move or print file!
os.chdir(cwd)
pdffile = '%s/rotd.pdf' % tempdir
if print_output:
    with open(pdffile, 'rb') as file:
        data = file.read()
    with open(output_file, 'wb') as file:
        file.write(data)
        file.flush()
else:
    spawn('mv', '--', pdffile, output_file)
