#!/usr/bin/env python3
#
# Notify users of slices that are about to expire
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2005 The Trustees of Princeton University
#
# pylint: disable=c0326

import sys
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# Load shell with default configuration
sys.path.append('/usr/share/plc_api')
from PLC.Shell import Shell

def main():

    plc = Shell(globals())

    PLC_WWW_HOST = plc.config.PLC_WWW_HOST
    PLC_NAME = plc.config.PLC_NAME

    # E-mail parameteres
    slice_url = f"https://{PLC_WWW_HOST}/db/slices/index.php?id="


    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--slice", action="append", dest="slices", default=None,
                        help="Slice(s) to check (default: all)")
    parser.add_argument("-x", "--expires", type=int, default=5,
                        help="Warn if slice expires this many days from now")
    parser.add_argument("-n", "--dry-run", action="store_true", default=False,
                        help="Dry run, do not actually e-mail users")
    parser.add_argument("-f", "--force", action="store_true", default=False,
                        help="Force, send e-mail even if slice is not close to expiring")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Be verbose")
    args = parser.parse_args()

    now = int(time.time())
    expires = now + (args.expires * 24 * 60 * 60)

    if args.verbose:
        print("Checking for slices that expire before " + time.ctime(expires))

    slice_filter = {'peer_id': None}
    if args.slices:
        slice_filter['name'] = args.slices

    # issue one call to GetPersons to gather the sfa_created tag on all persons
    persons = GetPersons({'peer_id': None}, ['person_id', 'email', 'sfa_created'])
    persons_by_id = { p['person_id'] : p for p in persons }
    if args.verbose:
        print("retrieved {} persons".format(len(persons)))

    slices = GetSlices(
        slice_filter,
        ['slice_id', 'name', 'expires', 'description', 'url', 'person_ids'])
    if args.verbose:
        print("scanning {} slices".format(len(slices)))

    for slice in slices:
        # See if slice expires before the specified warning date
        if not args.force and slice['expires'] > expires:
            continue

        # Calculate number of whole days left
        delta = slice['expires'] - now
        days = delta // (24 * 60 * 60)
        if days == 0:
            days = "less than a day"
        else:
            if days > 1:
                suffix = "s"
            else:
                suffix = ""
            days = f"{days} day{suffix}"

        slice_name = slice['name']
        slice_id = slice['slice_id']

        message = f"""
    The {PLC_NAME} slice {slice_name} will expire in {days}.
    """

        # Explain that slices must have descriptions and URLs
        if not slice['description'] or not slice['description'].strip() or \
           not slice['url'] or not slice['url'].strip():
            message += f"""
    Before you may renew this slice, you must provide a short description
    of the slice and a link to a project website.
    """

        # Provide links to renew or delete the slice
        message += f"""
    To update, renew, or delete this slice, visit the URL:

            {slice_url}{slice_id}
    """

        # compute set of persons but keep federated users (the ones with sfa_created) out
        slice_persons    = [persons_by_id[id] for id in slice['person_ids']]
        recipient_emails = [person['email'] for person in slice_persons
                            if not person['sfa_created']]
        nb_in_slice      = len(slice_persons)
        nb_not_sfa       = len(recipient_emails)

        if not recipient_emails:
            if args.verbose:
                print(f"""{slice_name} has no recipient
    ({nb_in_slice} in slice, {nb_not_sfa} not sfa_created)""")
            continue

        log_details = [time.ctime(now), slice_name, time.ctime(slice['expires'])]
        details = "\t".join(log_details)
        recipients = ",".join(recipient_emails)
        log_data = f"{details}\t{recipients}"

        extras = GetMessages({'message_id': "renew_reminder_addition"})
        if extras:
            message += extras[0]['template']

        if args.dry_run:
            print(f"-------------------- Found slice to renew {slice_name}")
            print(message)
            print(f"---- log_data\n{log_data}")
        else:
            NotifyPersons(slice['person_ids'],
                          f"{PLC_NAME}: slice {slice_name} expires in {days}",
                          message)
            print(log_data)

if __name__ == '__main__':
    main()
