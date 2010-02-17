#!/usr/bin/env /usr/bin/plcsh
#
# Generates static versions of expensive web pages
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2005 The Trustees of Princeton University
#
# $Id: gen-static-content.py,v 1.35.2.1 2007/02/07 03:27:50 mlhuang Exp $
#

import os, sys, shutil
import time
import string
import codecs
import socket
import urllib2
import csv

SCRIPT_PID_FILE= "/var/run/gen-static-content.pid"

# where to store the generated files
GENERATED_OUTPUT_PATH= '/var/www/html/generated'

# this php block, if put at the top of the files,
# will enable them to be downloaded without the php
# engine parsing them
DISABLE_PHP_BLOCK= \
"""<?php
if( isset($_GET['disablephp']) )
  {
    readfile(__FILE__);
    exit();
  }
?>
"""

# Globals
all_nodes = []
all_sites = []
node_group_nodes = {}

# return a php page that has node and site counts in it
def GetCountsFileContent(f):
    f.write( DISABLE_PHP_BLOCK )
    f.write( "<?php\n" )

    node_count = len(all_nodes)
    f.write( "$node_count= %s;\n" % node_count )
    
    site_count= len(all_sites)
    f.write( "$site_count= %s;\n" % site_count )

    f.write( "?>" )


# generate a plain text file in ~/.ssh/known_hosts format
def GetHostKeys(f):
    time_generated= time.strftime("%a, %d %b %Y %H:%M:%S")

    f.write( DISABLE_PHP_BLOCK )
    
    f.write( "<?php\n" )
    f.write( "$node_list_generated_time= '%s';\n" % time_generated )
    f.write( "header('Content-type: text/plain');\n" )
    f.write( "?>\n" )

    nodes = all_nodes

    for node in all_nodes:
        hostname = node['hostname']
        ssh_rsa_key = node['ssh_rsa_key']
        ip = node['ip']
        if ssh_rsa_key:
            if hostname:
                f.write( "%s %s\n" % (hostname, ssh_rsa_key) )
            if ip:
                f.write( "%s %s\n" % (ip, ssh_rsa_key) )


