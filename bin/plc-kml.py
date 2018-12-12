#!/usr/bin/env plcsh
#
# this script generates a kml file, located under the default location below
# you should crontab this job from your myplc image
# you can then use the googlemap.js javascript for creating your applet
# more on this at http://svn.planet-lab.org/wiki/GooglemapSetup
# 
# kml reference can be found at
# http://code.google.com/apis/kml/documentation/kmlreference.html
#

import sys

default_output           = "/var/www/html/sites/sites.kml"
default_local_icon       = "sites/google-local.png"
default_foreign_icon     = "sites/google-foreign.png"
default_local_builtin    = "palette-4.png"
default_foreign_builtin  = "palette-3.png"

# cosmetic - peername cannot be easily changed on the PLC-PLE link...
def render_public_name (peername):
    if peername=='PlanetLab': return "PlanetLab Central"
    elif peername == 'PlanetLabEurope': return "PlanetLab Europe"
    else: return peername

class KmlMap:

    def __init__ (self,outputname,options):
        self.outputname=outputname
        self.options=options

    def open (self):
        self.output = open(self.outputname,"w")

    def close (self):
        if self.output:
            self.output.close()
        self.output = None

    def write(self,string):
        self.output.write(string.encode("UTF-8"))

# initial placement is for europe - dunno how to tune that yet
    def write_header (self):
        if not self.options.nodegroup:
            local_peername=render_public_name(api.config.PLC_NAME)
            title="%s sites"%local_peername
            detailed="All the sites known to the %s testbed"%local_peername
        else:
            title="Nodegroup %s"%self.options.nodegroup
            detailed="All sites involved in nodegroup %s"%self.options.nodegroup
        self.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
<name> %(title)s </name>
<LookAt>
<longitude>9.180821112577378</longitude>
<latitude>44.43275321178062</latitude>
<altitude>0</altitude>
<range>5782133.196489797</range>
<tilt>0</tilt>
<heading>-7.767386340832667</heading>
</LookAt>
<description> %(detailed)s. </description>
"""%locals())

    def write_footer (self):
        self.write("""</Document></kml>
