#!/usr/bin/python
###
### utility script for cleaning empty directories
### useful to clean up /var/tmp/bootmedium
### 

"""
Usage: $0 dir [ .. dir]
scans all provided directories and prunes any empty directory under
the arg directories are always preserved 
"""

import os,sys

### cleans up a everything under a given root
def clean_root (path, cleanRoot = False):

    if not os.path.isdir(path):
        return
    
    # scan dir contents
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
	    # we do not remove files
	    return
        elif os.path.isdir(fullpath):
            clean_root(fullpath,True)

    if (cleanRoot):
	# rescan, and clean if empty
	files=os.listdir(path)
	if not files:
	    os.rmdir(path)

ERROR_STR= """Error removing %(path)s, %(error)s """

def main (dirs):

    for dir in dirs:
	try:
	    if dir.index("/") != 0:
		print "%s: args must be absolute paths"%(sys.argv[0])
		print "%s: %s ignored"%(sys.argv[0],dir)
	    else:
		clean_root(dir)
	except OSError, (errno, strerror):
	    print ERROR_STR % {'path' : path, 'error': strerror }

if __name__ == '__main__':
    main (sys.argv[1:])