# return php content that includes all the node lists
def GetNodeListsContent(f):
    time_generated= time.strftime("%a, %d %b %Y %H:%M:%S")

    f.write( DISABLE_PHP_BLOCK )
    
    f.write( "<?php\n" )
    f.write( "$node_list_generated_time= '%s';\n" % time_generated )

    # Nodes with primary IP addresses in boot state
    nodes_in_boot = filter(lambda node: node['boot_state'] == "boot" and node['ip'],
                           all_nodes)

    # Hostnames
    all_hosts = [node['hostname'] for node in nodes_in_boot]
    f.write( "if( $which_node_list == 'all_hosts' )\n" )
    f.write( "{\n" )
    f.write( "?>\n" )
    f.write( "\n".join(all_hosts) + "\n" )
    f.write( "<?php\n" )
    f.write( "}\n" )

    # IPs
    all_ips = [node['ip'] for node in nodes_in_boot]
    f.write( "elseif( $which_node_list == 'all_ips' )\n" )
    f.write( "{\n" )
    f.write( "?>\n" )
    f.write( "\n".join(all_ips) + "\n" )
    f.write( "<?php\n" )
    f.write( "}\n" )

    # /etc/hosts entries
    etc_hosts = [node['ip'] + "\t" + node['hostname'] for node in nodes_in_boot]
    f.write( "elseif( $which_node_list == 'etc_hosts' )\n" )
    f.write( "{\n" )
    f.write( "?>\n" )
    # Create a localhost entry for convenience
    f.write( "127.0.0.1\tlocalhost.localdomain localhost\n" )
    f.write( "\n".join(etc_hosts) + "\n" )
    f.write( "<?php\n" )
    f.write( "}\n" )

    for group in ['Alpha', 'Beta']:
        if not node_group_nodes.has_key(group):
            node_group_nodes[group] = []

        # Group nodes with primary IP addresses in boot state
        group_nodes_in_boot = filter(lambda node: node['boot_state'] == "boot" and node['ip'],
                                     node_group_nodes[group])

        # Group hostnames
        group_hosts = [node['hostname'] for node in group_nodes_in_boot]
        f.write( "elseif( $which_node_list == '%s_hosts' )\n" % group.lower() )
        f.write( "{\n" )
        f.write( "?>\n" )
        f.write( "\n".join(group_hosts) + "\n" )
        f.write( "<?php\n" )
        f.write( "}\n" )

        # Group IPs
        group_ips = [node['ip'] for node in group_nodes_in_boot]
        f.write( "elseif( $which_node_list == '%s_ips' )\n" % group.lower() )
        f.write( "{\n" )
        f.write( "?>\n" )
        f.write( "\n".join(group_ips) + "\n" )
        f.write( "<?php\n" )
        f.write( "}\n" )

    # All production nodes (nodes not in Alpha or Beta)
    production_nodes_in_boot = filter(lambda node: node not in node_group_nodes['Alpha'] and \
                                                   node not in node_group_nodes['Beta'],
                                      nodes_in_boot)

    production_hosts = [node['hostname'] for node in production_nodes_in_boot]                           
    f.write( "elseif( $which_node_list == 'production_hosts' )\n" )
    f.write( "{\n" )
    f.write( "?>\n" )
    f.write( "\n".join(production_hosts) + "\n" )
    f.write( "<?php\n" )
    f.write( "}\n" )

    production_ips = [node['ip'] for node in production_nodes_in_boot]                           
    f.write( "elseif( $which_node_list == 'production_ips' )\n" )
    f.write( "{\n" )
    f.write( "?>\n" )
    f.write( "\n".join(production_ips) + "\n" )
    f.write( "<?php\n" )
    f.write( "}\n" )
    f.write( "?>" )


def GetPlanetFlowStats(f):
    if hasattr(config, 'PLANETFLOW_BASE'):
        url = "http://" + config.PLANETFLOW_BASE
    else:
        return

    # Slices to calculate detailed statistics for
    slices = [
        'cmu_esm',
        'cornell_beehive',
        'cornell_cobweb',
        'cornell_codons',
        'michigan_tmesh',
        'nyu_d',
        'princeton_codeen',
        'princeton_coblitz',
        'princeton_comon',
        'rice_epost',
        'ucb_bamboo',
        'ucb_i3',
        'ucsd_sword',
        'upenn_dharma',
        'idsl_psepr',
        'ucb_ganglia',
        'cmu_irislog',
        'tennessee_hliu'
        ]

    # Seconds to wait
    socket.setdefaulttimeout(3600)

    url = url + '/slice.php?csv=1&start_time=2+days+ago'
    if slices:
        url = url + '&slices[]=' + '&slices[]='.join(slices)
    stats = urllib2.urlopen(url)
    fields = ['slice', 'flows', 'packets', 'bytes', 'src_ips',
              'dst_ips', 'top_dst_ip', 'top_dst_ip_bytes']
    rows = csv.DictReader(stats, fields)
    f.write("<?php\n")
    f.write("$planetflow = array(\n")
    for row in rows:
        if row.has_key('slice'):
            f.write("'%s' => array(\n" % row['slice'])
            for field in fields:
                if row.has_key(field) and \
                   row[field] is not None and \
                   row[field] != "":
                    if type(row[field]) == type(0):
                        f.write("\t'%s' => %d,\n" % (field, int(row[field])))
                    else:
                        f.write("\t'%s' => '%s',\n" % (field, row[field]))
            f.write("),\n")
    f.write(");\n")
    f.write("?>")



