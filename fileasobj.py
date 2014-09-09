#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
fileasobj.py - Manage a local file as an object. Store contents in a 
                unique list and ignore commented lines.
                
                Written to handle files that contain only text data, 
                good for when you cannot or will not use a proper SQL
                database. 
                
                Not useful for config files.
                

nullpass, 2012

Examples:


    # Reading a file, first example
    my_file = FileAsObj()
    if my_file.read('./input.txt'):
        print('File was loaded')
    else:
        print('File was NOT loaded, here are the errors')
        print(my_file.Trace)

    # Reading a file, second example
    file_clients = FileAsObj(os.path.join('etc','clients.info'), verbose=True)
    if file_clients.Errors:
        print(file_clients.Trace)
        sys.exit(10)


    # If there is a line in file_foo that contains substring 'delete_me'
    # then remove that line
    file_foo.rm(file_foo.grep('delete_me'))


Methods:
    .grep    find substring in file
    .egrep   regex-find substring in file
    .add     Add given line to end of file
    .rm      Remove a line from file, give entire matching line.
    .check   Return line if line is in file, else return False
    .read    Read file into self.contents as list
    .write   Save list to file overriding file on disk
    .replace Replace a whole line (old, new)
    
Attributes you usually care about:
    self.Trace  A string log of all methods run on object 
                    including any errors

    self.Errors A list log of any errors captured

    Verbose     BOOLEAN, if true file is .read() verbatim, comments and
                    short lines are NOT ignored and duplicate lines
                    are preserved.
                    Please remember that .rm() and .replace() will work
                    on duplicate lines. 
                    

An ever-so-slightly-non-apocryphal version history:
    2014.09.09 - V3, added .replace(), removed .dump() and .inventory()
    2014.08.14 - Finally added __str__
    2014.08.11 - Tab fixes and print changes to comply with py3.
    2014.06.20 - V2, added [e]grep, dump and verbose; some code correction
    2012.08.15 - Full conversion to portability, added .read()
    2012.07.20 - Initial release

