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

    # mention local last 
    @staticmethod
    def site_compare (s1,s2):
        p1 = p2 = 0
        if s1['peer_id']: p1=s1['peer_id']
        if s2['peer_id']: p2=s2['peer_id']
        return p2-p1

    def refresh (self):
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

# initial placement is for europe - dunno how to tune that yet
    def write_header (self):
        self.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
<name> PlanetLab Sites </name>
<LookAt>
<longitude>9.180821112577378</longitude>
<latitude>44.43275321178062</latitude>
<altitude>0</altitude>
<range>5782133.196489797</range>
<tilt>0</tilt>
<heading>-7.767386340832667</heading>
</LookAt>
<description> All the sites known to the PlanetLab testbed. </description>
""")

    def write_footer (self):
        self.write("""</Document></kml>
""")

    def peer_info (self,site, peers):
        if not site['peer_id']:
            return (api.config.PLC_NAME, "http://%s/"%api.config.PLC_API_HOST,)
        for peer in peers:
            if peer['peer_id'] == site['peer_id']:
                return (peer['peername'],peer['peer_url'].replace("PLCAPI/",""),)
        return "Unknown peer_name"

    def write_site (self, site, peers):
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

        # Usage area
        description += "<tr>"
        description += "<td style='font-weight: bold; margin-bottom:2px;'>Usage</td>"

        # encapsulate usage in a table of its own
        description += "<td>"
        description += "<table style=''>"
        description += "<thead></thead><tbody>"

        # NODES
        description += "<tr><td align='center'>"
        description += "<img src='%(apiurl)s/googlemap/node.png'/>"%locals()
        description += "</td><td>"
        if nb_nodes:
            description += "<a style='text-decoration: none;' href='%(apiurl)s/db/nodes/index.php?site_id=%(site_id)d'>%(nb_nodes)d node(s)</a>"%locals()
            #description += "<a style='text-decoration: none;' href='%(apiurl)s/db/nodes/comon.php?site_id=%(site_id)d'> (in Comon)</a>"%locals()
        else:
            description += "<i>No node</i>"
        description += "</td></tr>"

        #SLICES
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
