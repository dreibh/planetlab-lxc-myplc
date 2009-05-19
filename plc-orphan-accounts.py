#!/usr/bin/env plcsh

# searches and displays any local orphan account (not attached to a site)
# remote accounts with identical emails are displayed as well

import time

def get_orphans ():
    return [p for p in GetPersons({'peer_id':None,'-SORT':'date_created'}) if not p['site_ids'] ]

def list_person (margin,p):
    print margin,'%6d'%p['person_id'], time.asctime(time.gmtime(p['date_created'])),
    if not p['peer_id']: print 'LOCAL',
    else: print 'pr=',p['peer_id'],
    print p['email']

def get_related(email):
    return GetPersons ({'email':email,'~peer_id':None})

def main ():
    
    orphans = get_orphans()
    print GetPeerName(),' ---  %d  --- '%len(orphans),'orphan accounts'
    print '---'
    index=1
    for p in orphans:
        list_person ("%3d"%index,p)
        for related in get_related(p['email']):
            list_person("dup",related)
        index+=1
    
if __name__ == '__main__':
    main()
