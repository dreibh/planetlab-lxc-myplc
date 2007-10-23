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
# $Id: build-native.sh,v 1.1.2.5 2007/08/31 17:46:11 mef Exp $
#

. build.functions

# XXX .spec file needs to have the appropriate set of requires statements

# Install configuration scripts
echo "* myplc-native: Installing configuration scripts"
tmpdir=$1
mkdir -p ${tmpdir}
rm -rf ${tmpdir}
mkdir -p ${tmpdir}
install -D -m 755 plc-config ${tmpdir}/usr/bin/plc-config
install -D -m 755 plc-config-tty ${tmpdir}/usr/bin/plc-config-tty
install -D -m 755 db-config ${tmpdir}/usr/bin/db-config
install -D -m 755 dns-config ${tmpdir}/usr/bin/dns-config
echo "* myplc-native: skipping build/install of plc_config.py"

# XXX needs to be done by %pre script in .spec file
# install -D -m 755 plc_config.py /tmp/plc_config.py
# sh -c 'cd ${tmpdir}; python plc_config.py build; python plc_config.py install'
# XXX needs to be done by %pre script in .spec file
# sh -c 'chkconfig --add plc; chkconfig plc on'



# Install initscripts
echo "* myplc-native: Installing initscripts"
find plc.d | cpio -p -d -u ${tmpdir}/etc/
install -D -m 755 guest.init ${tmpdir}/etc/init.d/plc


# Install web scripts
#echo "* myplc: Installing web scripts"
#mkdir -p ${tmpdir}/usr/bin
#install -m 755 \
#    $srcdir/plc/scripts/gen-sites-xml.py \
#    $srcdir/plc/scripts/gen-slices-xml-05.py \
#    $srcdir/plc/scripts/gen-static-content.py \
#    ${tmpdir}/usr/bin/

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 plc_config.xml ${tmpdir}/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd ${tmpdir}/etc/planetlab/plc_config.dtd

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
install -D -m 644 $pl_YUMGROUPSXML \
    ${tmpdir}/var/www/html/install-rpms/planetlab/yumgroups.xml

exit 0
