#!/usr/bin/plcsh

# running both RefreshPeer and Sfa requires to use some ugly hacks 
# over time we've faced quite a few situations where some 
# foreign entities somehow get wrongly attached to the local peer
#
# this script does damage assessment - no repairs yet - 
# in an attempt to monitor this sort of issues

from optparse import OptionParser

class SpotAliens:

    def __init__(self,verbose):
        print "==================== initializing ..",
        self.verbose=verbose
        self.all_sites=GetSites({},['peer_id','site_id','login_base','name'])
        self.all_nodes=GetNodes({},['peer_id','node_id','site_id','hostname'])
        self.all_persons=GetPersons({},['peer_id','person_id','site_ids','key_ids','email'])
        self.all_keys=GetKeys({},['peer_id','key_id'])
        self.all_slices=GetSlices({},['peer_id','slice_id','name','site_id'])

        self.site_hash=dict ( [ (site['site_id'],site) for site in self.all_sites ] )
        self.key_hash=dict ( [ (key['key_id'],key) for key in self.all_keys ] )
        self.slice_hash=dict ( [ (slice['slice_id'],slice) for slice in self.all_slices ] )
        print "done"

    def spot_nodes (self):
        "nodes are expected to be in the same peer as their owning site"
        counter=0
        for node in self.all_nodes:
            site=self.site_hash[node['site_id']]
            if node['peer_id'] != site['peer_id']: 
                counter+=1
                if self.verbose: print "NODE-SITE mismatch %r IN SITE %r"%(node,site)
        print '==================== Found %d inconsistent nodes'%counter

    def spot_slices (self):
        "slices are expected to be in the same peer as their owning site"
        counter=0
        for slice in self.all_slices:
            site=self.site_hash[slice['site_id']]
            if slice['peer_id'] != site['peer_id']: 
                counter+=1
                if self.verbose: print "SLICE-SITE mismatch %r IN SITE %r"%(slice,site)
        print '==================== Found %d inconsistent slices'%counter
    
    def spot_persons (self):
        "persons are expected to be in the same peer as their owning site"
        counter=0
        for person in self.all_persons:
            for site_id in person['site_ids']:
                site=self.site_hash[site_id]
                if person['peer_id'] != site['peer_id']:
                    counter+=1
                    if self.verbose: print "PERSON-SITE mismatch %r IN SITE %r"%(person,site)
        print '==================== Found %d inconsistent persons'%counter

    def spot_keys (self):
        "persons are expected to be in the same peer as their attached keys"
        counter=0
        for person in self.all_persons:
            for key_id in person['key_ids']:
                key=self.key_hash[key_id]
                if person['peer_id'] != key['peer_id']:
                    counter+=1
                    if self.verbose: print "PERSON-KEY mismatch %r & KEY %r"%(person,key)
        print '==================== Found %d inconsistent keys'%counter
    
    def spot_foreign (self):
        "foreign persons should not have a site"
        counter=1
        for person in self.all_persons:
            if person['peer_id'] and person['site_ids']:
                if self.verbose: print "WARNING Foreign person %r attached on sites:"%person
                for site_id in person['site_ids']:
                    counter+=1
                    if self.verbose: print "    %r"%self.site_hash[site_id]
        print '==================== Found %d foreign persons with a site'%counter

def main ():
    usage="""Usage: %prog [-- options]
Checks for db inconsistencies wrt remote peers
Mostly does damage assessment of running RefreshPeer together with SFA
If no option is set, performs all checks, otherwise performs the specified steps
"""
    parser=OptionParser (usage=usage)
    parser.add_option("-v","--verbose",action='store_true',dest='verbose',default=False)
    parser.add_option("-n","--nodes",action='store_true',dest='nodes',default=None,
                      help='check nodes')
    parser.add_option("-s","--slices",action='store_true',dest='slices',default=None,
                      help='check slices')
    parser.add_option("-p","--persons",action='store_true',dest='persons',default=None,
                      help='check persons')
    parser.add_option("-k","--keys",action='store_true',dest='keys',default=None,
                      help='check keys')
    parser.add_option("-f","--foreign",action='store_true',dest='foreign',default=None,
                      help='check foreign persons with a site')
    (options,args) = parser.parse_args()
    
    # default is to run all cheks
    # if at least one option was set, only enable the options that are set
    flags=['nodes','slices','persons','keys','foreign']
    nb_set = len ( [ getattr(options,flag) for flag in flags if getattr(options,flag) ] )
    
    if nb_set==0:
        for flag in flags: setattr(options,flag,True)

    spot = SpotAliens(verbose=options.verbose)
    if options.nodes: spot.spot_nodes()
    if options.slices: spot.spot_slices()
    if options.persons: spot.spot_persons()
    if options.keys: spot.spot_keys()
    if options.foreign: spot.spot_foreign()

if __name__ == '__main__':
    main()
