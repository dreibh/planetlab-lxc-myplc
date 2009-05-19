#!/usr/bin/env plcsh

# searches and displays any local orphan account (not attached to a site)
# remote accounts with identical emails are displayed as well

import time

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

def get_related(email):
    return GetPersons ({'email':email,'~peer_id':None})

def header (message):
    print '--------------------'
    print GetPeerName(),
    print time.asctime(time.gmtime())
    print 'Listing orphan accounts and any similar remote'
    print '--------------------'

def main_orphans ():
    orphans = get_orphans()
    header ('Listing  %d  local accounts with no site - and similar remote accounts'%len(orphans))
    index=1
    for p in orphans:
        list_person ("%3d"%index,p)
        for related in get_related(p['email']):
            list_person("dup",related)
        index+=1
    
def main_duplicates():

    header ('Listing all duplicate accounts')
    locals = GetPersons({'peer_id':None,'-SORT':'email'})
    locals.sort(sort_email)
    for local in locals:
        remotes=GetPersons({'email':local['email'],'~peer_id':None})
        if remotes:
            list_person('---',local)
            for remote in remotes:
                list_person('dup',remote)

def main():
    main_orphans()
    main_duplicates()

if __name__ == '__main__':
    main()