""")

    def peer_info (self,site, peers):
        if not site['peer_id']:
            return (render_public_name(api.config.PLC_NAME), "http://%s/"%api.config.PLC_API_HOST,)
        for peer in peers:
            if peer['peer_id'] == site['peer_id']:
                return (render_public_name(peer['peername']),peer['peer_url'].replace("PLCAPI/",""),)
        return "Unknown peer_name"

    # mention local last 
    @staticmethod
    def site_compare (s1,s2):
        p1 = p2 = 0
        if s1['peer_id']: p1=s1['peer_id']
        if s2['peer_id']: p2=s2['peer_id']
        return p2-p1

    ####################
    def refresh (self):
        if self.options.nodegroup:
            self.refresh_nodegroup()
        else:
            self.refresh_all_sites()

    def refresh_all_sites(self):
        self.open()
        self.write_header()
        # cache peers 
        peers = GetPeers()
        all_sites = GetSites({'enabled':True,'is_public':True})
        all_sites.sort(KmlMap.site_compare)
        for site in all_sites:
            self.write_site(site,peers)
        self.write_footer()
        self.close()

    def refresh_nodegroup(self):
        try:
            nodegroup=GetNodeGroups({'groupname':self.options.nodegroup})[0]
        except:
            print("No such nodegroup %s - ignored"%self.options.nodegroup)
            return
        nodegroup_node_ids=nodegroup['node_ids']
        if len(nodegroup_node_ids)==0:
            print("Empty nodegroup %s - ignored"%self.options.nodegroup)
            return
        # let's go
        self.open()
        self.write_header()
        # cache peers 
        peers = GetPeers()
        nodes=GetNodes(nodegroup_node_ids)
        global_node_hash = dict ( [ (n['node_id'],n) for n in nodes ] )
        site_ids = [ node['site_id'] for node in nodes]
        # remove any duplicate
        site_ids = list(set(site_ids))
        sites = GetSites (site_ids)
        # patch sites so that 'node_ids' only contains the nodes in the nodegroup
        for site in sites:
            site['node_ids'] = [ node_id for node_id in site['node_ids'] if node_id in nodegroup_node_ids ]
            node_hash = dict ( [ (node_id, global_node_hash[node_id]) for node_id in site['node_ids'] ] )
            self.write_site(site,peers,nodegroup_id=nodegroup['nodegroup_id'], node_hash=node_hash)
        self.write_footer()
        self.close()

    def write_site (self, site, peers, nodegroup_id=False, node_hash={}):
        # discard sites with missing lat or lon
        if not site['latitude'] or not site['longitude']:
            return
        # discard sites with no nodes 
        if len(site['node_ids']) == 0:
            return

        site_id=site['site_id']
        name=site['name']
        nb_nodes=len(site['node_ids'])
        nb_slices=len(site['slice_ids'])
        latitude=site['latitude']
        longitude=site['longitude']
        apiurl='https://%s:443'%api.config.PLC_WWW_HOST
        baseurl='http://%s'%api.config.PLC_WWW_HOST
        peer_id=site['peer_id']

        # STYLE
        # the size for google icons
        if not self.options.use_custom_icons:
            if not peer_id:
                # local sites
                iconfile=default_local_builtin
                xyspec="<x>128</x><y>0</y><w>32</w><h>32</h>"
            else:
                # remote
                iconfile=default_foreign_builtin
                xyspec="<x>160</x><y>0</y><w>32</w><h>32</h>"
            iconurl="root://icons/%(iconfile)s"%locals()
        # the size for our own brew of icons
        else:
            if not peer_id:
                iconfile=self.options.local_icon
            else:
                iconfile=self.options.foreign_icon
            iconurl="%(baseurl)s/%(iconfile)s"%locals()
            xyspec=""

        iconspec="<href>%(iconurl)s</href>%(xyspec)s"%locals()

        # open description
        # can't seem to get classes to get through to the google maps API
        # so have to use hard-wired settings
        description = ""
        description += "<table style='border: 1px solid black; padding: 3px; margin-top:5px;' width='300px'>"
        description += "<thead></thead><tbody>"

        # TESTBED
        description += "<tr>"
        description += "<td style='font-weight: bold'>Testbed</td>"
        (peername,peerurl) = self.peer_info (site,peers)
        description += "<td style='vertical-align:middle;'>"
        description += "<p><img src='%(iconurl)s' style='vertical-align:middle;'/>"%locals()
        description += "<a href='%(peerurl)s' style='text-decoration:none;vertical-align:middle;'> %(peername)s </a>"%locals()
	description += "</p></td></tr>"

	# URL
        if site['url']:
            site_url=site['url']
            description += "<tr>"
            description += "<td style='font-weight: bold'>Website</td>"
            description += "<td>"
            description += "<a style='text-decoration: none;' href='%(site_url)s'> %(site_url)s </a>"%locals()
            description += "</td>"
            description += "</tr>"

        # nodegroup direct link
        if self.options.nodegroup:
            nodegroup=self.options.nodegroup
            description += "<tr>"
            description += "<td style='font-weight: bold'>Nodegroup</td>"
            description += "<td>"
            description += "<a style='text-decoration: none;' href='/planetlab/tags/nodegroups.php?id=%(nodegroup_id)d'> %(nodegroup)s </a>"%locals()
            description += "</td>"
            description += "</tr>"


        # Usage area
        if not nodegroup_id: title="Usage"
        else: title="Nodes"
        description += "<tr>"
        description += "<td style='font-weight: bold; margin-bottom:2px;'>%(title)s</td>"%locals()

        # encapsulate usage in a table of its own
        description += "<td>"
        description += "<table style=''>"
        description += "<thead></thead><tbody>"

        # NODES
        # regular all-sites mode
        if not nodegroup_id:
            description += "<tr><td align='center'>"
            description += "<img src='%(apiurl)s/googlemap/node.png'/>"%locals()
            description += "</td><td>"
            if nb_nodes:
                description += "<a style='text-decoration: none;' href='%(apiurl)s/db/nodes/index.php?site_id=%(site_id)d'>%(nb_nodes)d node(s)</a>"%locals()
            else:
                description += "<i>No node</i>"
            description += "</td></tr>"
        # nodegroup mode : show all nodes
        else:
            for node_id in site['node_ids']:
                node=node_hash[node_id]
                hostname=node['hostname']
                description += "<tr><td align='center'>"
                description += "<img src='%(apiurl)s/googlemap/node.png'/>"%locals()
                description += "</td><td>"
                description += "<a style='text-decoration: none;' href='%(apiurl)s/db/nodes/index.php?id=%(node_id)d'>%(hostname)s </a>"%locals()
                description += "</td></tr>"

        #SLICES
        if not nodegroup_id:
            description += "<tr><td align='center'>"
            description += "<img src='%(apiurl)s/googlemap/slice.png'/>"%locals()
            description += "</td><td>"
            if nb_slices:
                description += "<a style='text-decoration: none;' href='%(apiurl)s/db/slices/index.php?site_id=%(site_id)d'>%(nb_slices)d slice(s)</a>"%locals()
            else:
                description += "<span style='font-style:italic;'>No slice</span>"
                description += "</td></tr>"
        
        # close usage table
        description += "</tbody></table>"
        description += "</td></tr>"

        # close description
        description += "</tbody></table>"

        if not self.options.labels:
            name=""
            description=""

        # set the camera 50km high
        template="""<Placemark>
<Style><IconStyle><Icon>%(iconspec)s</Icon></IconStyle></Style>
<name><![CDATA[%(name)s]]></name>
<LookAt>
  <latitude>%(latitude)f</latitude>
  <longitude>%(longitude)f</longitude>
  <altitude>0</altitude>
  <altitudeMode>relativeToGround</altitudeMode>              
  <range>50000.</range> 
</LookAt>
<description><![CDATA[%(description)s]]></description>
<Point> <coordinates>%(longitude)f,%(latitude)f,0</coordinates> </Point>
</Placemark>
"""
        self.write(template%locals())

def main () :
    from optparse import OptionParser
    usage = "Usage %prog [plcsh-options] [ -- options ]"
    parser = OptionParser (usage=usage)

    parser.add_option("-o","--output",action="store",dest="output",
                      default=default_output,
                      help="output file - default is %s"%default_output)
    parser.add_option("-n","--no-label",action="store_false",dest="labels",
                      default=True,
                      help="outputs only geographic positions, no labels")

    parser.add_option("-g","--nodegroup",action='store',dest='nodegroup',default=None,
                      help="outputs a kml file for a given nodegroup only")

    # default - for private depls. - is to use google-provided icons like palette-3
    parser.add_option("-c","--custom",action="store_true",dest="use_custom_icons",
                      default=False,
                      help="use locally customized icons rather than the %s and %s defaults"%(default_local_builtin,default_foreign_builtin))
    parser.add_option("-l","--local",action="store",dest="local_icon",
                      default=default_local_icon,
                      help="set icon url to use for local sites marker -- requires -c -- default is %s"%default_local_icon)
    parser.add_option("-f","--foreign",action="store",dest="foreign_icon",
                      default=default_foreign_icon,
                      help="set icon url to use for foreign sites marker -- requires -c -- default is %s"%default_foreign_icon)

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        sys.exit(1)
    KmlMap(options.output,options).refresh()

####################
if __name__ == "__main__":
    main()
