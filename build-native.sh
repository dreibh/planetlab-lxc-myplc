#!/bin/bash
#
# Builds MyPLC, either inside the MyPLC development environment in
# devel/root (if PLC_DEVEL_BOOTSTRAP is true), or in the current host
# environment (may be itself a MyPLC development environment or a
# Fedora environment with the appropriate development packages
# installed).
#
# Marc E. Fiuczynski <mef@cs.princeton.edu>
# Copyright (C) 2007 The Trustees of Princeton University
#
# $Id$
#

. build.functions

# XXX .spec file needs to have the appropriate set of requires statements

# Install configuration scripts
echo "* myplc-native: Installing configuration scripts"
tmpdir=$1
mkdir -p ${tmpdir}
rm -rf ${tmpdir}
mkdir -p ${tmpdir}
echo "* myplc-native: installing plc_config.py in /usr/share/myplc"
install -D -m 755 plc_config.py ${tmpdir}/usr/share/myplc/plc_config.py
install -D -m 755 plc-config ${tmpdir}/usr/bin/plc-config
install -D -m 755 plc-config-tty ${tmpdir}/usr/bin/plc-config-tty
install -D -m 755 db-config ${tmpdir}/usr/bin/db-config
install -D -m 755 dns-config ${tmpdir}/usr/bin/dns-config
install -D -m 755 plc-map.py ${tmpdir}/usr/bin/plc-map.py
install -D -m 755 clean-empty-dirs.py ${tmpdir}/usr/bin/clean-empty-dirs.py
install -D -m 755 mtail.py ${tmpdir}/usr/bin/mtail.py
install -D -m 755 check-ssl-peering.py ${tmpdir}/usr/bin/check-ssl-peering.py
# Extra scripts (mostly for mail and dns) not installed by myplc by default.  Used in production
mkdir -p ${tmpdir}/etc/support-scripts
cp support-scripts/* ${tmpdir}/etc/support-scripts
# copy initscripts to etc/plc_sliceinitscripts
mkdir -p ${tmpdir}/etc/plc_sliceinitscripts
cp plc_sliceinitscripts/* ${tmpdir}/etc/plc_sliceinitscripts

# Install initscripts
echo "* myplc-native: Installing initscripts"
find plc.d | cpio -p -d -u ${tmpdir}/etc/
install -D -m 755 guest.init ${tmpdir}/etc/init.d/plc


# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml ${tmpdir}/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd ${tmpdir}/etc/planetlab/plc_config.dtd

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
install -D -m 644 $pl_DISTRO_YUMGROUPS \
    ${tmpdir}/var/www/html/install-rpms/planetlab/yumgroups.xml

exit 0
