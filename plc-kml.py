#!/usr/bin/env plcsh

# this script generates a kml file, located under the default location below
# you should crontab this job from your myplc image
# you can then use the googlemap.js javascript for creating your applet
# more on this at http://svn.planet-lab.org/wiki/GooglemapSetup

import sys

default_output="/var/www/html/sites/sites.kml"

class KmlMap:

    def __init__ (self,outputname):
        self.outputname=outputname

    def open (self):
        self.output = open(self.outputname,"w")

    def close (self):
        if self.output:
            self.output.close()
        self.output = None

    def refresh (self):
        self.open()
        self.write_header()
        # cache peers 
        peers = GetPeers({},['peer_id','peername'])
        for site in GetSites({'enabled':True,'is_public':True}):
            self.write_site(site,peers)
        self.write_footer()
        self.close()

    def write(self,string):
        self.output.write(string.encode("UTF-8"))

    def write_header (self):
        self.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
<name> PlanetLab Sites </name>
<description> This map shows all sites knows to the PlanetLab testbed. </description>
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
        baseurl='https://%s:443'%api.config.PLC_WWW_HOST
        
        # open description
        description='<ul>'
        # Name and URL
        description += '<li>'
        description += '<a href="%(baseurl)s/db/sites/index.php?id=%(site_id)d"> Site page </a>'%locals()
        if site['url']:
            site_url=site['url']
            description += ' -- <a href="%(site_url)s"> %(site_url)s </a>'%locals()
        description += '</li>'
        # NODES
        if nb_nodes:
            description += '<li>'
            description += '<a href="%(baseurl)s/db/nodes/index.php?site_id=%(site_id)d">%(nb_nodes)d node(s)</a>'%locals()
            description += '<a href="%(baseurl)s/db/nodes/comon.php?site_id=%(site_id)d"> (in Comon)</a>'%locals()
            description += '</li>'
        else:
            description += '<li>No node</li>'
        #SLICES
        if nb_slices:
            description += '<li><a href="%(baseurl)s/db/slices/index.php?site_id=%(site_id)d">%(nb_slices)d slice(s)</a></li>'%locals()
        else:
            description += '<li>No slice</li>'
        # close description
        description +='</ul>'

        # STYLE
#        if not site['peer_id']:
#            iconfile="google-local.png"
#        else:
#            iconfile="google-foreign.png"
#        iconurl="http://%(baseurl)s/misc/%(iconfile)s"%locals()
#        xyspec=""

        if not site['peer_id']:
            # local sites
            iconurl="root://icons/palette-3.png"
            xyspec="<x>0</x><y>0</y><w>32</w><h>32</h>"
        else:
            # remote
            iconurl="root://icons/palette-3.png"
            xyspec="<x>32</x><y>0</y><w>32</w><h>32</h>"
            
        iconspec="<href>%(iconurl)s</href>%(xyspec)s"%locals()

        template="""<Placemark>
<Style><IconStyle><Icon>%(iconspec)s</Icon></IconStyle></Style>
<name><![CDATA[%(name)s]]></name>
<description><![CDATA[%(description)s]]></description>
<Point> <coordinates>%(longitude)f,%(latitude)f,0</coordinates> </Point>
</Placemark>
"""
        self.write(template%locals())

        
#        print 'name',name
#        print 'description',description
#        print template
#        print template%locals()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        out=default_output
    elif len(sys.argv) == 2:
        out=sys.argv[1]
    else:
        print "Usage: %s [output]"%sys.argv[0]
        print "default output is %s"%default_output
        sys.exit(1)
    KmlMap(out).refresh()
