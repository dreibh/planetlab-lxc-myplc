#!/usr/bin/env plcsh
import sys
from optparse import OptionParser

from PLC.Namespace import hostname_to_hrn, email_to_hrn, slicename_to_hrn
# (auth_hrn, email):

toplevel=api.config.PLC_HRN_ROOT

def handle_nodes (sites,sites_by_id, dry_run, verbose):
    nodes=GetNodes ({'peer_id':None},['node_id','hostname','hrn'])
    nodes_by_id = dict ( [ (node['node_id'],node) for node in nodes ] )
    for site in sites:
        login_base=site['login_base']
        for node_id in site['node_ids']:
            try:    node=nodes_by_id[node_id]
            except: print 'cannot find node %s'%node_id; continue
            hrn=hostname_to_hrn (toplevel, login_base, node['hostname'])
            if node['hrn'] != hrn:
                print "Node %s - current hrn %s, should be %s"%(node['hostname'], node['hrn'], hrn)
                if dry_run: continue
                SetNodeHrn (node['node_id'],hrn)
            else:
                if verbose: print "Node %s OK"%node['hostname']

def handle_persons (sites,sites_by_id, dry_run,verbose): 
    persons=GetPersons ({'peer_id':None},['person_id','email','hrn','site_ids'])
    for person in persons:
        how_many=len(person['site_ids'])
        if how_many !=1:
            if verbose: print "Checking persons in exactly one site -- person %s in %s site(s) -- ignored"%(person['email'],how_many)
            continue
        try:    login_base=sites_by_id[person['site_ids'][0]]['login_base']
        except: print "Cannot handle person %s - site not found"%person['email']; continue
        hrn=email_to_hrn ("%s.%s"%(toplevel,login_base),person['email'])
        if person['hrn'] != hrn:
            print "Person %s - current hrn %s, should be %s"%(person['email'], person['hrn'], hrn)
            if dry_run: continue
            SetPersonHrn (person['person_id'],hrn)
        else:
            if verbose: print "Person %s OK"%person['email']


def handle_slices (sites,sites_by_id, dry_run,verbose):
    slices=GetSlices ({'peer_id':None},['slice_id','name','hrn','site_id'])
    for slice in slices:
        try:    login_base=sites_by_id[slice['site_id']]['login_base']
        except: print "Cannot handle slice %s - site not found"%slice['name']; continue
        hrn=slicename_to_hrn (toplevel, slice['name'])
        if slice['hrn'] != hrn:
            print "Slice %s - current hrn %s, should be %s"%(slice['name'], slice['hrn'], hrn)
            if dry_run: continue
            SetSliceHrn (slice['slice_id'],hrn)
        else:
            if verbose: print "Slice %s OK"%slice['name']

        
            
def main():
    usage="""Usage: %prog
  Checks that the hrn tags are correctly set
Example:
  %prog -- -p -nv
"""
    parser = OptionParser(usage=usage)
    parser.add_option("-p", "--person", action = "store_true", default = False, 
                      dest='persons',help="run on persons")
    parser.add_option("-n", "--node", action = "store_true", default = False, 
                      dest='nodes',help="run on nodes")
    parser.add_option("-S", "--slice", action = "store_true", default = False,
                      dest='slices',help="run on slices")
    parser.add_option("-s", "--show", action = "store_true", default = False, 
                      dest='show', help="dry run, only show discrepencies")
    parser.add_option("-v", "--verbose", action = "store_true", default = False, 
                      dest='verbose', help="be verbose")
    (options, args) = parser.parse_args()

    if args: 
        parser.print_help()
        sys.exit(1)
    # if neither -p nor -n, run both
    if not options.nodes and not options.persons and not options.slices:
        options.nodes=True
        options.persons=True
        options.slices=True        

    dry_run=options.show
    verbose=options.verbose
    # optimizing : we compute the set of sites only once
    sites = GetSites({'peer_id':None},['site_id','login_base','node_ids','person_ids','name'])
    # remove external sites created through SFA
    sites = [site for site in sites if not site['name'].startswith('sfa.')]

    sites_by_id = dict ( [ (site['site_id'], site) for site in sites ] )
    if options.nodes: handle_nodes(sites,sites_by_id,dry_run,verbose)
    if options.persons: handle_persons(sites,sites_by_id,dry_run,verbose)
    if options.slices: handle_slices(sites,sites_by_id,dry_run,verbose)

if __name__ == "__main__":
    main()
