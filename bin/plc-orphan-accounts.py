#!/usr/bin/env plcsh
#
# searches and displays any local orphan account (not attached to a site)
# remote accounts with identical emails are displayed as well

import sys
import time
import readline
from optparse import OptionParser

logdir="/var/log/accounts"

def run_in_log (options):
    monthstring=time.strftime("%Y-%m")
    if not os.path.isdir(logdir):
        os.mkdir(logdir)
    logname="%s/orphans-%s.log"%(logdir,monthstring)
    sys.stdout=open(logname,'a')
    sys.stderr=sys.stdout
    run(options)
    sys.stderr.close()
    sys.stdout.close()

# sort filters look broken
def sort_email (p1,p2):
    if p1['email'] == p2['email']: return 0
    if p1['email'] < p2['email'] : return -1
    return 1

def get_orphans ():
    orphans = [p for p in GetPersons({'peer_id':None,'-SORT':'email'}) if not p['site_ids'] ]
    orphans.sort(sort_email)
    return orphans

def list_person (margin,p):
    print margin,'%6d'%p['person_id'], time.asctime(time.gmtime(p['date_created'])),
    if not p['peer_id']: print 'LOCAL',
    else: print 'pr=',p['peer_id'],
    if p['enabled']: print 'ENB',
    else: print 'DIS',
    print p['email']

date_keys=['date_created','last_updated']
def details_person (p):
    keys=p.keys()
    keys.sort()
    for key in keys:
        print key,'->',
        value=p[key]
        if key in date_keys:    print time.asctime(time.gmtime(value))
        else:                   print value

def get_related(email):
    return GetPersons ({'email':email,'~peer_id':None})

def header (message):
    print '--------------------'
    print GetPeerName(),
    print time.asctime(time.gmtime())
    print 'Listing orphan accounts and any similar remote'
    print '--------------------'

def delete_local (person,default_bool,options):
    
    # just in case
    if person['peer_id'] != None:
        print 'ERROR: cannot delete non-local person',person['email']
        return

    prompt = 'want to delete '+person['email']
    if default_bool:    prompt += ' v(erbose)/[y]/n ? '
    else:               prompt += ' v(erbose)y/[n] ? '

    done=False

    while not done:
        done=True
        try:
            answer = raw_input(prompt).strip()
        except EOFError :
            print 'bailing out'
            sys.exit(1)

        if answer=='':
            do_delete=default_bool
        elif answer.lower()[0]=='y':
            do_delete=True
        elif answer.lower()[0]=='n':
            do_delete=False
        elif answer.lower()[0]=='v':
            details_person(person)
            done=False
        else:
            done=False
    id=person['person_id']
    email=person['email']
    if options.dry_run:
        if do_delete:                   print 'Would delete',id,'->',email
        else:                           print 'Would preserve',id,'->',email
    elif do_delete:
        print 'Deleting',id,'->',email,
        if DeletePerson(id) == 1:       print 'OK',id,'deleted'
        else:                           print 'Deletion failed'

def main_orphans (options):
    orphans = get_orphans()
    header ('Listing  %d  local accounts with no site - and similar remote accounts'%len(orphans))
    index=0
    for local in orphans:
        index+=1
        list_person ("%3d"%index,local)
        for related in get_related(local['email']):
            list_person("dup",related)
        if options.delete:
            delete_default = not local['enabled']
            delete_local(local,delete_default,options)
    
def main_duplicates(options):

    header ('Listing all duplicate accounts')
    locals = GetPersons({'peer_id':None,'-SORT':'email'})
    locals.sort(sort_email)
    index=0
    for local in locals:
        remotes=GetPersons({'email':local['email'],'~peer_id':None})
        if remotes:
            index+=1
            list_person('%3d'%index,local)
            for remote in remotes:
                list_person('dup',remote)
            if options.delete:
                delete_default = not local['enabled']
                delete_local(local,delete_default,options)

def run (options):
    main_orphans(options)
    main_duplicates(options)

def main():

    usage="%prog [ -- options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-l","--log", dest="log", action="store_true",default=False,
                      help="write current status in /var/log/accounts")
    parser.add_option("-d","--delete", dest="delete", action="store_true",default=False,
                      help="interactively delete extraneous accounts")
    parser.add_option("-n","--dry-run", dest="dry_run", action="store_true",default=False,
                      help="go through the delete prompting but does not delete")

    (options,args) = parser.parse_args()
    if len(args)!=0:
        parser.error("Unexpected arguments",args)

    if options.dry_run: options.delete=True
    
    if options.log:
        options.delete=False
        run_in_log(options)
    else:
        run(options)
    
if __name__ == '__main__':
    main()
