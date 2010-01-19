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

# Install configuration scripts
echo "* Installing configuration scripts"
pldistro=$1; shift
RPM_BUILD_ROOT=$1 ; shift
PYTHON_SITEARCH=`python -c 'from distutils.sysconfig import get_python_lib; print get_python_lib(1)'`
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}

echo "* Installing plc_config.py in " ${PYTHON_SITEARCH}
install -D -m 755 plc_config.py ${RPM_BUILD_ROOT}/${PYTHON_SITEARCH}/plc_config.py

echo "* Installing scripts in /usr/bin"
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
rsync -av --exclude .svn bin/ ${RPM_BUILD_ROOT}/usr/bin/
chmod 755 ${RPM_BUILD_ROOT}/usr/bin/*

# Install initscript 
echo "* Installing plc initscript"
install -D -m 755 plc.init ${RPM_BUILD_ROOT}/etc/init.d/plc

# Install initscripts
echo "* Installing plc.d initscripts"
find plc.d | cpio -p -d -u ${RPM_BUILD_ROOT}/etc/
chmod 755 ${RPM_BUILD_ROOT}/etc/plc.d/*

# Install db-config.d files
echo "* Installing db-config.d files"
mkdir -p ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
cp db-config.d/* ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
chmod 444 ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d/*

# Extra scripts (mostly for mail and dns) not installed by myplc by default.  Used in production
echo "* Installing scripts in /etc/support-scripts"
mkdir -p ${RPM_BUILD_ROOT}/etc/support-scripts
cp support-scripts/* ${RPM_BUILD_ROOT}/etc/support-scripts
chmod 444 ${RPM_BUILD_ROOT}/etc/support-scripts/*

# copy initscripts to etc/plc_sliceinitscripts
mkdir -p ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts
cp plc_sliceinitscripts/* ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts
chmod 444 ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts/*

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml ${RPM_BUILD_ROOT}/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd ${RPM_BUILD_ROOT}/etc/planetlab/plc_config.dtd

echo "* Installing bashrc convenience"
install -D -m 644 bashrc ${RPM_BUILD_ROOT}/usr/share/myplc/bashrc

# yumgroups.xml and yum repo : let noderepo handle that

exit 0
