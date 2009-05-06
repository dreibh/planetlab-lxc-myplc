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
pldistro=$1; shift
RPM_BUILD_ROOT=$1 ; shift
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}
echo "* myplc-native: installing plc_config.py in /usr/share/myplc"
install -D -m 755 plc_config.py ${RPM_BUILD_ROOT}/usr/share/myplc/plc_config.py
install -D -m 644 bashrc ${RPM_BUILD_ROOT}/usr/share/myplc/bashrc
echo "* myplc-native: installing scripts in /usr/bin"
install -D -m 755 plc-config ${RPM_BUILD_ROOT}/usr/bin/plc-config
install -D -m 755 plc-config-tty ${RPM_BUILD_ROOT}/usr/bin/plc-config-tty
install -D -m 755 db-config ${RPM_BUILD_ROOT}/usr/bin/db-config
install -D -m 755 dns-config ${RPM_BUILD_ROOT}/usr/bin/dns-config
install -D -m 755 plc-map.py ${RPM_BUILD_ROOT}/usr/bin/plc-map.py
install -D -m 755 plc-kml.py ${RPM_BUILD_ROOT}/usr/bin/plc-kml.py
install -D -m 755 refresh-peer.py ${RPM_BUILD_ROOT}/usr/bin/refresh-peer.py
install -D -m 755 clean-empty-dirs.py ${RPM_BUILD_ROOT}/usr/bin/clean-empty-dirs.py
install -D -m 755 mtail.py ${RPM_BUILD_ROOT}/usr/bin/mtail.py
install -D -m 755 check-ssl-peering.py ${RPM_BUILD_ROOT}/usr/bin/check-ssl-peering.py
# Extra scripts (mostly for mail and dns) not installed by myplc by default.  Used in production
echo "* myplc-native: installing scripts in /etc/support-scripts"
mkdir -p ${RPM_BUILD_ROOT}/etc/support-scripts
cp support-scripts/* ${RPM_BUILD_ROOT}/etc/support-scripts
# copy initscripts to etc/plc_sliceinitscripts
mkdir -p ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts
cp plc_sliceinitscripts/* ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts

# Install initscripts
echo "* myplc-native: Installing initscripts"
find plc.d | cpio -p -d -u ${RPM_BUILD_ROOT}/etc/
install -D -m 755 plc.init ${RPM_BUILD_ROOT}/etc/init.d/plc

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml ${RPM_BUILD_ROOT}/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd ${RPM_BUILD_ROOT}/etc/planetlab/plc_config.dtd

# yumgroups.xml and yum repo : let noderepo handle that

exit 0
