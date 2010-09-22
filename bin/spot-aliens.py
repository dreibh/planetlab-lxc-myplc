#!/usr/bin/plcsh

all_sites=GetSites({},['peer_id','site_id','login_base','name'])
all_nodes=GetNodes({},['peer_id','node_id','site_id','hostname'])
all_persons=GetPersons({},['peer_id','person_id','site_ids','key_ids','email'])
all_keys=GetKeys({},['peer_id','key_id'])
all_slices=GetSlices({},['peer_id','slice_id','name','site_id'])

site_hash=dict ( [ (site['site_id'],site) for site in all_sites ] )
#node_hash=dict ( [ (node['node_id'],node) for node in all_nodes ] )
#person_hash=dict ( [ (person['person_id'],person) for person in all_persons ] )
key_hash=dict ( [ (key['key_id'],key) for key in all_keys ] )
slice_hash=dict ( [ (slice['slice_id'],slice) for slice in all_slices ] )

# nodes are expected to be in the same peer as their owning site
for node in all_nodes:
    site=site_hash[node['site_id']]
    if node['peer_id'] != site['peer_id']: 
        print "NODE-SITE mismatch %r IN SITE %r"%(node,site)

# same for slices
for slice in all_slices:
    site=site_hash[slice['site_id']]
    if slice['peer_id'] != site['peer_id']: 
        print "SLICE-SITE mismatch %r IN SITE %r"%(slice,site)

# same for persons
for person in all_persons:
    for site_id in person['site_ids']:
        site=site_hash[site_id]
        if person['peer_id'] != site['peer_id']:
            print "PERSON-SITE mismatch %r IN SITE %r"%(person,site)

# persons and keys
for person in all_persons:
    for key_id in person['key_ids']:
        key=key_hash[key_id]
        if person['peer_id'] != key['peer_id']:
            print "PERSON-KEY mismatch %r & KEY %r"%(person,key)

        
### check that foreign persons don't have a site
# funny thing is, this actually populates stuff properly
# but the usual refreshpeer does not provide this data, so..
for person in all_persons:
    if person['peer_id'] and person['site_ids']:
        print "WARNING Foreign person %r attached on sites:"%person
        for site_id in person['site_ids']:
            print "    %r"%site_hash[site_id]
