#!/usr/bin/python
#
# Write out sites.xml
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: gen-sites-xml.py,v 1.8 2007/09/14 20:08:28 tmack Exp $
#

import os, sys
import getopt
import time
from xml.sax.saxutils import escape, quoteattr, XMLGenerator

PID_FILE= "/var/run/all_planetlab_xml.pid"

#
# Web server document root
#
DOCROOT = '/var/www/html/xml'

#
# DTD and version number for site information
#
ENCODING= "utf-8"
SITE_VERSION="0.4"

# Debug
dryrun = False

# Parse options
def usage():
    print "Usage: %s [OPTION]..." % sys.argv[0]
    print "Options:"
    print "     -n, --dryrun            Dry run, do not write files (default: %s)" % dryrun
    print "     -d, --docroot=DIR       Document root (default: %s)" % DOCROOT
    print "     -h, --help              This message"
    sys.exit(1)

# Get options
try:
    (opts, argv) = getopt.getopt(sys.argv[1:], "nd:h", ["dryrun", "docroot=", "help"])
except getopt.GetoptError, err:
    print "Error: " + err.msg
    usage()

for (opt, optval) in opts:
    if opt == "-n" or opt == "--dryrun":
        dryrun = True
    elif opt == "-d" or opt == "--docroot":
        DOCROOT = optval
    else:
        usage()

# Write out lock file
if not dryrun:
    if os.access(PID_FILE, os.R_OK):
        pid= file(PID_FILE).readline().strip()
        if pid <> "":
            if os.system("/bin/kill -0 %s > /dev/null 2>&1" % pid) == 0:
                sys.exit(0)

    # write out our process id
    pidfile= file( PID_FILE, 'w' )
    pidfile.write( "%d\n" % os.getpid() )
    pidfile.close()

# Load shell with default configuration
sys.path.append('/usr/share/plc_api')
from PLC.Shell import Shell
plc = Shell(globals())

#
# Get information from API
#

begin()
GetNodes(None, ['node_id', 'model', 'boot_state', 'hostname', 'version', 'ssh_rsa_key', 'interface_ids', 'slice_ids_whitelist'])
GetInterfaces({'is_primary': True}, ['interface_id', 'node_id', 'ip', 'mac', 'bwlimit'])
GetSites(None, ['name', 'latitude', 'longitude', 'url', 'site_id', 'login_base', 'abbreviated_name', 'node_ids'])
GetNodeGroups(['Alpha', 'Beta', 'Rollout', 'Production'], ['groupname', 'node_ids'])
(nodes, nodenetworks, sites, groups) = commit()

# remove whitelisted nodes
remove_whitelisted = lambda node: not node['slice_ids_whitelist']
nodes = filter(remove_whitelisted, nodes)

nodes = dict([(node['node_id'], node) for node in nodes])

for nodenetwork in nodenetworks:
    if nodes.has_key(nodenetwork['node_id']):
        node = nodes[nodenetwork['node_id']]
        for key, value in nodenetwork.iteritems():
            node[key] = value

group_node_ids = dict([(group['groupname'], group['node_ids']) for group in groups])

class PrettyXMLGenerator(XMLGenerator):
    """
    Adds indentation to the beginning and newlines to the end of
    opening and closing tags.
    """

    def __init__(self, out = sys.stdout, encoding = "utf-8", indent = "", addindent = "", newl = ""):
        XMLGenerator.__init__(self, out, encoding)
        # XMLGenerator does not export _write()
        self.write = self.ignorableWhitespace
        self.indents = [indent]
        self.addindent = addindent
        self.newl = newl

    def startDocument(self):
        XMLGenerator.startDocument(self)

    def startElement(self, name, attrs, indent = True, newl = True):
        if indent:
            self.ignorableWhitespace("".join(self.indents))
        self.indents.append(self.addindent)

        XMLGenerator.startElement(self, name, attrs)

        if newl:
            self.ignorableWhitespace(self.newl)

    def characters(self, content):
        # " to &quot;
        # ' to &apos;
        self.write(escape(content, {
            '"': '&quot;',
            "'": '&apos;',
            }))

    def endElement(self, name, indent = True, newl = True):
        self.indents.pop()
        if indent:
            self.ignorableWhitespace("".join(self.indents))

        XMLGenerator.endElement(self, name)

        if newl:
            self.ignorableWhitespace(self.newl)

    def simpleElement(self, name, attrs = {}, indent = True, newl = True):
        if indent:
            self.ignorableWhitespace("".join(self.indents))

        self.write('<' + name)
        for (name, value) in attrs.items():
            self.write(' %s=%s' % (name, quoteattr(value.strip())))
        self.write('/>')

        if newl:
            self.ignorableWhitespace(self.newl)

