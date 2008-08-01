#!/bin/bash
#
# Builds MyPLC in the current host environment
# This is for the so-called chroot installation mode, meaning that
# the resulting rpm will install a full chroot image in /plc/root
# that can be run through chroot /plc/root
# This chroot mode is to be opposed to the native mode (see build-native.sh)
# that can be used in the host's root context or within a vserver
#
# root.img (loopback image)
# root/ (mount point)
# data/ (various data files)
# data/etc/planetlab/ (configuration files)
# data/root (root's homedir)
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id$
#

. build.functions

# pldistro expected as $1 - defaults to planetlab
pldistro=$1 ; shift

# These directories are allowed to grow to unspecified size, so they
# are stored as symlinks to the /data partition. mkfedora and yum
# expect some of them to be real directories, however.
datadirs=(
/etc/planetlab
/root
/var/lib/pgsql
/var/www/html/alpina-logs
/var/www/html/boot
/var/www/html/download
/var/www/html/download-planetlab-i386
/var/www/html/files
/var/www/html/sites
/var/www/html/generated
/var/www/html/install-rpms
/var/www/html/xml
/tmp
/usr/tmp
/var/tmp
/var/log
)

pl_fixdirs root "${datadirs[@]}"

echo "* myplc: Installing base filesystem"
mkdir -p root data

pl_root_makedevs root
pkgsfile=$(pl_locateDistroFile ../build/ ${pldistro} myplc.pkgs)
pl_root_mkfedora root $pldistro $pkgsfile
pl_root_tune_image root

# Install configuration scripts
echo "* myplc: Installing configuration scripts"
install -D -m 755 plc_config.py root/tmp/plc_config.py
chroot root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config root/usr/bin/plc-config
install -D -m 755 plc-config-tty root/usr/bin/plc-config-tty
install -D -m 755 db-config root/usr/bin/db-config
install -D -m 755 dns-config root/usr/bin/dns-config
install -D -m 755 plc-map.py root/usr/bin/plc-map.py
install -D -m 755 plc-kml.py root/usr/bin/plc-kml.py
install -D -m 755 refresh-peer.py root/usr/bin/refresh-peer.py
install -D -m 755 clean-empty-dirs.py root/usr/bin/clean-empty-dirs.py
install -D -m 755 mtail.py root/usr/bin/mtail.py
install -D -m 755 check-ssl-peering.py root/usr/bin/check-ssl-peering.py
# Extra scripts (mostly for mail and dns) not installed by myplc by default.  Used in production
mkdir root/etc/support-scripts
cp support-scripts/* root/etc/support-scripts 
# copy initscripts to etc/plc_sliceinitscripts
mkdir root/etc/plc_sliceinitscripts
cp plc_sliceinitscripts/* root/etc/plc_sliceinitscripts

# Install initscripts
echo "* myplc: Installing initscripts"
find plc.d | cpio -p -d -u root/etc/
install -D -m 755 guest.init root/etc/init.d/plc
chroot root sh -c 'chkconfig --add plc; chkconfig plc on'

# fetch the release stamp from the build if any
# I could not come up with any more sensitive scheme 
if [ -f ../../../myplc-release ] ; then
  cp ../../../myplc-release myplc-release
else
  echo "Cannot find release information." > myplc-release
  date >> myplc-release
  echo "$HeadURL$" >> myplc-release
fi
# install it in /etc/myplc-release 
install -m 444 myplc-release root/etc/myplc-release

### Thierry Parmentelat - april 16 2007
# fix the yum.conf as produced by mkfedora
# so we can use the build's fc4 mirror for various installs/upgrades
# within the chroot jail
# yum_conf_to_build_host is defined in build.functions
yum_conf_to_build_host ../build > root/etc/yum.conf

### Thierry Parmentelat - may 8 2008
# no doc built in this old-fashioned packaging anymore
# use myplc-docs instead

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd data/etc/planetlab/plc_config.dtd

# handle root's homedir and tweak root prompt
echo "* myplc: root's homedir and prompt"
roothome=data/root
mkdir -p $roothome
cat << EOF > $roothome/.profile
export PS1="<plc> \$PS1"
EOF
chmod 644 $roothome/.profile

# Move "data" directories out of the installation
echo "* myplc: Moving data directories out of the installation"
pl_move_dirs root data /data "${datadirs[@]}"

# Fix permissions on tmp directories
pl_fixtmp_permissions data

# Remove generated bootmanager script
rm -f data/var/www/html/boot/bootmanager.sh

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
nodefamily=${pldistro}-${pl_DISTRO_ARCH}
install -D -m 644 $pl_DISTRO_YUMGROUPS \
    data/var/www/html/install-rpms/$nodefamily/yumgroups.xml
# temporary - so that node update still work until yum.conf.php gets fixed
( cd data/var/www/html/install-rpms ; ln -s $nodefamily planetlab)

# Make image out of directory
echo "* myplc: Building loopback image"
pl_make_image root root.img 100000000

exit 0
