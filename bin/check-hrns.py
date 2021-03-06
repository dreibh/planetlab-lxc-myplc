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
        for node_id in site.get('node_ids', []):
            try:    node=nodes_by_id[node_id]
            except: print('cannot find node %s'%node_id); continue
            hrn=hostname_to_hrn (toplevel, login_base, node['hostname'])
            if node['hrn'] != hrn:
                if verbose:
                    print("Node %s - current hrn %s, should be %s"%(node['hostname'], node['hrn'], hrn))
                if dry_run: continue
                SetNodeHrn (node['node_id'],hrn)
            else:
                if verbose: print("Node %s OK"%node['hostname'])

def handle_persons (sites,sites_by_id, dry_run,verbose): 
    persons=GetPersons ({'peer_id':None},['person_id','email','hrn','site_ids'])
    persons_by_id = dict ( [ (person['person_id'],person) for person in persons ] )
    for site in sites:
        login_base=site['login_base']
        for person_id in site.get('person_ids', []):
            try:    person=persons_by_id[person_id]
            except: print('cannot find person %s'%person_id); continue
            how_many=len(person['site_ids'])
            if how_many !=1:
                if verbose: print("Checking persons in exactly one site -- person %s in %s site(s) -- ignored"%(person['email'],how_many))
                continue

            hrn=email_to_hrn ("%s.%s"%(toplevel,login_base),person['email'])
            if person['hrn'] != hrn:
                if verbose:
                    print("Person %s - current hrn %s, should be %s"%(person['email'], person['hrn'], hrn))
                if dry_run: continue
                SetPersonHrn (person['person_id'],hrn)
            else:
                if verbose: print("Person %s OK"%person['email'])


def handle_slices (sites,sites_by_id, dry_run,verbose):
    slices=GetSlices ({'peer_id':None},['slice_id','name','hrn','site_id'])
    slices_by_id = dict ( [ (slice['slice_id'],slice) for slice in slices ] )
    for site in sites:
        login_base=site['login_base']
        for slice_id in site.get('slice_ids', []):
            try:    slice=slices_by_id[slice_id]
            except: print('cannot find slice %s'%slice_id); continue
            hrn=slicename_to_hrn (toplevel, slice['name'])
            if slice['hrn'] != hrn:
                if verbose:  
                    print("Slice %s - current hrn %s, should be %s"%(slice['name'], slice['hrn'], hrn))
                if dry_run: continue
                SetSliceHrn (slice['slice_id'],hrn)
            else:
                if verbose: print("Slice %s OK"%slice['name'])


def handle_sites (sites,sites_by_id, dry_run,verbose):
    for site in sites:
        hrn='.'.join([toplevel, site['login_base']])
        if site['hrn'] != hrn:
            if verbose:
                print("Site %s - current hrn %s, should be %s"%(site['name'].encode('ascii', 'ignore'), site['hrn'], hrn))
            if dry_run: continue
            SetSiteHrn (site['site_id'],hrn)
        else:
            if verbose: print("Site %s OK"%site['name'])
        

            
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
    parser.add_option("-t", "--site", action = "store_true", default = False,
                      dest='sites',help="run on sites")
    parser.add_option("-s", "--show", action = "store_true", default = False, 
                      dest='show', help="dry run, only show discrepencies")
    parser.add_option("-v", "--verbose", action = "store_true", default = False, 
                      dest='verbose', help="be verbose")
    (options, args) = parser.parse_args()

    if args: 
        parser.print_help()
        sys.exit(1)
    # if neither -p nor -n, run both
    if not options.nodes and not options.persons and not options.slices and not options.sites:
        options.nodes=True
        options.persons=True
        options.slices=True        
        options.sites=True

    dry_run=options.show
    verbose=options.verbose
    # optimizing : we compute the set of sites only once
    sites = GetSites({'peer_id':None},['site_id','login_base','node_ids','person_ids','name','hrn','slice_ids', 'sfa_created'])
    # remove external sites created through SFA
    sites = [site for site in sites if site['sfa_created'] != 'True']
    sites_by_id = dict ( [ (site['site_id'], site) for site in sites ] )

    if options.nodes: handle_nodes(sites,sites_by_id,dry_run,verbose)
    if options.persons: handle_persons(sites,sites_by_id,dry_run,verbose)
    if options.slices: handle_slices(sites,sites_by_id,dry_run,verbose)
    if options.sites: handle_sites(sites,sites_by_id,dry_run,verbose)

if __name__ == "__main__":
    main()
