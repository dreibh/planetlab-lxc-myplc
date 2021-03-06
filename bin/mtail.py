#!/usr/bin/env python3

'''
Does tail -f on log files in a given directory.
The display is in chronological order of the logged lines,
given that the first column of log files is timestamp.
It can be altered to fit other formats too
'''

import os, sys, time
import select
import sys, tty, termios

from optparse import OptionParser

class mtail:

    default_time_format = "%H:%M:%S"

    def __init__ (self, args ):

        # internal structure for tracking changes
        self.files = {}
        # parse command-line args : will set options and args
        self.parse_args(args)
        # initialize
        self.scan_files()

    def parse_args (self, args):
        usage = """usage: %prog [options] file-or-dir ...
example:
# %prog -e '*access*' /var/log"""
        parser=OptionParser(usage=usage)
        # tail_period
        parser.add_option("-p","--period", type="int", dest="tail_period", default=1,
                          help="Files check period in seconds")
        # rescan_period
        parser.add_option("-d","--dir-period", type="int", dest="rescan_period", default=5,
                          help="Directories rescan period in seconds")
        # time format
        parser.add_option("-f","--format", dest="time_format", default=mtail.default_time_format,
                          help="Time format, defaults to " + mtail.default_time_format)
        # show time
        parser.add_option("-r","--raw", action="store_true", dest="show_time", default=True,
                          help="Suppresses time display")

        # note for exclusion patterns
        parser.add_option("-e","--exclude", action="append", dest="excludes", default=[],
                          help="Exclusion pattern  -- can be specified multiple times applies on files not explicitly mentioned on the command-line")

        parser.add_option("-u","--usual",action="store_true",dest="plc_mode",default=False,
                          help="Shortcut for watching /var/log with default settings")
        parser.add_option("-s","--sfa",action="store_true",dest="sfa_mode",default=False,
                          help="Shortcut for monitoring server-side SFA log files")

        # verbosity
        parser.add_option("-v","--verbose", action="store_true", dest="verbose", default=False,
                          help="Run in verbose mode")

        (self.options, self.args) = parser.parse_args(args)
        self.option_parser = parser

        ### plc shortcuts
        if self.options.plc_mode:
            # monitor all files in /var/log with some exceptions
            self.options.excludes.append('*access_log')
            self.options.excludes.append('*request_log')
            self.options.excludes.append('*.swp')
            self.args.append('/var/log')
            # watch the postgresql logs as well
            self.args.append('/var/lib/pgsql/data/pg_log')

        if self.options.sfa_mode:
            self.args.append("/var/log/sfa.log")
            self.args.append("/var/log/sfa_import.log")
            self.args.append("/var/log/httpd/sfa_access_log")

        if self.options.verbose:
            print('Options:',self.options)
            print('Arguments:',self.args)

    def file_size (self,filename):
        try:
            return os.stat(filename)[6]
        except:
            print("WARNING: file %s has vanished"%filename)
            return 0

    def number_files (self):
        return len(self.files)

    # scans given arguments, and updates files accordingly
    # can be run several times
    def scan_files (self) :

        if self.options.verbose:
            print('entering scan_files, files=',self.files)

        # mark entries in files as pre-existing
        for key in self.files:
            self.files[key]['old-file']=True

        # refreshes the proper set of filenames
        filenames = []
        for arg in self.args:
            if self.options.verbose:
                print('scan_files -- Considering arg',arg)
            if os.path.isfile (arg):
                filenames += [ arg ]
            elif os.path.isdir (arg) :
                filenames += self.walk (arg)
            else:
                print("mtail : no such file or directory %s -- ignored"%arg)

        # updates files
        for filename in filenames :
            # known file
            if filename in self.files:
                size = self.file_size(filename)
                offset = self.files[filename]['size']
                if size > offset:
                    self.show_file_end(filename,offset,size)
                    self.files[filename]['size']=size
                elif size < offset:
                    self.show_file_when_size_decreased(filename,offset,size)
                try:
                    del self.files[filename]['old-file']
                except:
                    pass
            else:
                # enter file with current size
                # if we didn't set format yet, it's because we are initializing
                try:
                    self.format
                    self.show_now()
                    print(self.format%filename,"new file")
                    self.show_file_end(filename,0,self.file_size(filename))
                except:
                    pass
                self.files[filename]={'size':self.file_size(filename)}

        # cleanup
        # avoid side-effects on the current loop basis
        read_filenames = list(self.files.keys())
        for filename in read_filenames:
            if 'old-file' in self.files[filename]:
                self.show_now()
                print(self.format%filename,"file has gone")
                del self.files[filename]

        # compute margin and format
        if not filenames:
            print(sys.argv[0],": WARNING : no file in scope")
            self.format="%s"
        else:
            if len(filenames)==1:
                self.margin=len(filenames[0])
            else:
                # this stupidly fails when there's only 1 file
                self.margin=max(*[len(f) for f in filenames])
            self.format="%%%ds"%self.margin
            if self.options.verbose:
                print('Current set of files:',filenames)

    def tail_files (self):

        if self.options.verbose:
            print('tail_files')
        for filename in self.files:
            size = self.file_size(filename)
            offset = self.files[filename]['size']
            if size != offset:
                self.show_file_end(filename,offset,size)
                self.files[filename]['size']=size

    def show_now (self):
        if self.options.show_time:
            label=time.strftime(self.options.time_format,time.localtime())
            print(label, end=' ')

    def show_file_end (self, filename, offset, size):
        try:
            file = open(filename,"r")
        # file has vanished
        except:
            return
        file.seek(offset)
        line=file.read(size-offset)
        self.show_now()
        print(self.format%filename,'----------------------------------------')
        print(line)
        file.close()

    def show_file_when_size_decreased (self, filename, offset, size):
        print(self.format%filename,'---------- file size decreased ---------', end=' ')
        if self.options.verbose:
            print('size during last check',offset,'current size',size)
        else:
            print('')

    # get all files under a directory
    def walk ( self, root ):
        import fnmatch, os, string

        # initialize
        result = []

        # must have at least root folder
        try:
            names = os.listdir(root)
        except os.error:
            return result

        # check each file
        for name in names:
            fullname = os.path.normpath(os.path.join(root, name))

            # a file : check for excluded, otherwise append
            if os.path.isfile(fullname):
                try:
                    for exclude in self.options.excludes:
                        if fnmatch.fnmatch(name, exclude):
                            raise Exception('excluded')
                    result.append(fullname)
                except:
                    pass
            # a dir : let's recurse - avoid symlinks for anti-loop
            elif os.path.isdir(fullname) and not os.path.islink(fullname):
                result = result + self.walk( fullname )

        return result

    def run (self):

        if len(self.args) == 0:
            self.option_parser.print_help()
            sys.exit(1)
        counter = 0

        fdin = sys.stdin.fileno()
        while True:
            ## hit the period ?
            # dont do this twice at startup
            if (counter !=0 and counter % self.options.rescan_period == 0):
                self.scan_files()

            if (counter % self.options.tail_period == 0):
                self.tail_files()

            time.sleep(1)
            counter += 1
            # react on some keys - rough but convenient
            if os.isatty(fdin):
                # read stdin
                typed=[]
                while select.select([sys.stdin,],[],[],0.0)[0]:
                    typed.append(sys.stdin.read(1))
#                print 'found chars',typed
                for char in typed:
                    if char.lower() in ['l']: os.system("clear")
                    elif char.lower() in ['m']:
                        for i in range(3) : print(60 * '=')
                    elif char.lower() in ['q']: sys.exit(0)
                    elif char.lower() in ['h']:
                        print("""l: refresh page
m: mark
q: quit
h: help""")

###
if __name__ == '__main__':
    mtail (sys.argv[1:]).run()
