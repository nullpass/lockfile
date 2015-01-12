#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
locker.py - Provide easy lock file management as a class.
    "Dissatisfied with the shape of a perfect circle
        I've reinvented the wheel, again."


by: nullpass, 2012; based loosely on gekitsuu's Mutex()

Examples:
    # Try to create a lock file using default settings (see __init__)
    #
    from locker import Locker
    mylock = Locker()
    if mylock.create():
        ...
        ...code that requires a lock file here...
        ...
        mylock.delete()


    # Try to create a lock file using a custom pid file.
    # Don't allow a previous instance to be killed.
    # Set maximum age of the lock file to be 999999999 seconds.
    #
    from locker import Locker
    mylock = Locker()
    mylock.lockfile = '/var/run/custom.pid'
    mylock.maxage = 999999999
    mylock.Killable = False
    if mylock.create():
        print 'I made a lock file'
        print 'Debugg output: \n'+str(mylock.Trace)
    else:
        print 'unable to create lock file'
        print 'Errors: \n'+str(mylock.Errors)


Notes:
    Be mindful of 'thisExec' even if you don't override it with a custom
    name.
    The contents of /proc/'oldpid'/cmdline could be anything, and since the
    logic only does a very simple substring check you might end up `kill`ing
    a legitimate process that has a similar file name or argument.
    For example, if you named your 'thisExec' bob and there was another
    process that started later and happened to re-use the PID for a previous
    instance of `bob` and was named 'john.sh --path=/var/bob' then that
    process would get `kill`ed.
    The self.killable variable gives you the chance to be careful with
    process management without sacrificing lock file functionality.

    *You may think it is rather silly to worry about PID re-use, but I have
    to code on/for systems that stay online for years at a time, some have
    been up for over a decade, but whether or not it makes sense it is still
    a valid error condition and one that is easy to check for.

Logic:
    If lock file does not exist: OK, create

    If lock file exists but proc not running: OK, delete, create
        [Previous instance failed to remove its lock file before exiting]

    If PID running and process matches str(thisExec) and the lock file is
        older than int(maxage): OK, kill, delete, create
        [A previous instance is stuck, kill it and allow a new instance to run]

    If PID running but the name of the process does not match this_exec: OK,
        delete old lock file and create new one
        [Previous instance failed to remove its lock file and some other
        process spawned later with the same PID]*

    If lock file exists, PID running and the process matches str(thisExec): FAIL
        [Previous instance still running, not old enough to kill]


TODO:
    1. os.kill in Locker.murder() needs more testing
    2. Add basic funtionality to main() to allow locking with default
        settings from the command line. Use sys.exit(0|1) to inform
        caller if locker was successful. --DONE, check main() for usage