"""
__version__ = '3.0.0'

import sys
import os
from platform import node
import time
import re


class FileAsObj:
    """
    Manage a file as an object-
            -For when you just can't be bothered to use a real database.
    
   
    Each line of a file is added to the list 'self.contents'. 
    By default lines that start with a # are ignored. 
    By default data in self.contents is unique.
    Lines are sorted by whatever order they appear in the file.
    Elements can be added or removed with .add and .rm. 
    The object's contents can be written back to the file, overwritting
    the file, with .write. 
    
    Error handling: I will not sys.exit or throw an exception. All errors
        are logged to self.Trace and self.Errors. It is the duty of the 
        calling code to check for self.Errors and act however is needed.
        
        self.Trace is a log of everything the instance of this class
        did. If there is an exception it is included.
        
        self.Errors is a list of exceptions.
    
    """
    
    def __init__(self, filename=None, verbose=False):
        """
        
        You may specify the file to read() during instatiation, but be
        sure to check for self.Errors. 
        
        verbose - BE CAREFUL! if you enable verbose all of the lines in 
            your file will be added to self.contents. This includes 
            comments and duplicate lines. If you rely on this classes'
            .grep() or .egrep() methods be sure you understand that 
            comments can be returned as a valid result!
            My greps will return the first match found, in the real-
            world that is usually a commented entry. 
        
        """
        self.Birthday = (
            float(time.time()),
            str(time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime()))
        )
        #
        # Name of file this is running as
        self.thisExec = str(os.path.basename(sys.argv[0]))
        if len(self.thisExec) < 3 or len(self.thisExec) > 255:
            #
            # If there's no name in argv[0], like if you call this from 
            # the Python shell, call this python_$$
            # Also catches names too short or long.
            self.thisExec = 'python_'+str(os.getpid())
        #
        # Hostname
        self.thisHost = node()
        #
        # Current executable and PID, like myapp[12345]
        self.thisProc = self.thisExec.rstrip('.py')+'['+str(os.getpid())+']'
        #
        # List of any exceptions caught
        self.Errors = []
        #
        # String containing information about steps taken. For debugging
        self.Trace = ''
        #
        # If enabled, I will not unique contents or ignore comments.
        self.verbose = verbose
        #
        # The list where contents of the file are stored
        self.contents = []
        #
        # If you gave me a file to read when instatiated, then do so.
        self.filename = filename
        if self.filename:
            self.read(self.filename)
        #
        # Declare current state is original data from thisFile.
        self.virgin = True

    def __str__(self):
        """
        There's been much debate as to whether this should
        return self.filename or self.contents as a string.
        My first use case needed it as a string so that's
        what I'm publishing.
        """
        return '\n'.join(self.contents)
        
    def __log(self,thisEvent):
        """
        Private method to update self.Trace with str(thisEvent)
        """
        NOW = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())
        #self.Trace += '%s %s %s %s\n' % (NOW, self.thisHost, self.thisProc, thisEvent)
        self.Trace = '{OG}{Now} {Host} {Proc} {Event}\n'.format(
            OG=self.Trace,
            Now=time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime()),
            Host=self.thisHost,
            Proc=self.thisProc,
            Event=thisEvent,
        )
        return
    
    def read(self,thisFile):
        """
        
        Open thisFile and write its contents to self.contents.
        Will not add duplicate lines or lines that start with #
        
        WILL add a line if it starts with a space or tab but has a #
        later in the line.
        
        FileAsObj.read('./inputfile.txt')
        """
        self.filename = str.strip(thisFile)
        try:
            self.__log('Read-only opening %s ' % self.filename)
            with open(self.filename, 'r') as fileHandle:
                for line in fileHandle:
                    line = line.strip("\n")
                    #
                    # blank lines that were just \n become None, 
                    # so make sure this pass of line exists
                    if line:
                        if self.verbose:
                            #
                            # Some crazy person enabled verbose, just 
                            # add whatever is in the file to 
                            # self.contents.
                            # May whatever god you believe in 
                            #   have mercy on your code.
                            self.contents.append(line)
                        elif line[0] is not "#":
                            # Line is not a comment
                            #
                            #
                            # unique the contents of the thisFile when
                            # read()ing.
                            # Ignore lines that have fewer than 2 
                            # characters
                            if len(line) > 1 and line not in self.contents:
                                self.contents.append(line)
            self.__log('Read %s lines' % len(self.contents))
            return True
        except Exception as e:
            self.__log('ERROR during read(self,thisFile) : %s' % e)
            self.Errors.append(e)
            return False
    
    def check(self,needle):
        """
        check existing contents of file for a string
        
        This searches each line as a whole, if you want to see if 
        a substring is in a line, use .grep() or .egrep() methods.
        
        If found, return the needle; makes it easier for some code
        to delete more efficiently. 
        """
        if needle in self.contents:
            return needle
        return False
        
    def add(self,this):
        """
        add 'this' to end of list unless it already exists.
        
        RFC: should we add anyway if verbose == True?
        """
        self.__log('Call to add "%s" to %s' % (this, self.filename) )
        if this not in self.contents:
            self.contents.append(this)
            self.virgin = False
            return True
        return False
        
    def rm(self, this):
        """
        Remove all occurances of 'this' from contents
            where 'this' is an entire line.
        """
        self.__log('Call to remove "%s" from %s' % (this, self.filename) )
        if this in self.contents:
            while this in self.contents:
                self.__log('Removed string from line {} of {}'.format(self.contents.index(this), self.filename))
                self.contents.remove(this)
                self.virgin = False
        self.__log('"{}" not found in {}'.format(this, self.filename))
        return False
        
    def write(self):
        """
        write self.contents to self.filename
        self.filename was defined during .read()
        
        There is no self.virgin check because we need to let the caller
        decide whether or not to write. This is useful if you want to 
        force an overwrite of a file that might have been changed on 
        disk even if self.contents did not change.
        
        You can do something like:
        if not stats.virgin:
            #
            #something changed, re-write the file.
            stats.write()

        """
        try:
            self.__log('Writing '+str(self.filename))
            with open(self.filename, 'w') as fileHandle:
                for thisLine in self.contents:
                    fileHandle.write(thisLine+'\n')
            return True
        except Exception as e:
            self.__log('ERROR in write(self) : %s' % e)
            self.Errors.append(e)
            return False
            
    def grep(self, needle):
        """
        Search for a string like `grep string file`
        No regex support here.
        
        If found, return the line. This makes it easier to .rm(line)
        """
        for line in self.contents:
            if needle in line:
                return line
        return False

    def egrep(self, pattern):
        """
        REGEX search for pattern in file
        
        If found, return the line. This makes it easier to .rm(line)
        """
        for line in self.contents:
            if re.search(pattern, line):
                return line
        return False

    def replace(self, old, new):
        """
        Replace all lines of file that match 'old' with 'new'
        
        The fact that this method (and .rm) work on duplicate matches
        only matters if you _init_ the file with verbose=True because
        .read() strips out duplicates by default.
        """
        self.__log('Call to replace "{}" with "{}" in {}'.format(old, new, self.filename))
        if old not in self.contents:
            self.__log('"{}" not found in {}'.format(old, self.filename))
            return False
        #
        while old in self.contents:
            I = self.contents.index(old)
            self.contents.remove(this)
            self.contents.insert(I, new)
            self.virgin = False
        return True
