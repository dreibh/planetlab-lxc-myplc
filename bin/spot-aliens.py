#!/usr/bin/plcsh

# nodes in a site are expected to be in the same peer as their owning site

all_sites=GetSites({},['login_base','name','site_id','peer_id'])
all_nodes=GetNodes({},['node_id','hostname','peer_id','site_id'])

node_hash=dict ( [ (node['node_id'],node) for node in all_nodes ] )
site_hash=dict ( [ (site['site_id'],site) for site in all_sites ] )

for node in all_nodes:
    site=site_hash[node['site_id']]
    if node['peer_id'] != site['peer_id']: 
        print "mismatch with %r and site %r"%(node,site)

