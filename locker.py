# -*- coding: utf-8 -*-
"""
locker.py - Provide easy lock file management as a class for other Python programs.

    by: nullpass, 2012-2015+; based loosely on gekitsuu's Mutex().

    Tested with Python 2.6.6 and 3.4.2.

"""

__version__ = '0.4.b'
import time
import os
from platform import node
import sys


class Locker(object):
    """
    Examples, try to create a lock file using default settings (see __init__)

        my_lock_file = Locker()
        if my_lock_file.create():
            #
            # code that requires a lock file here
            #
            my_lock_file.delete()


    Example, try to create a lock file using a custom pid file. Allow a previous instance to be killed. Set
        maximum age of the lock file to be 999999999 seconds, and explicitly define the name of the process to look for.

        my_lock_file = Locker(file='/var/run/custom.pid', age_limit = 999999999, kill=True, name='bob.py')
        if my_lock_file.create():
            print('I made a lock file')
            print(my_lock_file.log)
        else:
            print('unable to create lock file')
            print(my_lock_file.log)


    Notes:
        Be mindful of 'self.name' even if you don't override it with a custom name.
        The contents of /proc/{pid}/cmdline could be anything, and since the logic only does a very simple substring
            check you might end up `kill`ing a legitimate process that has a similar file name or argument.
        For example, if you set name to 'bob' and there was another process that started later and happened to re-
            use the PID for a previous instance of `bob` and was named 'john.sh --path=/var/bob' then that process would
            get `kill`ed.
        The self.kill variable gives you the chance to be careful with process management without sacrificing lock
            file functionality.

        *You may think it is rather silly to worry about PID re-use, but I have to code on/for systems that stay online
            for years at a time, some have been up for over a decade, but whether or not it makes sense it is still a
            valid error condition and one that is easy to check for.
    """

    def __init__(self, age_limit=3600, file='/var/run/{name}.pid', kill=False, name=None):
        """
        Default settings:
            age_limit: 36000 seconds (1 hour)
            name: Actual name of this process else 'Python'
            file: /var/run/{{name}}.pid
            kill: False
        """
        self.birthday = (
            float(time.time()),
            str(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))
            )
        self.hostname = str(node())
        self.kill = bool(kill)
        self.age_limit = int(age_limit)
        #
        # Name of file this is running as
        if name is None:
            self.name = str(os.path.basename(sys.argv[0]))
        else:
            self.name = str(name)
        arg0 = self.name.replace('.py', '')
        if len(arg0) < 3 or len(arg0) > 255:
            #
            # If arg zero is invalid, name me Python
            arg0 = 'Python'
        #
        self.file = file.format(name=arg0)
        self.log = self.Log(tag='{0}[{1}]'.format(arg0, os.getpid()))
        self.log('init(age_limit={0}, file={1}, kill={2}, name={3}):'.format(
            self.age_limit,
            self.file,
            self.kill,
            self.name
        ))

    class Log(object):
        """
        Track and report steps taken in this app.
        'tag' is "name[pid]", similar to the -t argument used in `/bin/logger`
        """
        def __init__(self, tag):
            """ Create new log """
            self.trace = ''
            self.tag = tag

        def __call__(self, this):
            """ Add 'this' to my log """
            self.trace = '{OG}{Now} {Host} {Proc} {Event}\n'.format(
                OG=self.trace,
                Now=time.strftime('%c', time.localtime()),
                Host=node(),
                Proc=self.tag,
                Event=this,
            )

        def __str__(self):
            """ Return my log as multi-line string """
            return self.trace

    def create(self):
        """
        check() for existing lock file, if that returns True create a
        new lock file and return True.
        """
        self.log('create()')
        if not self.check():
            return False
        with open(self.file, 'w') as handle:
            handle.write('{0}\n'.format(os.getpid()))
            self.log('create() return True')
        return True

    def delete(self):
        """
        Remove the lock file.
        This can also be accessed as my_lock_file.remove()
        """
        self.log('delete({0})'.format(self.file))
        os.remove(self.file)
        return True

    def remove(self):
        """
        For ease of use.
        """
        self.delete()

    def check(self):
        """
        Check for lock file, running process, and validate name of running process.

        Return True if is OK to start new process.
        Return False if old process still running, have to wait.
        """
        self.log('check()')
        if not os.path.exists(self.file):
            self.log('No lock file found, assume not running')
            return True
        #
        self.log('Lock file {0} found'.format(self.file))
        #
        try:
            self.log('Get old PID from {0}'.format(self.file))
            with open(self.file, 'r') as handle:
                contents = handle.read().rstrip()
                pid = int(contents)
        except Exception as error:
            self.log(type(error))
            self.log(error)
            return False
        #
        self.log('PID is {0}'.format(pid))
        #
        if os.path.exists('/proc/{0}'.format(pid)):
            self.log('PID {0} is running'.format(pid))
        else:
            self.log('PID {0} not found in process table'.format(pid))
            return True
        #
        cmdline = '/proc/{0}/cmdline'.format(pid)
        try:
            self.log('Check name, args in {0}'.format(cmdline))
            with open(cmdline, 'r') as handle:
                current_process = handle.read()
        except Exception as error:
            self.log(type(error))
            self.log(error)
            return False
        #
        if self.name not in current_process:
            self.log('"{0}" not found in "{1}"'.format(
                self.name,
                current_process,
                ))
            return True
        #
        self.log('"{0}" was found in "{1}"'.format(
            self.name,
            current_process,
            ))
        self.log(current_process)
        self.log('Check the age of the lock file')
        difference = int(time.time()) - int(os.path.getmtime(self.file))
        if difference >= self.age_limit:
            self.log('Lock file too old, diff={0}'.format(difference))
            return self.murder(pid)
        else:
            #
            # Lock file was created recently, PID
            # still running and the process looks
            # like this application, refuse new lock
            self.log('Lock file is recent, time difference={0}'.format(difference))
            return False

    def murder(self, pid=None):
        """
        Try to kill pid found in the lock file
        """
        self.log('murder({0})'.format(pid))
        if not pid:
            self.log('pid is None or False')
            return False
        if not isinstance(pid, int):
            self.log('pid is not an integer')
            return False
        if self.kill is not True:
            self.log('Not allowed to kill')
            return True
        try:
            #
            # send `kill -9 ${PID}`
            os.kill(pid, 9)
            return True
        except Exception as error:
            # Usually pid not running or unable to terminate process due to OS permissions.
            self.log(type(error))
            self.log(error)
        return False
