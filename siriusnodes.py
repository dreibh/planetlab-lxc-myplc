#!/usr/bin/python
'''
Subscribes new nodes to princeton_sirius slice.

$Id$
'''
import sys
from sets import Set

# Load shell with default configuration
sys.path.append('/usr/share/plc_api')
from PLC.Shell import Shell
plc = Shell(globals())



def main(argv = None):
	debug = False
	allnodes = []
	whitelist = []
	newnodes = []

	# Get All Nodes
	for node in GetNodes(None, ['node_id']): allnodes.append(node['node_id'])

	# Get WhiteListed nodes
	for node in GetWhitelist(None, ['node_id']): whitelist.append(node['node_id'])

	# Nodes already running slice
	siriusnodes = GetSlices("princeton_sirius")[0]['node_ids']

	available = Set(allnodes) - Set(whitelist)

	nodestoadd = available - Set(siriusnodes)

	for node in nodestoadd: newnodes.append(node)

	# Add to Sirius slice
	if debug:
		print newnodes
	else:
		AddSliceToNodes("princeton_sirius", [newnodes])
