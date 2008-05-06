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
tmpdir=$1 ; shift
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

# fetch the release stamp from the build if any
if [ -f ../../../myplc-release ] ; then
  cp ../../../myplc-release myplc-release
else
  echo "Cannot find release information." > myplc-release
  date >> myplc-release
  echo "$HeadURL$" >> myplc-release
fi
# install it in /etc/myplc-release 
install -m 444 myplc-release ${tmpdir}/etc/myplc-release

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml ${tmpdir}/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd ${tmpdir}/etc/planetlab/plc_config.dtd

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
nodefamily=${pldistro}-${pl_DISTRO_ARCH}
install -D -m 644 $pl_DISTRO_YUMGROUPS \
    ${tmpdir}/var/www/html/install-rpms/$nodefamily/yumgroups.xml
# temporary - so that node update still work until yum.conf.php gets fixed
( cd ${tmpdir}/var/www/html/install-rpms ; ln -s $nodefamily planetlab)

# building myplc doc
# beware that making the pdf file somehow overwrites the html
make -C doc myplc.pdf 
rm -f doc/myplc.html
make -C doc myplc.html 

# install doc
for doc in myplc.html myplc.pdf ; do
    install -D -m 644 doc/$doc ${tmpdir}/var/www/html/planetlab/doc/$doc
done

# create drupal pages
# at this stage we dont have access to the PLCAPI html
# so, let's just package build.common and do the job in the post-install script
install -m 644 ./docbook2drupal.sh ${tmpdir}/usr/share/myplc/docbook2drupal.sh

exit 0
