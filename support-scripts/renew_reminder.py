#!/usr/bin/python3
#
# Notify users of slices that are about to expire
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2005 The Trustees of Princeton University
#

import os
import sys
import time
from optparse import OptionParser

# Load shell with default configuration
sys.path.append('/usr/share/plc_api')
from PLC.Shell import Shell
plc = Shell(globals())

PLC_WWW_HOST = plc.config.PLC_WWW_HOST
PLC_NAME = plc.config.PLC_NAME

LOGFILE = '/var/log/renew_reminder'
class Logfile:
    def __init__(self, filename):
	self.filename = filename
    def write(self, data):
	try:
	    fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
	    os.write(fd, '{}'.format(data))
	    os.close(fd)
	except OSError:
	    sys.stderr.write(data)
	    sys.stderr.flush()

log = Logfile(LOGFILE)

# Debug
verbose = False;

# E-mail parameteres
slice_url = "https://{PLC_WWW_HOST}/db/slices/index.php?id=".format(**locals())

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
    print("Checking for slices that expire before " + time.ctime(expires))

slice_filter = {'peer_id': None}
if options.slices:
    slice_filter['name'] = options.slices

# issue one call to GetPersons to gather the sfa_created tag on all persons
persons = GetPersons ({'peer_id': None}, ['person_id', 'email', 'sfa_created'])
persons_by_id = { p['person_id'] : p for p in persons }
if options.verbose:
    print("retrieved {} persons".format(len(persons)))

slices = GetSlices(slice_filter, ['slice_id', 'name', 'expires', 'description', 'url', 'person_ids'])
if options.verbose:
    print("scanning {} slices".format(len(slices)))
    
for slice in slices:
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
	days = "{days} day{suffix}".format(**locals())

    slice_name = slice['name']
    slice_id = slice['slice_id']

    message_format = """
The {PLC_NAME} slice {slice_name} will expire in {days}.
"""

    # Explain that slices must have descriptions and URLs
    if not slice['description'] or not slice['description'].strip() or \
       not slice['url'] or not slice['url'].strip():
        message_format += """
Before you may renew this slice, you must provide a short description
of the slice and a link to a project website.
"""

    # Provide links to renew or delete the slice
    message_format += """
To update, renew, or delete this slice, visit the URL:

	{slice_url}{slice_id}
"""

    # compute set of persons but keep federated users (the ones with sfa_created) out 
    slice_persons    = [ persons_by_id[id] for id in slice['person_ids'] ]
    recipient_emails = [ person['email'] for person in slice_persons if not person['sfa_created'] ]
    recipient_ids    = [ person['email'] for person in slice_persons if not person['sfa_created'] ]
    nb_in_slice      = len(slice_persons)
    nb_not_sfa       = len(recipient_emails)

    if not recipient_emails:
        if options.verbose:
            print("""{slice_name} has no recipient 
({nb_in_slice} in slice, {nb_not_sfa} not sfa_created)""".format(**locals()))
        continue

    log_details = [time.ctime(now), slice_name, time.ctime(slice['expires'])]
    log_data = "{}\t{}".format("\t".join(log_details), ",".join(recipient_emails))

    if options.dryrun:
        print("-------------------- Found slice to renew {slice_name}".format(**locals()))
        print(message_format.format(**locals()))
        print("log >> {}".format(log_data))
    else:
        NotifyPersons(slice['person_ids'],
                      "{PLC_NAME} slice {slice_name} expires in {days}".format(**locals()),
                      message_format.format(**locals()))
        print(log_data, file=log)
	    