def GenDistMap():
    # update the node distribution map
    datadir = '/var/www/html/plot-latlong'

    # plot-latlong looks for .mapinfo and .mapimages in $HOME
    os.environ['HOME'] = datadir

    if hasattr(config, 'PLC_WWW_MAPIMAGE'):
        image = config.PLC_WWW_MAPIMAGE
    else:
        image = "World50"

    (child_stdin,
     child_stdout) = \
     os.popen2('perl ' + datadir + os.sep + 'plot-latlong -m "%s" -s 3' % image)

    for site in all_sites:
        if site['latitude'] and site['longitude']:
            child_stdin.write("%f %f\n" % \
                              (site['latitude'], site['longitude']))
    child_stdin.close()

    map = file(GENERATED_OUTPUT_PATH + os.sep + image + '.png', 'w')
    map.write(child_stdout.read())
    child_stdout.close()
    map.close()


# which files to generate, and the functions in
# this script to call to get the content for
STATIC_FILE_LIST= (
    ('_gen_counts.php',GetCountsFileContent),
    ('_gen_node_lists.php',GetNodeListsContent),
    ('_gen_known_hosts.php',GetHostKeys),
    ('_gen_planetflow.php',GetPlanetFlowStats),
    (None,GenDistMap)
    )


if __name__ == '__main__':

    # see if we are already running by checking the existance
    # of a PID file, and if it exists, attempting a test kill
    # to see if the process really does exist. If both of these
    # tests pass, exit.
        
    if os.access(SCRIPT_PID_FILE, os.R_OK):
        pid= string.strip(file(SCRIPT_PID_FILE).readline())
        if pid <> "":
            if os.system("/bin/kill -0 %s > /dev/null 2>&1" % pid) == 0:
                sys.exit(0)
            
    # write out our process id
    pidfile= file( SCRIPT_PID_FILE, 'w' )
    pidfile.write( "%d\n" % os.getpid() )
    pidfile.close()
    pidfile= None

    # Get all nodes and sites
    begin()
    GetNodes(None, ['node_id', 'hostname', 'boot_state', 'ssh_rsa_key', 'interface_ids'])
    GetInterfaces(None, ['interface_id', 'ip', 'is_primary'])
    GetSites(None, ['site_id', 'latitude', 'longitude'])
    GetNodeGroups(None, ['nodegroup_id', 'tagname', 'node_ids'])
    (all_nodes, all_nodenetworks, all_sites, all_groups) = commit()

    all_nodenetworks = dict([(nodenetwork['interface_id'], nodenetwork) \
                             for nodenetwork in all_nodenetworks])

    # Set primary IP, if any
    for node in all_nodes:
        node['ip'] = None
        for interface_id in node['interface_ids']:
            try:
                nodenetwork = all_nodenetworks[interface_id]
                if nodenetwork['is_primary']:
                    node['ip'] = nodenetwork['ip']
                break
            except IndexError, KeyError:
                continue

    # Get list of nodes in each node group
    for group in all_groups:
        nodes_in_group = filter(lambda node: node['node_id'] in group['node_ids'], all_nodes)
        node_group_nodes[group['tagname']] = nodes_in_group

    # generate the static content files
    for (file_name,func) in STATIC_FILE_LIST:
        if file_name is not None:
            try:
                output_file_path= "%s/%s" % (GENERATED_OUTPUT_PATH,file_name)
                tmp_output_file_path= output_file_path + '.tmp'
                tmp_output_file= codecs.open( tmp_output_file_path, encoding = 'utf-8', mode = "w" )
            except IOError, err:
                print( "Unable to open file %s for writing." % output_file_path )
                continue

            try:
                func(tmp_output_file)
                tmp_output_file.flush()
                shutil.copyfile( tmp_output_file_path, output_file_path )
            except Exception, e:
                print "Unable to get content for file: %s" % file_name, e
                import traceback
                traceback.print_exc()

            tmp_output_file.close()
            tmp_output_file= None
            os.unlink( tmp_output_file_path )
        else:
            func()

    # remove the PID file
    os.unlink( SCRIPT_PID_FILE )
