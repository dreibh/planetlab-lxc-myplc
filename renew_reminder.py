#!/usr/bin/python
#
# Notify users of slices that are about to expire
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2005 The Trustees of Princeton University
#
# $Id: renew_reminder.pl,v 1.1 2005/06/28 16:49:12 mlhuang Exp $
#

import sys
import time
from optparse import OptionParser

# Load shell with default configuration
sys.path.append('/usr/share/plc_api')
from PLC.Shell import Shell
plc = Shell(globals())

PLC_WWW_HOST = plc.config.PLC_WWW_HOST
PLC_NAME = plc.config.PLC_NAME

# Debug
verbose = False;

# E-mail parameteres
slice_url = """https://%(PLC_WWW_HOST)s/db/slices/index.php?id=""" % locals()

parser = OptionParser()
parser.add_option("-s", "--slice", action = "append", dest = "slices", default = None,
		  help = "Slice(s) to check (default: all)")
parser.add_option("-x", "--expires", type = "int", default = 5,
		  help = "Warn if slice expires this many days from now (default: %default)")
parser.add_option("-n", "--dryrun", action = "store_true", default = False,
		  help = "Dry run, do not actually e-mail users (default: %default)")
parser.add_option("-f", "--force", action = "store_true", default = False,
		  help = "Force, send e-mail even if slice is not close to expiring (default: %default)")
parser.add_option("-v", "--verbose", action = "store_true", default = False,
		  help = "Be verbose (default: %default)")
(options, args) = parser.parse_args()

now = int(time.time())
expires = now + (options.expires * 24 * 60 * 60)

if options.verbose:
    print "Checking for slices that expire before " + time.ctime(expires)

slice_filter = {'peer_id': None}
if options.slices:
    slice_filter['name'] = options.slices

for slice in GetSlices(slice_filter, ['slice_id', 'name', 'expires', 'description', 'url', 'person_ids']):
    # See if slice expires before the specified warning date
    if not options.force and slice['expires'] > expires:
        continue

    # Calculate number of whole days left
    delta = slice['expires'] - now
    days = delta / 24 / 60 / 60
    if days == 0:
	days = "less than a day"
    else:
        if days > 1:
            suffix = "s"
        else:
            suffix = ""
	days = "%d day%s" % (days, suffix)

    name = slice['name']
    slice_id = slice['slice_id']

    message = """
The %(PLC_NAME)s slice %(name)s will expire in %(days)s.
"""

    # Explain that slices must have descriptions and URLs
    if not slice['description'] or not slice['description'].strip() or \
       not slice['url'] or not slice['url'].strip():
        message += """
Before you may renew this slice, you must provide a short description
of the slice and a link to a project website.
"""

    # Provide links to renew or delete the slice
    message += """
To update, renew, or delete this slice, visit the URL:

	%(slice_url)s%(slice_id)d
"""

    # Send it
    if slice['person_ids']:
        if options.dryrun:
            print message % locals()
        else:
            NotifyPersons(slice['person_ids'],
                          "%(PLC_NAME)s slice %(name)s expires in %(days)s" % locals(),
                          message % locals())
    elif options.verbose:
        print slice['name'], "has no users, skipping"