"""

__version__ = '0.1.1b'
import time
import os
from platform import node
import sys
sys.dont_write_bytecode = True

class Locker(object):
    # pylint: disable=too-many-instance-attributes
    """
    Yu' sure gotta purddy lockfile.
    """
    def __init__(self):
        """
        Give birth, define default settings.
        """
        self.birthday = (
            float(time.time()),
            str(time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()))
            )
        #
        # True = Let Locker.murder() os.kill an old pid found where the name
        #        of the process matches this application.
        # If False, Locker.murder() will return True but not actually os.kill
        self.killable = True
        #
        # String containing information about steps taken. Used for debugging
        self.trace = ''
        """
        >>> print m.trace
        Tue Aug 14 15:29:53 EDT 2012 pyt[3253] check(self)
        Tue Aug 14 15:29:53 EDT 2012 pyt[3253] PID file /me/m.pid found
        Tue Aug 14 15:29:53 EDT 2012 pyt[3253] Get old PID from /me/m.pid
        Tue Aug 14 15:29:53 EDT 2012 pyt[3253] PID 3212 in /me/m.pid not running
        Tue Aug 14 15:29:53 EDT 2012 pyt[3253] delete(self)
        Tue Aug 14 15:30:02 EDT 2012 pyt[3253] create(self)
        """
        #
        # Max age (in seconds) a lock file can be before it is
        # considered invalid (too old to trust)
        #self.maxage = 1     # 1 second
        #self.maxage = 300   # 5 minutes
        #self.maxage = 3600  # 1 hour
        #self.maxage = 43200 # 12 hours
        self.maxage = 86400 # 24 hours
        #
        # Name of file this is running as
        self.this_exec = str(os.path.basename(sys.argv[0]))
        arg0 = self.this_exec.replace('.py', '')
        if len(arg0) < 3 or len(arg0) > 255:
            #
            # If arg zero is invalid, name me Python
            arg0 = 'Python'
        #
        # Current executable and PID, like myapp[12345]
        self.logname = '{0}[{1}]'.format(arg0, os.getpid())
        self.hostname = node()
        #
        # Full path to lock file, default to /var/run/$0.pid
        self.lockfile = '/var/run/{0}.pid'.format(arg0)
        #
        # If you need to double check lock status after calling Locker.create()
        self.locked = False
        self.log = self.Log(self.logname)


    class Log(object):
        # pylint: disable=too-few-public-methods
        """ Track and report steps taken in this app."""
        def __init__(self, logname):
            """ Create new log """
            self.trace = ''
            self.logname = logname

        def __call__(self, this):
            """ Add 'this' to my log """
            self.trace = '{OG}{Now} {Host} {Proc} {Event}\n'.format(
                OG=self.trace,
                Now=time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()),
                Host=node(),
                Proc=self.logname,
                Event=this,
            )

        def __str__(self):
            """ Return my log as multiline string """
            return self.trace


    def create(self):
        """
        check() for existing lock file, if that returns True create a
        new lock file and return True.
        """
        self.log('create(self)')
        if not self.check():
            return False
        try:
            with open(self.lockfile, 'w') as handle:
                handle.write('{0}\n'.format(os.getpid()))
                self.locked = True
                return True
        except (FileNotFoundError, PermissionError) as error:
            self.log(error)
        # all-else
        return False

    def delete(self):
        """
        Remove the lock file.
        This can also be accessed as mylock.remove()
        """
        self.log('delete(self)')
        try:
            os.remove(self.lockfile)
            return True
        except Exception as error:
            self.log(error)
        # all-else
        return False

    def remove(self):
        """
        For ease of use.
        """
        self.delete()

    def check(self):
        # pylint: disable=too-many-return-statements
        """
        Check for lock file, running proc, and name of running proc.

        Return True if is OK to start new process (not running or too old)
        Return False if running, have to wait.
        """
        self.log('check(self)')
        if not os.path.exists(self.lockfile):
            self.log('No lock file found, assume not running')
            return True
        #
        self.log('Lock file {0} found'.format(self.lockfile))
        #
        try:
            self.log('Get old PID from {0}'.format(self.lockfile))
            with open(self.lockfile, 'r') as handle:
                oldpid = handle.read().rstrip()
        except (FileNotFoundError, PermissionError) as error:
            self.log(error)
            return False
        #
        self.log('PID is {0}'.format(oldpid))
        #
        if os.path.exists(os.path.join('proc', oldpid)):
            self.log('PID {0} is running'.format(oldpid))
        else:
            self.log('PID {0} not found in process table'.format(oldpid))
            if self.delete():
                return True
            return False
        #
        cmdline = os.path.join('proc', oldpid, 'cmdline')
        try:
            self.log('Check name, args in /proc/{0}/cmdline'.format(oldpid))
            with open(cmdline, 'r') as handle:
                current_process = handle.read()
        except (FileNotFoundError, PermissionError) as error:
            self.log(error)
            return False
        #
        if self.this_exec not in current_process:
            self.log('"{0}" not found in {1}'.format(
                self.this_exec,
                cmdline,
                ))
            if self.delete():
                return True
            return False
        #
        self.log('"{0}" was found in {1}'.format(
            self.this_exec,
            cmdline,
            ))
        self.log(current_process)
        self.log('Check the age of the lock file')
        file_mtime = int(os.path.getmtime(self.lockfile))
        diff = int(time.time()) - file_mtime
        if diff > self.maxage:
            self.log('Lock file too old, diff={0}'.format(diff))
            if self.murder(oldpid):
                return True
            return False
        else:
            #
            # Lock file was created recently, PID
            # still running and the process looks
            # like this application, refuse new lock
            self.log('Lock file is recent, diff={0}'.format(diff))
            return False
        # all-else
        return False

    def murder(self, oldpid=None):
        """
        Try to kill pid found in the lock file
        """
        self.log('murder(self, {0})'.format(oldpid))
        if not oldpid:
            # __backcap__
            self.log('oldpid is None')
            return False
        if not isinstance(oldpid, int):
            # __backcap__
            self.log('oldpid not an integer')
            return False
        if not self.killable:
            self.log('Not allowed to kill')
            return True
        try:
            #
            # send `kill -9 ${PID}`
            os.kill(oldpid, 9)
            return True
        except Exception as error:
            # No pid or no permissions (usually)
            self.log(error)
        return False

def main():
    """
    If you want to use this for shell scripts or unix apps do this:

    me@pybox01:~$ python ./locker.py create ./foo.pid ; echo $?
    0
    me@pybox01:~$ python ./locker.py delete ./foo.pid ; echo $?
    0
    me@pybox01:~$

    in shell code
    python ./locker.py create ./foo.pid || exit $?

    """
    if not sys.argv[1:] and sys.stdin.isatty():
        sys.exit(1)
    mylock = Locker()
    if sys.argv[2:]:
        mylock.lockfile = sys.argv[2]
    #
    if 'create' in sys.argv[1]:
        if mylock.create():
            print(mylock.log)
            sys.exit(0)
        sys.exit(1)
    #
    if 'delete' in sys.argv[1]:
        if mylock.delete():
            print(mylock.log)
            sys.exit(0)
        sys.exit(1)
    #
    # all-else
    sys.exit(1)

if __name__ == '__main__':
    main()
