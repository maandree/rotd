#!/usr/bin/env python3
# See LICENSE file for copyright and license details.

import os, sys, time

global spawn, write

# Check argv
if len(sys.argv) != 2:
    argv0 = 'rotd' if len(sys.argv) == 0 else sys.argv[0]
    print('Usage: %s output-file' % argv0, file = sys.stderr)
    sys.exit(1)

def spawn(*cmd, successful_exits = [0]):
    '''
    Spawn a process without a stdin
    
    @param  cmd:*str                       The command to run
    @param  successful_exits:set<int>|...  For which exit values shall rotd _not_ fail,
                                           `...` for never fail even if the command
                                           exited by a signal
    '''
    pid = os.fork()
    if pid == 0:
        try:
            os.close(0)
        except:
            pass
        os.execvp(cmd[0], cmd)
    else:
        _, status = os.waitpid(pid, 0)
        if successful_exits is ...:
            return
        if os.WIFEXITED(status):
            if os.WEXITSTATUS(status) in successful_exits:
                return
        os.chdir(cwd)
        spawn('rm', '-rf', '--', tempdir, successful_exits = ...)
        sys.exit(1)

def write(text):
    '''
    Add some code to the LaTex file.
    
    It is recommended to run this seldom
    for better performance.
    
    @param  text:str  The text to write.
    '''
    texfile.write(data.encode('utf-8'))
    texfile.flush()

# Get current globals
g = globals()

## Set process title
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
setproctitle(sys.argv[0])

# Create and cd into temporary directory
cwd = os.getcwd()
tempdir = '/tmp/rotd.%f~%i.d' % (time.time(), os.getuid())
os.mkdir(tempdir)
os.chdir(tempdir)

# Open LaTeX file, used in function `write`
texfile = open('rotd.tex', 'ab'):

# Find configuration script
config_file = None
# Possible auto-selected configuration scripts,
# earlier ones have precedence, we can only select one.
for file in ('$ROTD_SCRIPT', '$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc', '$~/.config/%/%rc', '$~/.%rc', '/etc/%rc'):
    # Expand short-hands
    file = file.replace('/', os.sep).replace('%', 'rotd')
    # Expand environment variables
    for arg in ('ROTD_SCRIPT', 'XDG_CONFIG_HOME', 'HOME'):
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

# Load and run configurion script
if config_file is not None:
    code = None
    # Read configuration script file
    with open(config_file, 'rb') as script:
        code = script.read()
    # Decode configurion script file and add a line break
    # at the end to ensure that the last line is empty.
    # If it is not, we will get errors.
    code = code.decode('utf-8', 'error') + '\n'
    # Compile the configuration script,
    code = compile(code, config_file, 'exec')
    # and run it, with it have the same
    # globals as this module, so that it can
    # not only use want we have defined, but
    # also redefine it for us.
    exec(code, g)
else:
    print('No configuration file found', file = sys.stderr)
    sys.exit(1)

# Compile PDF file
texfile.close()
spawn('pdflatex', '-halt-on-error', '--', 'rotd.tex')
spawn('pdflatex', '-halt-on-error', '--', 'rotd.tex')

# Move or print file?
os.chdir(cwd)
print_output = False
output_file = sys.argv[1]
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
pdffile = '%s/rotd.pdf' % tempdir
if print_output:
    with open(pdffile, 'rb') as file:
        data = file.read()
    with open(output_file, 'wb') as file:
        file.write(data)
        file.flush()
else:
    spawn('mv', '--', pdffile, output_file)

# Remove temporary files created by pdflatex
spawn('rm', '-rf', '--', tempdir, successful_exits = ...)