#
# Write out sites.xml
#

if dryrun:
    sites_xml = sys.stdout
else:
    sites_xml = open(DOCROOT + "/sites.xml", mode = "w")

xml = PrettyXMLGenerator(out = sites_xml, encoding = ENCODING, indent = "", addindent = "  ", newl = "\n")
xml.startDocument()

# Write embedded DTD verbatim
xml.ignorableWhitespace("""
<!DOCTYPE PLANETLAB_SITES [
  <!ELEMENT PLANETLAB_SITES (SITE)*>
  <!ATTLIST PLANETLAB_SITES VERSION CDATA #REQUIRED
                            TIME    CDATA #REQUIRED>

  <!ELEMENT SITE (HOST)*>
  <!ATTLIST SITE NAME            CDATA #REQUIRED
                 LATITUDE        CDATA #REQUIRED
                 LONGITUDE       CDATA #REQUIRED
                 URL             CDATA #REQUIRED
                 SITE_ID         CDATA #REQUIRED
                 LOGIN_BASE      CDATA #REQUIRED
                 FULL_SITE_NAME  CDATA #REQUIRED
                 SHORT_SITE_NAME CDATA #REQUIRED
  >

  <!ELEMENT HOST EMPTY>
  <!ATTLIST HOST NAME         CDATA #REQUIRED
                 IP           CDATA #REQUIRED
                 MODEL        CDATA #REQUIRED
                 MAC          CDATA #IMPLIED
                 BOOTCD       (y|n) "n"
                 VERSION      CDATA #REQUIRED
                 NODE_ID      CDATA #REQUIRED
                 BOOT_VERSION CDATA ""
                 STATUS       CDATA ""
                 BOOT_STATE   CDATA #REQUIRED
                 RSA_KEY      CDATA ""
                 BWLIMIT      CDATA ""
  >
]>
""")

def format_tc_rate(rate):
    """
    Formats a bits/second rate into a tc rate string
    """

    if rate >= 1000000000 and (rate % 1000000000) == 0:
        return "%.0fgbit" % (rate / 1000000000.)
    elif rate >= 1000000 and (rate % 1000000) == 0:
        return "%.0fmbit" % (rate / 1000000.)
    elif rate >= 1000:
        return "%.0fkbit" % (rate / 1000.)
    else:
        return "%.0fbit" % rate

# <PLANETLAB_SITES VERSION="major.minor" TIME="seconds_since_epoch">
xml.startElement('PLANETLAB_SITES', {'VERSION': SITE_VERSION,
                                     'TIME': str(int(time.time()))})

for site in sites:
    # <SITE ...>
    attrs = {}
    for attr in ['name', 'latitude', 'longitude', 'url', 'site_id', 'login_base']:
        attrs[attr.upper()] = unicode(site[attr])
    attrs['FULL_SITE_NAME'] = unicode(site['name'])
    attrs['SHORT_SITE_NAME'] = unicode(site['abbreviated_name'])
    xml.startElement('SITE', attrs)

    for node_id in site['node_ids']:
        if nodes.has_key(node_id):
            node = nodes[node_id]

            # <HOST ...>
            attrs = {}
            attrs['NAME'] = unicode(node['hostname'])
            attrs['VERSION'] = "2.0"
            for attr in ['model', 'node_id', 'boot_state']:
                attrs[attr.upper()] = unicode(node[attr]).strip()

            # If the node is in Alpha, Beta, or Rollout, otherwise Production
            for group in ['Alpha', 'Beta', 'Rollout', 'Production']:
                if group_node_ids.has_key(group) and \
                   node_id in group_node_ids[group]:
                    break
            attrs['STATUS'] = group

            if node['version']:
                attrs['BOOT_VERSION'] = unicode(node['version'].splitlines()[0])
            if node['ssh_rsa_key']:
                attrs['RSA_KEY'] = unicode(node['ssh_rsa_key'].splitlines()[0])

            if node.has_key('ip') and node['ip']:
                attrs['IP'] = unicode(node['ip'])
            if node.has_key('mac') and node['mac']:
                attrs['MAC'] = unicode(node['mac'])
            if node.has_key('bwlimit') and node['bwlimit']:
                attrs['BWLIMIT'] = unicode(format_tc_rate(node['bwlimit']))

            xml.simpleElement('HOST', attrs)

    # </SITE>
    xml.endElement('SITE')

xml.endElement('PLANETLAB_SITES')

if not dryrun:
    # remove the PID file
    os.unlink( PID_FILE )
