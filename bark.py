#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
"""
bark.py - Log or print given string. If unable to log, print.

    nullpass, 2012
    https://github.com/nullpass/npnutils

Examples:

    # Log 'Hello World' to myapplication.log
    from bark import Bark
    bark = Bark()
    bark.logfile = '/var/log/myapplication.log'
    bark('Hello World.')

    # Print 'Hello World' in log format
    from bark import Bark
    bark = Bark()
    bark.logfile = False
    bark('Hello World.')

    # Disable output
    from bark import Bark
    bark = Bark()
    bark.enabled = False
    bark('Hello World.') # This won't be logged or printed.

    # Or call from command line and use default settings
    $ python ./bark.py hello world
    $ cat ~/log/bark.log
    Sat Aug 11 18:33:45 EDT 2012 bark[4535] hello world

    # See process name, pid, log file and time of __init__
    bark = Bark()
    print(bark)


"""
__version__ = '5.0.0'
import time
import os
from platform import node
import sys
sys.dont_write_bytecode = True

class Bark(object):
    """
    The Mighty Bark Class.

    Bark is a devel-logging tool to make it easier to log and/or print
    messages (usually debug messages) and allows the devel to quickly
    enable/disable those debug messages globally.

    This program was born as a simple function which printed a given
    string to STDOUT and included a locale timestamp. The function kept
    getting copied and re-used in most of my programs so I converted it
    to a module, and eventually a class. Making it a class enabled easy
    setting management for Enable and Bark.logfile.

    """
    def __init__(self):
        """
        Define default settings which are:
            Bark is enabled.
            Log file is saved in ~log/ using name of calling script.
            Default is to log to the log file, not print.
        """
        self.birthday = (
            float(time.time()),
            str(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))
            )
        self.enabled = True
        #
        #
        self.pid = str(os.getpid())
        #
        # Name of file this is running as
        arg0 = str(os.path.basename(sys.argv[0])).replace('.py', '')
        if len(arg0) < 3 or len(arg0) > 255:
            #
            # If arg zero is invalid, name me Python
            arg0 = 'Python'
        #
        # Current executable and PID, like myapp[12345]
        self.logname = '{0}[{1}]'.format(arg0, self.pid)
        #
        # Full path to log file
        self.logfile = '{0}.log'.format(
            os.path.join(os.path.expanduser('~'), 'log', arg0),
            )
        self.this_event = ''

    def __call__(self, this):
        """
        Bark 'this' when the instance is called directly.

        Will attempt to write your bark to your log file. If
        the path leading to that file does not exist or you
        do not have permissions to add it this method will
        report that and print your bark. Any other exception
        will cause a fatal.
        """
        if not self.enabled == True:
            return
        self.this_event = '{now} {hostname} {proc} {this}\n'.format(
            now=time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()),
            hostname=node(),
            proc=self.logname,
            this=this
            )
        if not self.logfile:
            print(self.this_event)
            return
        try:
            with open(self.logfile, 'a') as handle:
                handle.write(self.this_event)
        except (FileNotFoundError, PermissionError) as err:
            print(err)
            print(self.this_event)

    def __str__(self):
        """
        Return process name, pid and time of init.
        """
        return '{0} {1} {2}'.format(self.logname, self.logfile, self.birthday)

    def do(self, this):
        # pylint: disable=invalid-name
        """
        Dep support for old code.
        """
        self('The bark.do(...) method is depricated. Just bark(...)')
        self(this)

    def bark(self, this):
        """
        Dep support for old code.
        """
        self('The bark.bark(...) method is depricated. Just bark(...)')
        self(this)

    def last(self):
        """
        Show last event barked
        """
        self(self.this_event)

def main():
    """
    Accept bark messages via command line.
    Anti-TODO: Don't expand this to accept options via arguments. If you
    need that much complexity use your system's `logger`.
    """
    if not sys.argv[1:] and sys.stdin.isatty():
        sys.exit(1)
    bark = Bark()
    msg = ''
    for arg in sys.argv[1:]:
        msg += str(arg)+' '
    bark(msg)
    return

if __name__ == '__main__':
    main()
