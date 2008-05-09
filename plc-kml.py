#!/usr/bin/env plcsh

# this script generates a kml file, located under the default location below
# you should crontab this job from your myplc image
# you can then use the googlemap.js javascript for creating your applet
# more on this at http://svn.planet-lab.org/wiki/GooglemapSetup

import sys

default_output       = "/var/www/html/sites/sites.kml"
default_local_icon   = "sites/google-local.png"
default_foreign_icon = "sites/google-foreign.png"

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

    def refresh (self):
        self.open()
        self.write_header()
        # cache peers 
        peers = GetPeers({},['peer_id','peername'])
        for site in GetSites({'enabled':True,'is_public':True}):
            self.write_site(site,peers)
        self.write_footer()
        self.close()

    def write_header (self):
        self.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
<name> PlanetLab Sites </name>
<description> All the sites known to the PlanetLab testbed. </description>
""")

    def write_footer (self):
        self.write("""</Document></kml>
""")

    def peer_name (self,site, peers):
        if not site['peer_id']:
            return "local"
        for peer in peers:
            if peer['peer_id'] == site['peer_id']:
                return peer['peername']

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

        # open description
        description='<ul>'
        # Name and URL
        description += '<li>'
        description += '<a href="%(apiurl)s/db/sites/index.php?id=%(site_id)d"> Site page </a>'%locals()
        if site['url']:
            site_url=site['url']
            description += ' -- <a href="%(site_url)s"> %(site_url)s </a>'%locals()
        description += '</li>'
        # NODES
        if nb_nodes:
            description += '<li>'
            description += '<a href="%(apiurl)s/db/nodes/index.php?site_id=%(site_id)d">%(nb_nodes)d node(s)</a>'%locals()
            description += '<a href="%(apiurl)s/db/nodes/comon.php?site_id=%(site_id)d"> (in Comon)</a>'%locals()
            description += '</li>'
        else:
            description += '<li>No node</li>'
        #SLICES
        if nb_slices:
            description += '<li><a href="%(apiurl)s/db/slices/index.php?site_id=%(site_id)d">%(nb_slices)d slice(s)</a></li>'%locals()
        else:
            description += '<li>No slice</li>'
        # PEER
        if peer_id:
            peername = self.peer_name(site,peers)
            description += '<li>'
            description += '<a href="%(apiurl)s/db/peers/index.php?id=%(peer_id)d">At peer %(peername)s</a>'%locals()
            description += '</li>'
        # close description
        description +='</ul>'

        # STYLE
        if self.options.use_google_icons:
            if not peer_id:
                # local sites
                iconfile="palette-4.png"
                xyspec="<x>128</x><y>0</y><w>32</w><h>32</h>"
            else:
                # remote
                iconfile="palette-3.png"
                xyspec="<x>160</x><y>0</y><w>32</w><h>32</h>"
            iconurl="root://icons/%(iconfile)s"%locals()
        else:
            if not peer_id:
                iconfile=self.options.local_icon
            else:
                iconfile=self.options.foreign_icon
            iconurl="%(baseurl)s/%(iconfile)s"%locals()
            xyspec=""

        iconspec="<href>%(iconurl)s</href>%(xyspec)s"%locals()

        template="""<Placemark>
<Style><IconStyle><Icon>%(iconspec)s</Icon></IconStyle></Style>
<name><![CDATA[%(name)s]]></name>
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
    parser.add_option("-c","--custom",action="store_false",dest="use_google_icons",
                      default=True,
                      help="use locally customized icons rather than the google-provided defaults")
    parser.add_option("-l","--local",action="store",dest="local_icon",
                      default=default_local_icon,
                      help="set icon url to use for local sites marker -- default is %s"%default_local_icon)
    parser.add_option("-f","--foreign",action="store",dest="foreign_icon",
                      default=default_foreign_icon,
                      help="set icon url to use for foreign sites marker -- default is %s"%default_foreign_icon)
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        sys.exit(1)
    KmlMap(options.output,options).refresh()

####################
if __name__ == "__main__":
    main()
